# Chlora MCP graph recipes

These are checked sequences, not transactions. A synchronous write returns the
new binding tuple; use it in the next call. After an asynchronous load, poll its
operation and read state again. Do not reuse an old topology token.

## Low-cost model workflow

- Read `chlora_graph_get_summary` for node keys and exact wires. Request full
  `chlora_get_state` when slot, format, or layout detail is needed.
- For Group boundaries, use `groups[].fanouts[].nodeKey/side/position` and the
  node's `groupId`; left and right Fanouts are distinct routing endpoints.
  Independent annotations are in `comments[]` with stable IDs and geometry.
- A visible aggregate Snake cable is represented as `isBundle: true` and its
  summary wire includes `bundleWidth`, `snakeBranch` (source branch), and
  `snakeInputBranch` (destination branch). Ordinary per-channel wires do not
  carry branch identity. Compare the aggregate fields when checking a Snake
  route; do not infer a branch from a cable's position on screen.
- Resolve the plug-in UID with `chlora_find_plugins`; retain the exact `uid`.
  For a known absolute local `.vst3` path, use
  `chlora_graph_add_plugin_file` and poll the same operation endpoint.
- Load, poll `chlora_get_operation`, then refresh state before routing.
- List parameters, retain the exact normalized value and layout token, write one
  parameter, and re-list to verify quantization/readback.
- On a stale binding or layout token, stop and rediscover; never replay a timed
  out write without checking its operation/state result.
- Include `instanceId`, `bindingGeneration`, `graphTopology`, and
  `graphLifetime` in every bound `chlora_graph_*` call. Keep the last two as
  decimal strings. `chlora_graph_get_summary` takes `{}` and returns the
  fresh tuple; other read-only Graph calls still require it.

## Deterministic dry/wet parallel reverb

Use this on a blank Graph, or after explicitly recording and accepting the
existing routes that Snake wrapping will remove.

1. Identify Graph IN and OUT keys and their MAIN widths in the summary.
   Compare `inputChannels`, `outputChannels`, the requested route width (if
   any), and the plug-in's catalog support. Select one common width for
   IN → reverb → Merge → OUT before mutation. Prefer a reverb whose
   `verifiedChannels` includes that width. A `candidateChannels` value is not
   verification, but an isolated exact-width load may test it: poll the
   terminal operation, then require the new node's MAIN input and output widths
   to equal the requested width before routing. If the load rejects that width,
   stop or choose another reverb when the user did not require an exact model.
   Never construct a partial route around a failed or pending load. Choose free creation points
   in the `0..20000` creation-coordinate range. On a blank Graph, start with
   reverb `x: 600, y: 300` and Merge `x: 900, y: 300`; inspect geometry and
   adjust when existing nodes occupy those points. Load the reverb plug-in at
   the requested exact `channels` width with `x` and `y`; poll, then confirm
   its returned node key.
2. List its parameters and use their IDs, layout, labels, and readback text to
   establish a fully wet return. Set an identified Mix/Wet control to its
   verified wet-only value and an independent Dry control to its verified
   silent value when present. Normalized `1.0` and `0.0` are usable only when
   the descriptors/readback confirm those meanings. If the plug-in cannot be
   shown to return wet-only signal, stop this parallel recipe and report the
   unresolved processor setting; a second dry path would otherwise duplicate
   its dry signal.
3. Wrap Graph IN, reverb and Graph OUT with `chlora_graph_set_snake` where
   needed. This clears incident wires on any changed node. Keep Graph IN at
   **one compact Snake output at the chosen route width**. Add an explicit Fanout builtin
   with `chlora_graph_add_builtin` (`kind: "fanout"`) for parallel branches;
   do not add a second Graph IN Snake output.
