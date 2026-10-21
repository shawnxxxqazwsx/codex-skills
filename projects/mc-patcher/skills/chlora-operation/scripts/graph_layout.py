#!/usr/bin/env python3
"""Finite headless Graph layout planning and independently verified MCP execution.

collect/execute use one pinned persistent connection. plan is offline. No session
switch, automatic recovery, write retry, topology rewrite, or visual acceptance.
"""
import argparse
from collections import Counter
import copy
import json
import math
import os
import re
from pathlib import Path
import stat
import struct
import time

CATEGORIES = ('nodes', 'groups', 'groupPorts', 'containers', 'comments', 'pins', 'nodeSizes')
LIMITS = {name: 256 for name in CATEGORIES}
LIMITS.update(groups=128, containers=128)
BIND = ('instanceId', 'bindingGeneration', 'graphTopology', 'graphLifetime')


def bound(state):
    result = {k: state.get('activeInstanceId') if k == 'instanceId' and
              'activeInstanceId' in state else state[k] for k in BIND}
    for key in ('graphTopology', 'graphLifetime'):
        if not isinstance(result[key], str) or re.fullmatch(r'-?[0-9]{1,20}', result[key]) is None:
            raise ValueError('Graph identity tokens must be decimal strings')
    return result


def number(value, low=-20000, high=20000):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('finite numeric coordinate/size required')
    if not low <= value <= high:
        raise ValueError('coordinate/size outside supported range')
    return value


def geometry_document(value):
    """Accept a complete merged inventory, never silently accept a first page."""
    if 'result' in value and isinstance(value['result'], dict):
        value = value['result']
    geom = value.get('geometry', value)
    if geom.get('nativePerWorldCss') != 3 or geom.get('units', 'native') != 'native':
        raise ValueError('geometry must use native units, 3 per world CSS pixel')
    if geom.get('coverage', {}).get('complete') is not True:
        raise ValueError('incomplete geometry; collect every revision-consistent page first')
    page = geom.get('page')
    if page and (page.get('nextCursor') is not None or page.get('offset') != 0
                 or page.get('returnedItems') != page.get('totalItems')):
        raise ValueError('incomplete geometry page')
    items = geom.get('items')
    if items is None:
        # Complete legacy geometry remains readable; ownership metadata is still
        # mandatory when a node is selected for automatic placement.
        items = [item for name in ('nodes', 'groups', 'comments', 'cablePins')
                 for item in geom.get(name, [])]
    if not isinstance(items, list) or len(items) > 4096:
        raise ValueError('invalid/oversized inventory')
    keys = [item.get('key') for item in items]
    if any(not isinstance(key, str) or not key for key in keys) or len(set(keys)) != len(keys):
        raise ValueError('missing or duplicate object identity')
    return geom, {item['key']: item for item in items}


def node_item(items, key, loose=False):
    item = items.get('node:' + str(key))
    if not item or item.get('kind') != 'node' or item.get('nodeKey') != key:
        raise ValueError('unknown node: ' + str(key))
    if item.get('visible') is not True or item.get('movable') is not True \
            or item.get('placement', {}).get('kind') != 'node':
        raise ValueError('node must be visible and independently movable; use its placement owner: ' + str(key))
    if loose and item.get('parentGroupId', 0):
        raise ValueError('automatic placement requires loose nodes; use explicit container layout')
    b, p = item.get('bounds'), item.get('position')
    if not isinstance(b, dict) or not isinstance(p, dict):
        raise ValueError('node anchor and envelope required')
    for field in ('x', 'y', 'w', 'h'):
        number(b.get(field), -math.inf if field in ('x', 'y') else 0, math.inf)
    if b['w'] <= 0 or b['h'] <= 0:
        raise ValueError('positive envelope required')
    for field in ('x', 'y'):
        number(p.get(field), -math.inf, math.inf)
    return item


def keys_checked(items, keys, loose=True):
    if not isinstance(keys, list) or not keys or len(keys) > 256 or len(set(keys)) != len(keys):
        raise ValueError('nodeKeys must be a nonempty unique list of at most 256 nodes')
    return [node_item(items, key, loose) for key in keys]


def row_rows(items, keys, origin=(0, 0), gap=240):
    selected = keys_checked(items, keys)
    if len(origin) != 2:
        raise ValueError('origin must contain native x and y')
    x, y = (number(v) for v in origin)
    number(gap, 0)
    out = []
    for item in selected:
        b, p = item['bounds'], item['position']
        # x/y describe envelope alignment; native move uses the saved anchor.
        ax, ay = x + p['x'] - b['x'], y + p['y'] - b['y']
        out.append({'nodeKey': item['nodeKey'], 'x': number(ax), 'y': number(ay)})
        x += b['w'] + gap
    return out


def ancestors(items, group_id):
    seen = set()
    while group_id:
        if group_id in seen:
            raise ValueError('cyclic Group ownership')
        seen.add(group_id)
        item = items.get('group:' + str(group_id))
        if not item:
            raise ValueError('missing parent Group in inventory')
        yield group_id
        group_id = item.get('parentGroupId', 0)


