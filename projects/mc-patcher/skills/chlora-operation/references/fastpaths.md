# Compose common Graph routes

Read one current summary and the needed schemas. Resolve processing widths,
channel order, wrapped status, current wires and container membership before
writing. Reuse returned binding/state and await async work. Detailed entity
semantics are in [nodes.md](nodes.md); parameter/level decisions are in
[controls-and-plugins.md](controls-and-plugins.md).

## Choose the smallest matching construction

| Request | Construction |
|---|---|
| One mono channel | Exact MAIN channel edges, mono-capable processor |
| Contiguous stereo/wider bus | `connect_bus` with offsets and actual width |
| Whole wrapped bus in sequence | Snake branches; prefer exact aggregate-wire splice |
| Parallel processors | Split → independent chains → Merge, explicit branch gains |
| Dry plus wet effect return | Parallel recipe with effect verified wet-only |
| Process selected channels and preserve others | Selected subset → processor/Stack → identity Router gather |
| Repeat independent mono/stereo processing | Stack N×1 or N×2; one instance per lane |
| Pack or reorder source channels | Bundle or ordered PortSnake plus explicit mapping |
| Shared parameter changes across copies | MultiLink or sync selection; routing stays separate |
| Reuse a saved region | [Preset recall](presets.md), not reconstructing its internals |
| Clean the drawing | [Layout](layout.md), preserving semantic routes |

## Serial insertion and replacement

For one MAIN channel, use `connect_channel`; for a contiguous bus use
`connect_bus`. Retain both starting offsets. A stereo processor operates on a
pair; a multichannel processor must actually support the chosen width.
Independent mono lanes can use Stack or distinct nodes according to user intent.

For already wrapped equal-width endpoints, load a detached processor at its
path width, await it, confirm `mainIn/mainOut`, wrap it, then connect with
`connect_snake` using current source/destination branches. When adding it on
an existing aggregate wire, prefer `splice_snake_node`: retain exact width and
branch IDs, and verify the replaced wire becomes two serial wires. For an
ordinary supported MAIN wire, `splice_node`/`detach_node` offer native insertion
and removal. Detached nodes must meet the native operation's connection rules.

Only remove/replace the intended original feed. Read back that an old direct
path did not survive as an accidental parallel path. Wrapping an already
connected node clears its incident routes; include every affected edge in the
reconstruction scope. A node removal and a detach that restores continuity
have different outcomes.

## Parallel processing and dry/wet returns

Split the same intended bus into branch paths; gather once at a Merge of the
matching width. For a wrapped aggregate source, an explicit Fanout keeps one
compact output and legible split. For ordinary channel/bus paths, use the native
supported endpoints; don't create extra Graph IN sockets merely for fanout.
A split can occur after any compatible source node, not only Graph IN.

On an existing MAIN wire, `insert_builtin_on_wire(kind=fanout)` and a downstream
`kind=merge` insertion can preserve the original route while adding boundaries.
For detached construction, `add_builtin(kind=fanout)` and `add_merge(channels=W,
inputs=N)` create them; establish the Fanout input before matching its output
width. Inspect returned branch IDs before choosing Merge inputs. Native Merge
may retain a spare empty bank; `sumBranches` count is not the active path count.

For ordinary parallel processing, branch outputs can intentionally contain
full processed signal. For dry plus wet-only return, establish the effect's
wet-only state from listed descriptors and readback before adding a separate
dry branch. Do not infer “wet-only” from a name or a guessed normalized value.
An unresolved wet-only setting blocks that particular return topology, not
unrelated serial/parallel requests.

Write user-specified branch/output gains using `set_merge_gain`; output uses
branch -1. If balance is unspecified, preserve existing gains when meaningful;
otherwise choose and report an explicit starting balance. Mute, Solo and polarity
are separate Merge branch operations. Verify branch feeds, resulting gains and
one intended gathered downstream feed; listening/level matching is separate.

## Selected-channel processing with an identity gather

Let W be the full destination width and S the ordered selected source channels.
Resolve names from the current layout rather than fixed immersive numbering.
An identity Router gather preserves the untouched channels and replaces only S
with processed return lanes. Ensure the chosen processor widths sum to |S|.

For an ascending subset on compatible unwrapped ports, use output PortSnake on
the source and input PortSnake on the Router, both using the same S order; route
output sidecar → processor/Stack → input sidecar. PortSnake uses native ascending
order. Arbitrary reordering uses explicit Bundle packing or Router crosspoints
instead; see [advanced recipes](graph-recipes.md).

Before creating attached sidecars, remove exact authorized occupied edges at
those ports. If a replaced aggregate overlaps unselected channels, disconnect
it as a whole and explicitly restore those unselected channels. Native creation
may convert an untouched Graph IO identity route; inspect returned wiring and
restore all required passthrough lanes. A selected subset's own bus width is |S|,
not W. Never delete its plug-in owner just to replace a sidecar partition.

## Plugin Stack and built-in insertion

`create_stack(count=N,width=1|2)` → retain groupId/boundary keys →
`load_stack` or `load_stack_file` → await → inspect every member width/state.
Connect its left and right boundary Fanouts externally; creation/load does not
supply those feeds. Lanes remain independent. A single wider processor uses an
ordinary node; Stack widths are mono or stereo. Configure only while empty and
disconnected. See nodes.md for split/unload/macros/Names and nesting limits.

`insert_builtin_on_wire` supports the native insertable kinds and exact current
MAIN identity. `splice_existing_builtin` uses a compatible detached built-in.
Use full channel/aggregate/branch fields; do not derive a wire from a screenshot.
Group insertion similarly requires explicit supported boundary/internal routing.

## Offline plan helper

`graph_plan.py` composes `series`, `subset`, `stack`, `builtin`, `group`, and
explicit `steps`. `builtin` creates bundle/fanout/router or a Merge using its
native tool. The planner validates approved exact replacement edges and emits
their disconnects first; it is not a transactional or continuity-preserving
rewrite engine. For a live continuity-preserving splice, use exact native steps.
Subset owners must already be present in the snapshot; aliases do not stand in
for an unknown owner width. Group/Stack and capability limits remain native.

Example detached Stack component:

```json
{"replaceEdges": [], "components": [
  {"recipe":"stack","name":"lanes","count":2,"width":2,"x":1800,"y":600,
   "pluginPath":"/absolute/ExactInstalledPlugin.vst3"}
]}
```

This creates components, not a fully connected route. Capture references such
as `$lanes.groupId`, `$lanes.leftNodeKey` and `$lanes.rightNodeKey` use actual
returned state; missing boundaries stop execution. Explicit step shape:

```json
{"tool":"chlora_graph_connect_snake","arguments":{
  "sourceNodeKey":"CURRENT_SOURCE_KEY","destinationNodeKey":"$lanes.leftNodeKey",
  "sourceBranch":0,"destinationBranch":0},"capture":"optionalResult"}
```

Use current verified identities, paths and schemas. The executor automatically
fills current Graph/session binding for steps in the same active Graph; library
calls stay unbound. It does not invent wet values, presets/revisions, routing
crosspoints or parameter-layout tokens. Writes stop at first failure without
replay, with one cached schema set and transcript. Standalone Strip workflows
are not a template of this planner. `plannedChecks` describes intended checks;
inspect the returned state to judge the result.

For scoped offline placement, `layout(geometry,node_keys,origin,gap)` calculates
one loose-node row from actual native bounds. Containers use the native layout
workflow. No hardcoded session, device model, channel order or total width is
required by these recipes.