4. Add a Merge with the required `channels` set to the intended width,
   `inputs: 2`, and the planned `x` and `y`. Connect exactly:
   `IN branch 0 → Fanout input 0`, `Fanout output 0 → reverb input 0`,
   `Fanout output 0 → Merge input 0` (dry),
   `reverb output 0 → Merge input 1` (wet), `Merge output 0 → OUT input 0`.
   One Fanout output can feed both aggregate destinations without adding
   another Graph IN socket. On an existing live IN→reverb Snake wire,
   `chlora_graph_insert_builtin_on_wire` with `kind: "fanout"` and the exact
   wire identity inserts it atomically; then connect its output to the dry
   Merge input with `replaceExisting: true` and remove the now-unused extra
   Graph IN branch using `chlora_graph_remove_snake_branch`. Verify only one
   Graph IN Snake output remains.
   Use `chlora_graph_connect_snake` and `replaceExisting: false` unless the
   user requested replacement of a conflicting route. Connecting the last
   visible Merge input can add one empty spare bank automatically. Identify
   active dry and wet branches from the returned wires; an extra entry in
   `sumBranches` is not another signal path.
5. If the user supplied gains, use them. Otherwise use explicit starting
   values `dryGainDb: 0`, `wetGainDb: -6`, and `outputGainDb: 0` and report
   those values. Write them with `chlora_graph_set_merge_gain` on branches 0,
   1, and -1 respectively; `branch: -1` is the Merge output. Read back all
   five wires, the reverb's wet setting and all three gains. The complete example and
   exact binding rules are in [Chlora MCP](mcp-tool-reference.md#pure-mcp-parallel-reverb-workflow).

This is a sequential recipe and does not prove realtime audition or level
matching. If a requested branch operation is absent from `tools`/MCP
validation, mark the recipe provisional and stop rather than inventing a call.

## Strip channel mapping

In Strip mode, route mapping is separate from plug-in slots. Use
`chlora_strip_set_route` for one `input` (bridge to insert) or `post`
(post-insert to output) edge. Adding an edge does not replace another edge to
the same destination; fan-in sums signals. To replace a destination map,
call `chlora_strip_clear_route_destination` first and read the returned
`routes`, then add the intended edge. `chlora_strip_reset_routes` restores
identity mapping, while `chlora_strip_clear_routes` silences the selected
stage or both stages. These operations are for Strip modes, not Graph.

## Per-channel Graph serial chains

For each requested channel `c`, load each processor as an exact 1-channel Graph
node with `x` and `y`, poll each load, and retain its stable key. On an open
canvas, place stage `j` initially at `x=400+200*j`, `y=200+120*c` only when
both coordinates are in `0..20000` and geometry shows space; otherwise plan
free coordinates from current geometry before loading. Confirm the plug-in actually
supports mono. Connect `IN[c] → first[0] → ... → last[0] → OUT[c]` with
`chlora_graph_connect_channel`, passing zero-based MAIN offsets. If a direct
`IN[c] → OUT[c]` route exists and the user wants replacement rather than dry
parallel, disconnect that exact pair. A plug-in load can restore default direct
IN-to-OUT wires even after clearing a Graph, so check again after all loads.
Read back every edge and ensure no
unwanted direct route remains. Repeat independently for other channels.

For cross-channel remaps, create a Router with a declared width, then set every
intended input/output crosspoint through `chlora_graph_set_router_route` and
read back its `routerRoutes`. Use `chlora_graph_clear_router_output` to empty
one output, or `chlora_graph_reset_router` to restore identity. Resize an
existing Router with `chlora_graph_set_router_channels` when input and output
widths differ; shrinking refuses ports or routes that are still connected.
Resize Merge branches with `chlora_graph_set_merge_inputs`, keeping each branch
identity and refusing deletion of a connected branch. Resize an
ordinary node with `chlora_graph_resize_node` when the arrangement needs it.
Never infer routing from node position, Group
membership, or similar names. Fanout and Stack members keep their individual
node identities.
To duplicate a selected plug-in chain, use `chlora_graph_duplicate_plugins`
with stable `nodeKeys`; poll its operation and use the returned new keys.
`chlora_graph_copy_plugins` stores plug-in state in Chlora's Graph clipboard;
`chlora_graph_paste_plugins` places it at a native Graph coordinate. Paste and
duplicate use isolated loading, so wait for terminal success before routing the
new nodes and then refresh the Graph binding.
Use `chlora_graph_move_selection` to shift a handful of stable node keys and
optionally one Comment by a single native-coordinate delta. For a larger
arrangement, preview and apply a layout plan with its renderer revision.
For mixed cleanup, call `chlora_graph_delete_selection` with four explicit
arrays: `nodeKeys`, `groupIds`, `commentIds`, and `wires`. Copy wire identities
from the current summary, including roles and channel offsets; bundle wires
also require width and both branch numbers. Leave unused arrays empty. The
host rejects stale or ambiguous wire identities before deletion. Read back
the remaining nodes and every neighboring route before the next edit.
To place a built-in directly on an existing MAIN cable, use
`chlora_graph_insert_builtin_on_wire` with the exact source/destination keys,
channel offsets, aggregate flag, width, and branch numbers from that visible
wire. The operation is atomic. `chlora_graph_splice_existing_builtin` moves a
detached built-in onto a wire without replacing its processor. After either
call, read back the inserted node identity and neighboring routes before
continuing.
To add an already loaded wrapped plug-in in series on one aggregate Snake
wire, confirm it has no MAIN connections, then call
`chlora_graph_splice_snake_node` with its stable key and the current visible
wire's source/destination keys, width, and two branch numbers. Read back the
two resulting aggregate edges and the absence of the replaced edge.

When the user asks to synchronize the same plug-in across Graph nodes, list
their stable keys and call `chlora_graph_set_multi_link`. Link at least two
compatible plug-in nodes; `unlink: true` removes the listed memberships.
Read back each node's `multiLink` identity before editing linked parameters.
Use `chlora_graph_set_sync_selection` for a temporary parameter-sync selection;
an empty `nodeKeys` list clears it. Inspect `graphSyncSelection` in the next
summary. This is separate from persistent Multi Link membership.
For a Stack macro, list parameters on the first member, retain its layout token,
and call `chlora_graph_set_stack_macro` with the Stack `groupId`, first-member
`nodeKey`, one stable `gesture` ID, and normalized start/value. Set `absolute`
to false to preserve lane offsets or true to set every compatible lane to the
same value. Read back all member values. Visible Graph controls appear in
node state; remove one with `chlora_graph_remove_exposed_parameter` using its
exact exposed `id`.

For a contiguous multichannel processor, use `chlora_graph_connect_bus` with
the source and destination starting offsets and `channels` instead of separate
lane calls. The call is atomic; use `destinationRole: "sidechain"` only when
the destination exposes that many SIDECHAIN inputs. Read back every lane and
refresh graph tokens before the next edit.

For sparse channel collection, create two Bundle nodes. Append explicit MAIN
source channels to the Pack with `chlora_graph_bundle_append_channels`, connect
the Pack to the empty Unpack with `chlora_graph_bundle_connect`, then use
`chlora_graph_bundle_fanout` to map dense lanes into the destination. Keep both
Bundle identities and the aggregate strap in the readback; channel offsets do
not replace the Bundle branch identity. An attached Bundle may become a
`hiddenRoutingNode`; its stable key remains valid for the Bundle tools.

For a visual cable bend, identify the exact visible wire in current state and
call `chlora_graph_add_cable_pin` with both stable node keys, MAIN/SIDECHAIN
offsets, and the desired point. Include `isBundle`, `bundleWidth`, and both
branch numbers for an aggregate cable. Keep the returned `pinId` for move or
remove calls; a topology edit may invalidate the original wire identity.
Use the same exact wire identity with `chlora_graph_set_wire_style` to choose
`curve` or `straight`; this changes presentation only.
For a Group boundary, `chlora_graph_add_group_fanout` creates a separate
Fanout with its own stable `nodeKey`; `chlora_graph_move_group_fanout` moves it
along the same side. `chlora_graph_connect_group_fanout` connects that attached
boundary to one ordinary MAIN peer at its supported width. The UI shows one
aggregate MAIN socket, and a two-channel Router boundary has been verified at
the wire level. Read back every expected lane. Preserve the boundary key. Group
membership alone never creates a signal route.
Group creation already provides one left and one right boundary Fanout. After
wiring the Group's internal path, `chlora_graph_splice_group_on_wire` inserts
that sealed Group on an exact visible MAIN wire; `chlora_graph_detach_group`
restores the external predecessor-to-successor route while retaining the
Group. Read back both external wires and all internal member identities.

When one Graph IO, Router, or compatible plug-in port needs a selected MAIN
channel subset as an aggregate socket, call `chlora_graph_create_port_snake`
with the owner key, `direction`, distinct zero-based `channels`, and required
`x`/`y` creation coordinates. Keep the returned Port Snake key and inspect
its actual attached routes before connecting further; creation may convert
an untouched default Graph IO identity path. A Port Snake appears as an
attached hidden Bundle in state. Its returned stable key is valid as either
endpoint of `chlora_graph_connect_snake` with branch `0`; use its
`bundleLaneCount` to match the other aggregate endpoint's width. For a
multichannel processor feeding stereo effects, keep the processor unwrapped,
create disjoint output Port Snakes for the selected channel pairs, and use
matching input Port Snakes on the receiving Router. Verify each resulting
visible wire has `isBundle: true` and the expected `bundleWidth`.

When the topology requires a Stack, use `chlora_graph_create_stack` with an
explicit lane count and width (1 or 2); retain its `groupId`. Configure only
while empty and disconnected, then read back the boundary Fanout identities.
Its left and right Fanouts start at the same normalized height. If a layout
operation has moved them independently, set both to the same `position` with
`chlora_graph_move_group_fanout` using their stable keys; do not add another
Stack boundary Fanout. Read back both positions and the unchanged wires.
Load an exact plug-in UID into every lane with `chlora_graph_load_stack` (or a
known absolute local `.vst3` path with `chlora_graph_load_stack_file`), poll
its operation, and read back all member keys before routing. `chlora_graph_unload_stack`
returns an empty bypass Stack without removing its boundary. To split one
stereo row into two mono rows, call `chlora_graph_split_stack_lane` with the
zero-based row, poll its operation, then read back the new widths and member
keys. A loaded split copies the source plug-in state to both replacements.

### Parallel immersive reverb with a height-only stereo delay Stack

For a 9.1.6 ITU 16-channel session, first confirm from live state that
zero-based channels 10..15 are FTL/FTR, MTL/MTR, RTL/RTR. Use one 16-channel
wet-only immersive reverb, one 16-channel Router with identity crosspoints,
one 16-channel two-input Merge, and **one Stack with `count: 3`, `width: 2`**.
Load the exact stereo delay UID into the empty Stack once; the operation must
return three independent member nodes. Read back each member's 2-in/2-out
width, worker state, and exact parameter descriptors. Set the desired tempo
sync, Ping-Pong mode, note divisions, feedback, and mix on all three members
and re-list each member to prove equality. A Stack macro may set a shared
parameter only after listing compatible descriptors and confirming the member
layout tokens; do not assume one member's setting automatically reaches the
other two.

Plan the signal path as `IN branch 0 -> Fanout`, then `Fanout -> reverb ->
Router -> Merge wet` and `Fanout -> Merge dry`. Keep Graph IN's compact IO
Snake at one output; the Fanout owns the explicit parallel split. The Router
retains the reverb's channels 0..9.
Route reverb outputs 10..15, in that order, through a six-lane output Port
Snake to the Stack's left boundary Fanout; route its right boundary Fanout to
a six-lane Router input Port Snake assigned channels 10..15. This preserves the
three stereo lane identities inside one visible Stack and keeps the external
connections as Snake cables. Complete Router output -> Merge wet -> OUT.
Read back the exact boundary Fanout keys, each aggregate cable's `isBundle`
and `bundleWidth`, Router crosspoints, Stack members, Merge gains, and no
ordinary duplicate feed into those six channels. The Stack boundary and its
members do not connect themselves to external nodes: wire both Fanouts.

If a previous channel partition left attached Port Snake sidecars on an owner,
remove only the affected sidecar nodes with `chlora_graph_remove_node` using
their stable `nodeKey`, then read back the owner's remaining sidecars before
creating the wider replacement. A Port Snake can be an invisible routing
node in the summary but still a valid explicit removal target. Reuse fresh
Graph binding tokens after each removal or creation. Never delete the plug-in
owner just to change its Port Snake partition.

## Arrange and group without changing the signal path

Use stable node keys from a fresh Graph summary. Create a Group only for
explicitly chosen members and retain the returned `groupId`; creation adds
boundary Fanouts and changes topology, so get a fresh summary and binding
before the next Graph call. A Group or Stack position has no routing meaning.

For layout, call `chlora_graph_get_layout_geometry` with the current Graph
binding and poll `chlora_get_operation` to success. Read the nested `result`
for actual geometry and `layoutRevision`. Build a non-empty `layout` with
`nodes: [{nodeKey,x,y}, ...]` (and `groups`/`groupPorts` only if needed).
Include only current, visible, movable nodes in `nodes`; the renderer rejects
`hiddenRoutingNode`, attached Port Snake sidecars, and Group/Stack boundary
Fanouts there. Position Stack/Group frames with `groups` and their boundary
Fanouts with `groupPorts`, using IDs from the current geometry. A Stack member
is visible but cannot move independently: leave its `nodeKey` out of `nodes`
and move the Stack through its `groupId` as one container. Preview rejects
independent Stack-member moves; apply still requires the validated plan.
These layout coordinates allow `-20000..20000`; creation coordinates above
allow only `0..20000`. Call `chlora_graph_preview_layout`, poll it, inspect
resolved geometry and quality metrics; then call `chlora_graph_validate_layout`
with the same proposed `layout`, poll it, and resolve reported collisions or
crossings. For a sparse Graph, require `nodeOverlap.pairs: 0`, zero `obstacleHits`,
and zero `wireIntersections`; use cable Pins to route dry returns around the
processing path when node placement alone cannot separate cables. Inspect the
rendered Graph as well, since quality metrics do not prove visually distinct
curves at every zoom level. Omitting `layout` validates only the current graph. Fetch geometry again
if a grouping or other geometry-changing write occurred. Apply with
`chlora_graph_apply_layout` using the current non-empty `layoutRevision`, poll
to success, and read the Graph summary to verify positions and unchanged wires.
If the revision is stale, recompute the plan from fresh geometry rather than
replaying the old apply request.

## Builtins and routing

The current surface includes Graph builtin creation for bundle/fanout/router,
exact MAIN channel connect/disconnect, atomic bus connect, router route updates, Merge branch mute/polarity and overload protection,
Snake input/remove, and node-channel updates. `chlora_graph_add_builtin`
accepts `channels` only as Router width. Fanout has one logical aggregate output
that can carry multiple edges; do not create extra sockets for those edges.
Use the operation's returned
node key and current graph tokens; preserve explicit Fanout boundaries and
individual member identities. If an operation's argument schema or result is
not present in the live MCP catalog, treat the corresponding recipe as
provisional.

## Recovery and limits

For a failed multi-step edit, read state first, identify the last confirmed
mutation, and undo once only when the history result is accepted. Poll state
until restoration completes, then rediscover all keys/tokens. Never describe a
sequence as atomic, auditioned, deployed, or AU-validated based on MCP state
alone.