def explicit_layout(items, raw):
    if not isinstance(raw, dict) or set(raw) - set(CATEGORIES):
        raise ValueError('unknown layout category')
    shapes = {
        'nodes': ('nodeKey', {'nodeKey', 'x', 'y'}, {'nodeKey', 'x', 'y'}),
        'nodeSizes': ('nodeKey', {'nodeKey', 'w', 'h'}, {'nodeKey', 'w', 'h'}),
        'groups': ('groupId', {'groupId', 'x', 'y', 'w', 'h'}, {'groupId', 'x', 'y', 'w', 'h'}),
        'containers': ('groupId', {'groupId', 'x', 'y'}, {'groupId', 'x', 'y'}),
        'groupPorts': ('nodeKey', {'groupId', 'nodeKey', 'side', 'position'}, {'groupId', 'nodeKey', 'side', 'position'}),
        'comments': ('commentId', {'commentId', 'x', 'y', 'w', 'h'}, {'commentId', 'x', 'y'}),
        'pins': ('pinId', {'pinId', 'x', 'y'}, {'pinId', 'x', 'y'})}
    result, targets = {}, []
    for category, rows in raw.items():
        if not isinstance(rows, list) or len(rows) > LIMITS[category]:
            raise ValueError('layout entry limit exceeded: ' + category)
        identity, allowed, required = shapes[category]
        seen = set()
        for row in rows:
            if not isinstance(row, dict) or set(row) - allowed or required - set(row):
                raise ValueError('invalid layout row: ' + category)
            key = row[identity]
            if key in seen:
                raise ValueError('duplicate layout identity: ' + category)
            seen.add(key)
            if category in ('nodes', 'nodeSizes'):
                item = node_item(items, key)
                if category == 'nodeSizes' and item.get('type') != 'plugin':
                    raise ValueError('nodeSizes requires an independently resizable plugin node')
            elif category == 'groupPorts':
                item = items.get('node:' + str(key))
                if not item or item.get('placement', {}).get('kind') != 'group-port' \
                        or item['placement'].get('groupId') != row['groupId']:
                    raise ValueError('invalid Group boundary port')
                if row['side'] not in ('left', 'right'):
                    raise ValueError('invalid Group port side')
                number(row['position'], 0, 1)
                group = items.get('group:' + str(row['groupId']), {})
                if group.get('type') == 'stack' and row['side'] != item['placement'].get('side'):
                    raise ValueError('Stack port side is fixed')
            else:
                if type(key) is not int or key <= 0:
                    raise ValueError('positive object ID required')
                prefix = 'group' if category in ('groups', 'containers') else 'comment' if category == 'comments' else 'cable-pin'
                item = items.get(prefix + ':' + str(key))
                if not item or item.get('visible') is not True:
                    raise ValueError('unknown/invisible object: ' + prefix)
            if category == 'containers':
                frame, anchor = item.get('frameSize'), item.get('position')
                if item.get('boundsSource') != 'stored-frame' or not isinstance(frame, dict) or not isinstance(anchor, dict):
                    raise ValueError('container translation requires a valid saved frame')
                for axis in ('x', 'y'):
                    number(anchor.get(axis), -math.inf, math.inf)
                for axis in ('w', 'h'):
                    number(frame.get(axis), 1e-12, math.inf)
            if category == 'comments' and ('w' in row) != ('h' in row):
                raise ValueError('Comment w/h must be supplied together')
            for field in ('x', 'y'):
                if field in row:
                    number(row[field])
            for field in ('w', 'h'):
                if field in row:
                    minimum = (72 if field == 'w' else 40) if category == 'nodeSizes' \
                        else (72 if field == 'w' else 48) if category == 'comments' else 1e-12
                    number(row[field], minimum, 40000 if category == 'groups' else 20000)
            if category == 'groups' and item.get('type') == 'stack':
                if row['w'] != item['bounds']['w'] or row['h'] != item['bounds']['h']:
                    raise ValueError('Stack frame dimensions follow lane configuration')
            targets.append((category, item))
        if rows:
            result[category] = copy.deepcopy(rows)
    if not result:
        raise ValueError('nonempty layout required')
    containers = {row['groupId'] for row in result.get('containers', [])}
    if containers & {row['groupId'] for row in result.get('groups', [])}:
        raise ValueError('container translation conflicts with its frame edit')
    for category, item in targets:
        if category == 'groupPorts':
            continue
        own = item.get('groupId') if item.get('kind') == 'group' else None
        parent_chain = set(ancestors(items, item.get('parentGroupId', 0)))
        if category not in ('containers', 'nodeSizes') and own in containers or (category != 'nodeSizes' and parent_chain & containers):
            raise ValueError('container translation conflicts with explicit descendant edit')
        if item.get('placement', {}).get('kind') == 'attached-node':
            raise ValueError('attached objects follow their owner')
    return result


def semantic_routes(state):
    """Exact route multiset and semantic node controls, including hidden routes."""
    rows = state.get('graphNodes', state.get('nodes', []))
    indices = {n.get('index'): n['nodeKey'] for n in rows if 'index' in n}
    keys = [n['nodeKey'] for n in rows]
    if len(keys) != len(set(keys)):
        raise ValueError('duplicate semantic node identity')
    fields = ('mainIn', 'mainOut', 'sidechainIn', 'isInput', 'isOutput', 'isRouter', 'isBundle',
              'isSum', 'isFanout', 'snakeWrapped', 'snakeInputCount', 'snakeOutputCount',
              'bundleMode', 'bundleLaneCount', 'routerRoutes', 'routerChannels', 'routerDirection',
              'routerAttached', 'routerIndex', 'hiddenRoutingNode', 'stackId', 'stackRow', 'groupFanout', 'groupId')
    identities = sorted((n['nodeKey'], json.dumps({k: n[k] for k in fields if k in n}, sort_keys=True)) for n in rows)
    edges = []
    for w in state.get('graphWires', state.get('wires', [])):
        src = w.get('sourceNodeKey', indices.get(w.get('from')))
        dst = w.get('destinationNodeKey', indices.get(w.get('to')))
        if src not in keys or dst not in keys:
            raise ValueError('unresolved semantic route endpoint')
        edge = (src, dst, w.get('fromCh', w.get('sourceChannel', 0)),
                w.get('toCh', w.get('destinationChannel', 0)), w.get('fromRole', w.get('sourceRole', 'main')),
                w.get('toRole', w.get('destinationRole', 'main')), bool(w.get('isBundle')),
                w.get('bundleWidth', 1) if w.get('isBundle') else 1,
                w.get('snakeBranch', w.get('sourceBranch', 0)),
                w.get('snakeInputBranch', w.get('destinationBranch', 0)), bool(w.get('hiddenRoutingWire')))
        edges.append(json.dumps(edge))
    return {'nodes': identities, 'routes': sorted(Counter(edges).items())}


def make_plan(inventory, spec, state=None):
    _, items = geometry_document(inventory)
    state = state if state is not None else inventory.get('semanticState')
    mode = spec.get('mode', 'explicit')
    if mode == 'explicit':
        proposal = spec.get('layout', {})
    elif mode == 'row':
        proposal = {'nodes': row_rows(items, spec['nodeKeys'], spec.get('origin', (0, 0)), spec.get('gap', 240))}
    elif mode == 'parallel':
        lanes = spec.get('lanes', [])
        if not isinstance(lanes, list) or not lanes:
            raise ValueError('parallel layout needs explicit nonempty lanes')
        flat = [key for lane in lanes for key in lane]
        keys_checked(items, flat)
        x, y = spec.get('origin', (0, 0))
        number(x); number(y)
        row_gap = number(spec.get('rowGap', 240), 0)
        proposal = {'nodes': []}
        for lane in lanes:
            selected = keys_checked(items, lane)
            proposal['nodes'].extend(row_rows(items, lane, (x, y), spec.get('gap', 240)))
            y += max(item['bounds']['h'] for item in selected) + row_gap
    elif mode == 'topology':
        if state is None:
            raise ValueError('topology layout requires a complete semantic state')
        selected = keys_checked(items, spec['nodeKeys'])
        keys = [item['nodeKey'] for item in selected]
        incoming = {key: set() for key in keys}
        outgoing = {key: set() for key in keys}
        index = {n.get('index'): n['nodeKey'] for n in state.get('graphNodes', state.get('nodes', []))}
        for wire in state.get('graphWires', state.get('wires', [])):
            a = wire.get('sourceNodeKey', index.get(wire.get('from')))
            b = wire.get('destinationNodeKey', index.get(wire.get('to')))
            if a in incoming and b in incoming:
                if wire.get('hiddenRoutingWire') or wire.get('fromRole', 'main') != 'main' \
                        or wire.get('toRole', 'main') != 'main':
                    raise ValueError('automatic topology supports visible MAIN DAG only; use explicit layout')
                incoming[b].add(a); outgoing[a].add(b)
        pending = {key: set(value) for key, value in incoming.items()}
        ready = sorted(key for key in keys if not pending[key])
        level, order = {key: 0 for key in ready}, []
        while ready:
            key = ready.pop(0); order.append(key)
            for dst in sorted(outgoing[key]):
                level[dst] = max(level.get(dst, 0), level[key] + 1)
                pending[dst].discard(key)
                if not pending[dst] and dst not in order and dst not in ready:
                    ready.append(dst); ready.sort()
        if len(order) != len(keys):
            raise ValueError('cyclic topology unsupported; use explicit feedback layout')
        ox, oy = spec.get('origin', (0, 0))
        number(ox); number(oy)
        gap, row_gap = number(spec.get('gap', 240), 0), number(spec.get('rowGap', 240), 0)
        proposal = {'nodes': []}; x = ox
        for depth in range(max(level.values()) + 1):
            layer = [key for key in order if level[key] == depth]
            y = oy
            for key in layer:
                item = items['node:' + key]
                proposal['nodes'].extend(row_rows(items, [key], (x, y), gap))
                y += item['bounds']['h'] + row_gap
            x += max(items['node:' + key]['bounds']['w'] for key in layer) + gap
    else:
        raise ValueError('unsupported finite layout mode: ' + str(mode))
    proposal = explicit_layout(items, proposal)
    result = {'version': 1, 'layout': proposal, 'planner': mode, 'units': 'native', 'nodeSizeUnits': 'world-css'}
    if 'binding' in inventory:
        result['expectedBinding'] = inventory['binding']
    if 'layoutRevision' in inventory:
        result['expectedLayoutRevision'] = inventory['layoutRevision']
    if state is not None:
        result['expectedSemanticRoutes'] = semantic_routes(state)
    return result


def unwrap(value):
    while isinstance(value, dict) and isinstance(value.get('mcpResult'), dict):
        value = value['mcpResult']
    return value


def operation(client, tool, args, timeout=120, progress=None):
    r = client.tool(tool, args)
    detail = unwrap(r)
    op = r.get('operationId') or detail.get('operationId')
    if not op:
        return detail
    if progress is not None:
        progress['operationId'] = op
    deadline = time.monotonic() + timeout
    while True:
        terminal = client.tool('chlora_get_operation', {'operationId': op})
        status = terminal.get('status')
        if status in ('failed', 'cancelled'):
            raise RuntimeError('operation stopped: ' + json.dumps(terminal))
        if status == 'succeeded':
            return unwrap(terminal.get('result', terminal))
        if time.monotonic() >= deadline:
            raise TimeoutError('operation outcome unknown; never replay a write: ' + str(op))
        time.sleep(.2)


def collect(client, state=None, timeout=120):
    """Byte-limited compact nodes pages, strict revision/binding/count coverage."""
    state = state or client.tool('chlora_get_state', {})
    if state.get('mode') != 'graph' or state.get('pendingPluginLoads', 0):
        raise ValueError('active Graph required with no pending loads')
    binding = bound(state)
    merged, revision, total, offset, cursor = [], None, None, 0, None
    metadata = None
    seen = set()
    for _ in range(4097):
        args = {**binding, 'detail': 'nodes', 'representation': 'compact',
                'includePorts': False, 'pageSize': 128}
        if cursor:
            args['cursor'] = cursor
        value = operation(client, 'chlora_graph_get_layout_geometry', args, timeout)
        geom = value.get('geometry', {})
        if geom.get('nativePerWorldCss') != 3 or geom.get('portsIncluded') is not False:
            raise ValueError('compact inventory format unsupported')
        if geom.get('representation', 'compact') != 'compact':
            raise ValueError('inventory representation changed')
        if 'binding' in value and value['binding'] != binding:
            raise ValueError('inventory binding changed')
        current_revision = value.get('layoutRevision')
        page = geom.get('page', {})
        if not isinstance(current_revision, str) or not current_revision:
            raise ValueError('inventory revision required')
        if revision is None:
            revision, total, metadata = current_revision, page.get('totalItems'), copy.deepcopy(geom)
            if type(total) is not int or not 0 <= total <= 4096:
                raise ValueError('invalid inventory total')
        if current_revision != revision or page.get('totalItems') != total or page.get('offset') != offset:
            raise ValueError('inventory revision/count/offset changed; recollect explicitly')
        rows = geom.get('items')
        if not isinstance(rows, list) or len(rows) != page.get('returnedItems') or offset + len(rows) > total:
            raise ValueError('invalid inventory page count')
        for item in rows:
            key = item.get('key')
            if not isinstance(key, str) or not key or key in seen:
                raise ValueError('duplicate/missing inventory identity')
            seen.add(key); merged.append(item)
        offset += len(rows)
        next_cursor = page.get('nextCursor')
        if next_cursor is None:
            if offset != total:
                raise ValueError('inventory terminated before complete coverage')
            break
        if not rows or not isinstance(next_cursor, str) or not next_cursor or next_cursor == cursor:
            raise ValueError('nonprogressing inventory cursor')
        cursor = next_cursor
    else:
        raise ValueError('inventory page budget exceeded')
    final_state = client.tool('chlora_graph_get_summary', {})
    if bound(final_state) != binding:
        raise ValueError('Graph binding changed during inventory collection')
    metadata.update(items=merged, page={'offset': 0, 'returnedItems': total, 'totalItems': total, 'nextCursor': None})
    metadata.setdefault('coverage', {})['complete'] = True
    result = {'binding': binding, 'layoutRevision': revision, 'geometry': metadata}
    geometry_document(result)
    return result


def capability_preflight(client, layout=None):
    required = ('chlora_get_capabilities', 'chlora_get_state', 'chlora_graph_get_summary',
                'chlora_get_operation', 'chlora_graph_get_layout_geometry')
    if layout is not None:
        required += ('chlora_graph_preview_layout', 'chlora_graph_apply_layout')
    if any(tool not in client.schemas for tool in required):
        raise ValueError('connection lacks required layout/capability tools')
    caps = unwrap(client.tool('chlora_get_capabilities', {}))
    if caps.get('readyRenderer') is not True:
        raise ValueError('live Host renderer is not ready')
    # Static adapter schemas only describe arguments. Require live feature
    # evidence as well; exact Host feature schema is checked below.
    features = caps.get('features', {})
    if caps.get('geometrySchemaVersion') != 2 or not all(features.get(name) is True
            for name in ('pagedInventory', 'compactInventory', 'portProjection', 'backgroundGeometry')):
        raise ValueError('live Host lacks required inventory capabilities')
    host_layout = caps.get('layout', {})
    if layout is not None:
        if not all(features.get(name) is True for name in ('deltaLayout', 'mixedLayout')):
            raise ValueError('live Host lacks mixed/delta layout support')
        if layout.get('containers') and features.get('containerTranslation') is not True:
            raise ValueError('live Host lacks container translation')
        if not {'bounds', 'none'} <= set(host_layout.get('qualityModes', [])):
            raise ValueError('live Host lacks required quality modes')
        if set(layout) - set(host_layout.get('fields', [])):
            raise ValueError('live Host lacks requested layout fields')
        for name, rows in layout.items():
            maximum = host_layout.get('limits', {}).get(name)
            if type(maximum) is not int or len(rows) > maximum:
                raise ValueError('live Host layout entry limit unavailable/exceeded')
    geometry = client.schemas['chlora_graph_get_layout_geometry'].get('properties', {})
    if 'compact' not in geometry.get('representation', {}).get('enum', []) \
            or 'includePorts' not in geometry:
        raise ValueError('connection lacks compact inventory schema')
    if layout is not None:
        for tool, quality in (('chlora_graph_preview_layout', 'bounds'), ('chlora_graph_apply_layout', 'none')):
            props = client.schemas[tool].get('properties', {})
            if quality not in props.get('quality', {}).get('enum', []):
                raise ValueError('connection lacks required quality mode')
            fields = props.get('layout', {}).get('properties', {})
            if set(layout) - set(fields):
                raise ValueError('connection lacks requested layout fields')
    return caps


def float32(value):
    """The native Point<float>/Rectangle<float> storage operation, ties-to-even."""
    return struct.unpack('!f', struct.pack('!f', value))[0]


def storage_tolerance(value, scale=1):
    """Half one IEEE754 float32 ULP in the actual storage domain.

    Native positions/frame/comment sizes use scale1; CSS node dimensions become
    native envelope lengths at scale3. 1e-9 only covers double arithmetic noise.
    Direct fields are compared to the exact nearest float32 value instead;
    this bound is used only to propagate independent storage into envelopes.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return 0
    try:
        bits = struct.unpack('!I', struct.pack('!f', abs(value / scale)))[0]
    except (OverflowError, struct.error):
        raise ValueError('geometry exceeds float32 storage domain')
    exponent = (bits >> 23) & 255
    if exponent == 255:
        raise ValueError('geometry exceeds float32 storage domain')
    ulp = math.ldexp(1.0, -149 if exponent == 0 else exponent - 127 - 23)
    return max(1e-9, scale * ulp * 0.5)


def close_number(a, b, tolerance=None):
    if not (isinstance(a, (int, float)) and not isinstance(a, bool) and math.isfinite(a)
            and isinstance(b, (int, float)) and not isinstance(b, bool) and math.isfinite(b)):
        return False
    if tolerance is not None:
        return abs(a - b) <= tolerance
    try:
        rounded = float32(b)
    except (OverflowError, struct.error):
        return False
    # Preview may still contain the exact JSON double; native readback contains
    # its nearest float32. Admit those two values, not an arbitrary interval.
    return abs(a - b) <= 1e-9 or abs(a - rounded) <= 1e-9


def geometry_tolerance(item, all_items, field, axis):
    """Propagate only independently stored source rounding into derived geometry."""
    value = item.get(field, {}).get(axis)
    if field not in ('bodyBounds', 'bounds'):
        return None  # exact JSON or exact nearest float32 storage, plus 1e-9 noise
    kind, placement = item.get('kind'), item.get('placement', {})
    if kind == 'group':
        source = item.get('position', {}) if axis in ('x', 'y') else item.get('frameSize', {})
        return storage_tolerance(source.get(axis, value))
    if kind == 'comment':
        source = item.get('position', {}) if axis in ('x', 'y') else item.get('size', {})
        if axis in ('w', 'h') and source.get(axis, 0) < (216 if axis == 'w' else 144):
            return 1e-9  # fixed rendered minimum, no size-rounding amplification
        return storage_tolerance(source.get(axis, value))
    if kind == 'cable-pin':
        return storage_tolerance(item.get('center', {}).get(axis, value)) if axis in ('x', 'y') else 1e-9
    if kind != 'node':
        return storage_tolerance(value)
    def dimension_error(node, dimension):
        css = node.get('size', {}).get('wCss' if dimension == 'w' else 'hCss')
        body = node.get('bodyBounds', {}).get(dimension)
        if not isinstance(css, (int, float)) or not isinstance(body, (int, float)) or abs(body - css * 3) > 1e-9:
            return 1e-9  # intrinsic/fixed dimensions are independent of stored size
        return storage_tolerance(css) * 3
    if axis in ('w', 'h'):
        return dimension_error(item, axis)
    owner = all_items.get('node:' + str(placement.get('ownerNodeKey')))
    if placement.get('kind') == 'attached-node' and owner:
        error = storage_tolerance(owner.get('position', {}).get(axis, value))
        if axis == 'x' and placement.get('direction', 'output') == 'output':
            error += dimension_error(owner, 'w')
        return error
    group = all_items.get('group:' + str(placement.get('groupId')))
    if placement.get('kind') == 'group-port' and group:
        error = storage_tolerance(group.get('position', {}).get(axis, value))
        frame = group.get('frameSize', {})
        if axis == 'x':
            if placement.get('side') == 'right': error += storage_tolerance(frame.get('w', 0))
        else:
            fraction = placement.get('position', 0)
            height = frame.get('h', 0)
            # y=top+height*fraction: bound each float source and their product.
            eh, ep = storage_tolerance(height), storage_tolerance(fraction)
            error += abs(fraction) * eh + abs(height) * ep + eh * ep
        return error
    return storage_tolerance(item.get('position', {}).get(axis, value))


def expected_projection(before, delta, preview_geometry):
    """Complete expected inventory for byte-truncated pure container translations.

    Nonlinear intrinsic resize/relative port changes require complete affected
    preview geometry. Never treat its byte-limited prefix as full coverage.
    """
    _, original = geometry_document(before)
    expected = copy.deepcopy(original)
    preview_items = preview_geometry.get('items', [])
    if preview_geometry.get('coverage', {}).get('readbackRequired'):
        if any(rows for category, rows in delta.items() if category not in ('containers', 'groups')):
            raise ValueError('truncated mixed preview needs a smaller proposal; nonlinear geometry cannot be inferred')
        def shift(item, dx, dy, saved=True):
            view_dx, view_dy = dx, dy
            raw_field = 'position' if isinstance(item.get('position'), dict) else 'center'
            if saved and isinstance(item.get(raw_field), dict):
                value = item[raw_field]
                nx, ny = float32(float32(value['x']) + dx), float32(float32(value['y']) + dy)
                view_dx, view_dy = nx-value['x'], ny-value['y']
                value.update(x=nx, y=ny)
            for field in ('bodyBounds', 'bounds'):
                value = item.get(field)
                if not isinstance(value, dict): continue
                for axis, amount in (('x', view_dx), ('y', view_dy)):
                    if axis in value: value[axis] += amount
                for edge, amount in (('left', view_dx), ('right', view_dx), ('top', view_dy), ('bottom', view_dy)):
                    if edge in value: value[edge] += amount
            return view_dx, view_dy
        moved_groups, moved_nodes = {}, {}
        for row in delta.get('containers', []):
            container = original.get('group:' + str(row['groupId']))
            if not container or not container.get('position'):
                raise ValueError('container projection requires saved frame')
            dx = float32(float32(row['x']) - float32(container['position']['x']))
            dy = float32(float32(row['y']) - float32(container['position']['y']))
            ids = {row['groupId']}
            for item in original.values():
                if item.get('kind') == 'group' and row['groupId'] in set(ancestors(original, item.get('parentGroupId', 0))):
                    ids.add(item['groupId'])
            members = {key for group_id in ids for key in original['group:' + str(group_id)].get('memberNodeKeys', [])}
            for group_id in ids:
                group_item = expected['group:' + str(group_id)]
                shift(group_item, dx, dy)
                if group_id == row['groupId']:
                    # Native root is anchored directly to requested float32,
                    # bypassing cancellation in old+float32(request-old).
                    nx, ny = float32(row['x']), float32(row['y'])
                    shift(group_item, nx-group_item['position']['x'], ny-group_item['position']['y'], saved=False)
                    group_item['position'] = {'x': nx, 'y': ny}
                old_point = original['group:' + str(group_id)]['position']
                moved_groups[group_id] = (group_item['position']['x']-old_point['x'], group_item['position']['y']-old_point['y'])
            for key in members:
                obj_key = 'node:' + key
                if obj_key not in expected: raise ValueError('container member missing from inventory')
                moved_nodes[key] = shift(expected[obj_key], dx, dy)
            for key, item in original.items():
                if item.get('kind') in ('comment', 'cable-pin') and item.get('parentGroupId') in ids:
                    shift(expected[key], dx, dy)
        # Boundary and attached bodies follow owners even when their saved raw
        # anchors are not explicit Group members. Translate raw member anchors
        # once; derived displayed origins always translate exactly once.
        for key, item in original.items():
            if item.get('kind') != 'node': continue
            placement = item.get('placement', {})
            movement = moved_groups.get(placement.get('groupId')) if placement.get('kind') == 'group-port' \
                else moved_nodes.get(placement.get('ownerNodeKey')) if placement.get('kind') == 'attached-node' else None
            if movement:
                saved_position = copy.deepcopy(expected[key].get('position'))
                expected[key] = copy.deepcopy(item)
                shift(expected[key], *movement, saved=False)
                if item.get('nodeKey') in moved_nodes:
                    expected[key]['position'] = saved_position
        for row in delta.get('groups', []):
            item = expected.get('group:' + str(row['groupId']))
            if item is None: raise ValueError('missing affected ancestor frame')
            x, y, w, h = (float32(row[k]) for k in ('x', 'y', 'w', 'h'))
            item['position'] = {'x': x, 'y': y}
            item['frameSize'] = {'w': w, 'h': h}
            item['bounds'] = {'x': x, 'y': y, 'w': w, 'h': h,
                              'left': x, 'top': y, 'right': x+w, 'bottom': y+h}
    for item in preview_items:
        if item.get('key') not in original:
            raise ValueError('preview introduced unknown object identity')
        expected[item['key']] = copy.deepcopy(item)
    return {'items': list(expected.values()), 'coverage': {'complete': True}}


def verify_readback(before, after, expected_geometry, delta, semantic_before, semantic_after):
    if semantic_before != semantic_after:
        raise ValueError('semantic routing/node topology changed during layout')
    _, old = geometry_document(before)
    _, actual = geometry_document(after)
    if set(old) != set(actual):
        raise ValueError('inventory identity coverage changed during layout')
    expected = {item['key']: item for item in expected_geometry.get('items', [])}
    if len(expected) != len(expected_geometry.get('items', [])):
        raise ValueError('preview geometry has duplicate identity')
    requested_keys = set()
    for category, rows in delta.items():
        for row in rows:
            prefix = 'node' if category in ('nodes', 'nodeSizes', 'groupPorts') else 'group' \
                if category in ('groups', 'containers') else 'comment' if category == 'comments' else 'cable-pin'
            identity = row.get('nodeKey', row.get('groupId', row.get('commentId', row.get('pinId'))))
            requested_keys.add(prefix + ':' + str(identity))
    if requested_keys - set(expected):
        raise ValueError('preview omitted requested object geometry')
    for key in actual:
        if actual[key].get('placement') != old[key].get('placement'):
            # Group-port position tuning is intentional, ownership is still fixed.
            planned = next((row for row in delta.get('groupPorts', []) if 'node:' + row['nodeKey'] == key), None)
            if not planned:
                raise ValueError('object placement ownership changed: ' + key)
            for field in ('kind', 'groupId', 'nodeKey'):
                if actual[key].get('placement', {}).get(field) != old[key].get('placement', {}).get(field):
                    raise ValueError('Group port owner changed')
        target = expected.get(key, old[key])
        for field in ('position', 'center', 'bodyBounds', 'bounds', 'size', 'frameSize'):
            wanted, got = target.get(field), actual[key].get(field)
            if wanted is None:
                if got is not None:
                    raise ValueError('unexpected visible geometry: ' + key)
                continue
            if not isinstance(got, dict) or any(not close_number(got.get(k), wanted.get(k), geometry_tolerance(target, expected, field, k)) for k in ('x', 'y', 'w', 'h', 'wCss', 'hCss') if k in wanted):
                raise ValueError('geometry readback differs: ' + key + '/' + field)
        if target.get('parentGroupId', 0) != actual[key].get('parentGroupId', 0):
            raise ValueError('object parent ownership changed: ' + key)
    for row in delta.get('groupPorts', []):
        p = actual['node:' + row['nodeKey']]['placement']
        if p.get('side') != row['side'] or not close_number(p.get('position'), row['position']):
            raise ValueError('Group port readback differs')
    return {'semanticRoutes': 'unchanged-exact-multiset', 'geometry': 'requested-and-derived-preview-matched',
            'identities': len(actual), 'visualReadability': 'not assessed', 'audioAcceptance': 'not assessed'}


def verify_requested(proposal, geometry):
    """Ensure the preview expresses the request, including unchanged rows."""
    items = {item['key']: item for item in geometry.get('items', [])}
    for category, rows in proposal.items():
        for row in rows:
            prefix = 'node' if category in ('nodes', 'nodeSizes', 'groupPorts') else 'group' \
                if category in ('groups', 'containers') else 'comment' if category == 'comments' else 'cable-pin'
            identity = row.get('nodeKey', row.get('groupId', row.get('commentId', row.get('pinId'))))
            key = prefix + ':' + str(identity)
            item = items.get(key)
            if item is None:
                raise ValueError('preview omitted original requested object: ' + key)
            if category in ('nodes', 'comments', 'pins'):
                point = item.get('position') if category in ('nodes', 'comments') else item.get('center')
                if not point or any(not close_number(point.get(axis), row[axis]) for axis in ('x', 'y')):
                    raise ValueError('preview does not express requested origin: ' + key)
                if category == 'comments' and 'w' in row:
                    size = item.get('size', {})
                    if not close_number(size.get('w'), row['w']) or not close_number(size.get('h'), row['h']):
                        raise ValueError('preview does not express requested stored native Comment size')
            elif category == 'containers':
                point = item.get('position', {})
                if any(not close_number(point.get(axis), row[axis]) for axis in ('x', 'y')):
                    raise ValueError('preview does not express requested container saved-frame origin')
            elif category == 'nodeSizes':
                size = item.get('size', {})
                if not close_number(size.get('wCss'), row['w']) or not close_number(size.get('hCss'), row['h']):
                    raise ValueError('preview does not express requested stored CSS size: ' + key)
            elif category == 'groupPorts':
                p = item.get('placement', {})
                if p.get('side') != row['side'] or not close_number(p.get('position'), row['position']):
                    raise ValueError('preview does not express requested Group port')


def execute(client, plan, timeout=120, progress=None):
    progress = progress if progress is not None else {}
    progress.update(stage='preflight', writeAttempted=False, writeReplay=False)
    caps = capability_preflight(client, plan['layout'])
    state = client.tool('chlora_get_state', {})
    if 'graphNodes' not in state or 'graphWires' not in state:
        raise ValueError('full semantic Graph state required, including hidden routes')
    binding = bound(state)
    if plan.get('expectedBinding') is None or binding != plan['expectedBinding']:
        raise ValueError('planned Graph binding changed/missing; replan')
    before_semantic = semantic_routes(state)
    if 'expectedSemanticRoutes' in plan and json.dumps(before_semantic, sort_keys=True) != json.dumps(plan['expectedSemanticRoutes'], sort_keys=True):
        raise ValueError('planned semantic routes changed; replan')
    progress['stage'] = 'inventory-before'
    before = collect(client, state, timeout)
    if plan.get('expectedLayoutRevision') != before['layoutRevision']:
        raise ValueError('planned layout revision changed/missing; replan')
    _, items = geometry_document(before)
    proposal = explicit_layout(items, plan['layout'])
    progress['stage'] = 'preview-bounds'
    preview = operation(client, 'chlora_graph_preview_layout', {**binding, 'layout': proposal, 'quality': 'bounds'}, timeout, progress)
    if preview.get('quality', {}).get('mode') != 'bounds':
        raise ValueError('Host did not honor bounds-only preview')
    if not isinstance(preview.get('layoutRevision'), str) or not isinstance(preview.get('layout'), dict):
        raise ValueError('preview lacks revision/changed delta')
    if preview['layoutRevision'] != before['layoutRevision']:
        raise ValueError('preview revision differs from inventory; replan')
    delta = preview['layout']
    if set(delta) - set(CATEGORIES):
        raise ValueError('preview returned unsupported layout delta')
    if any(delta.values()):
        explicit_layout(items, delta)
    expected = expected_projection(before, delta, preview.get('geometry', {}))
    verify_requested(proposal, expected)
    progress['preview'] = preview
    # Refresh semantic state just before the write. It must still match the
    # initial Graph; layout revision is separately enforced by native apply.
    current = client.tool('chlora_get_state', {})
    if bound(current) != binding or semantic_routes(current) != before_semantic:
        raise ValueError('Graph changed after preview; no write')
    if not any(delta.values()):
        after = collect(client, current, timeout)
        verification = verify_readback(before, after, expected, delta, before_semantic, semantic_routes(current))
        return {'status': 'verified-no-change', 'capabilities': caps, 'verification': verification, 'before': before, 'after': after, 'preview': preview}
    progress.update(stage='apply-none', writeAttempted=True)
    applied = operation(client, 'chlora_graph_apply_layout', {**binding, 'layout': delta,
                        'layoutRevision': preview['layoutRevision'], 'quality': 'none'}, timeout, progress)
    progress['applyResult'] = applied
    if applied.get('quality', {}).get('mode') != 'none':
        raise ValueError('Host did not honor none-quality apply; outcome unverified')
    progress['stage'] = 'readback'
    final_state = client.tool('chlora_get_state', {})
    if bound(final_state) != binding:
        raise ValueError('Graph binding changed after apply')
    after = collect(client, final_state, timeout)
    verification = verify_readback(before, after, expected, delta,
                                   before_semantic, semantic_routes(final_state))
    progress['stage'] = 'verified'
    return {'status': 'verified', 'capabilities': caps, 'verification': verification,
            'qualityCoverage': preview.get('quality'), 'before': before, 'after': after, 'preview': preview, 'applied': applied}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    offline = sub.add_parser('plan')
    offline.add_argument('--inventory', required=True); offline.add_argument('--spec', required=True)
    offline.add_argument('--state'); offline.add_argument('--output', required=True)
    for name in ('collect', 'execute'):
        p = sub.add_parser(name)
        p.add_argument('--socket', required=True); p.add_argument('--socket-identity', required=True)
        p.add_argument('--transcript', required=True); p.add_argument('--output', required=True)
        p.add_argument('--adapter', default=str(Path(__file__).resolve().parents[4] / 'tools/chlora_mcp.py'))
        if name == 'execute': p.add_argument('--plan', required=True)
    args = parser.parse_args()
    # Reserve output before starting any connection or mutation.
    with Path(args.output).open('x') as output:
        if args.command == 'plan':
            try:
                inventory = json.loads(Path(args.inventory).read_text())
                spec = json.loads(Path(args.spec).read_text())
                state = json.loads(Path(args.state).read_text()) if args.state else None
                result = make_plan(inventory, spec, state)
            except BaseException as exc:
                json.dump({'status': 'stopped', 'error': str(exc), 'writeAttempted': False}, output, indent=2)
                raise
        else:
            from graph_plan import Client
            progress = {'stage': 'connect', 'writeAttempted': False, 'writeReplay': False}
            client = None
            try:
                if not os.path.isabs(args.socket):
                    raise ValueError('exact absolute socket required')
                st = os.stat(args.socket)
                if not stat.S_ISSOCK(st.st_mode) or f'{st.st_dev}:{st.st_ino}' != args.socket_identity:
                    raise ValueError('socket filesystem identity mismatch')
                client = Client(args.socket, args.transcript, args.adapter)
                if args.command == 'collect':
                    caps = capability_preflight(client)
                    state = client.tool('chlora_get_state', {})
                    result = collect(client, state)
                    result.update(capabilities=caps, semanticState=state, transcript=args.transcript)
                else:
                    result = execute(client, json.loads(Path(args.plan).read_text()), progress=progress)
                    result['transcript'] = args.transcript
            except BaseException as exc:
                result = {'status': 'stopped', 'error': str(exc), 'transcript': args.transcript,
                          'outcome': 'unknown-or-unverified' if progress['writeAttempted'] else 'no-write', **progress}
                json.dump(result, output, indent=2); output.write('\n'); output.flush()
                raise
            finally:
                if client is not None: client.close()
        json.dump(result, output, indent=2); output.write('\n')


if __name__ == '__main__':
    main()
