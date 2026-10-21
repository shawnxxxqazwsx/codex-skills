# Graph nodes, containers and routing

Choose an entity by the requested signal path. The built-in palette contains
**Snake, Merge, Fanout, Router, Stack and Pin**. Groups, Comments, Port Snakes,
Graph IN/OUT and hosted plug-in nodes complete the supporting surface. A
container, wrapper or parameter link does not establish a parallel audio route.
Read [graph-recipes.md](graph-recipes.md) for composed operations,
[controls-and-plugins.md](controls-and-plugins.md) for gains, flags and hosted
parameters, and [layout.md](layout.md) for geometry, pins, wire styles and camera.
Discover exact current schemas rather than deriving arguments from this table.

Derive every span/partition from current input/output widths, port roles and
processor support. Counts may differ between IN and OUT and may be mono, stereo,
odd or mixed; a named immersive layout is not required. Stack creation uses
uniform width 1 or 2; stereo-row splitting can produce mixed lane widths. Native
limits below are capability bounds, not fixed session sizes or routing recipes.

## Inventory and lifecycle

| Native entity / state identity | Create and configure through MCP | Connect, edit and remove |
| --- | --- | --- |
| **Graph IN / OUT**, session-owned stable `nodeKey` | Already exist. Read actual MAIN widths and roles. Input width is session/connected-host state; `chlora_set_output_channels` requests Output width with its current layout token, and the connected Chloe bus may later publish its authoritative width. There is no general Graph IN width setter. | MAIN channel/bus routes, compatible Port Snakes and Snake wrapping are supported. `move_node` can position them. `remove_node` rejects both; do not include them in a processing-node deletion. Only wrapped OUT supports `add_snake_input`. |
| **Snake**, palette kind `bundle`, `isBundle` | `chlora_graph_add_builtin(kind="bundle")` creates an empty Pack. `bundle_append_channels` accepts explicit MAIN channels from one source owner; native packing sorts ascending and deduplicates. Mixing source owners is rejected. Array order is not an arbitrary channel permutation; use Router mapping for reordering. It is not a new hosted effect. | `bundle_connect` connects a populated Pack to a distinct empty Bundle as an aggregate strap; `bundle_fanout` unpacks to contiguous MAIN or SIDECHAIN inputs. Use the returned width/branch identities. Move/remove by `nodeKey`; do not invent a Bundle channel-count setter. |
| **Snake wrapping**, `snakeWrapped` on an existing compatible node | `set_snake(wrapped)` changes port presentation and incident routing. A changed mode removes incident routes; capture them first. `add_snake_output` requires wrapped IN or a compatible wrapped hosted node with a nonzero MAIN output; it does not add a Fanout/Bundle/Router or OUT output. `remove_snake_branch` manages removable wrapping branches. | `connect_snake` / `disconnect_snake` operate whole aggregate branches. `splice_snake_node` inserts a detached wrapped hosted node. Minimum required branches cannot be removed; Graph OUT uses input branches. Ordinary Graph wrapping aggregates existing ports; native Multi-mono creates independent mono processors. Wrapping does not change the hosted processor into Multi-mono. |
| **Port Snake**, owned sidecar `nodeKey` | `create_port_snake(ownerNodeKey,direction,channels,x,y)` selects distinct MAIN channels of compatible IO, Router or hosted node. Use sparse channel selections explicitly; native packing sorts selected channels ascending, not in request-array order. Owners must be Router or unwrapped compatible IO/hosted nodes; occupied partitions and arbitrary existing mappings can reject creation. | Ownership and attachment constrain edits/removal. Read sidecar flags and current routes; use aggregate/bundle tools appropriate to its returned ports. Do not treat it as a detached arbitrary-width processor or SIDECHAIN port wrapper. |
| **Fanout**, palette kind `fanout`, `isFanout` | `add_builtin(kind="fanout")` creates a one-port multi-edge routing node. Its one visible output supports multiple destination edges; `add_snake_output` does not apply to Fanout. | `connect_snake` makes explicit aggregate distribution. An independent Fanout can be moved/removed. Distribution duplicates a signal; gain and summing controls belong to Merge, mixer or processors. |
| **Merge**, palette kind `sum`, `isSum` | `add_merge(channels,inputs,x,y)` sets width and 2–64 inputs. `set_merge_inputs` changes branch count within native connection constraints. | Aggregate branch connections feed the sum. `set_merge_gain`: branch `-1` is output, other branches are zero-based inputs. Input mute, solo and polarity have dedicated tools. Multiple soloed branches sum; mute wins. Move/remove by key. |
| **Router**, palette kind `router`, `isRouter` | `add_builtin(kind="router",channels=...)`; `set_router_channels` negotiates independent input/output widths and refuses removal of connected ports/required crosspoints. | `set_router_route(input,output,on)`, `clear_router_output`, `reset_router` control internal mapping; reset is identity up to the smaller width. MAIN external routes and compatible Port Snakes remain separate. Move/remove by key. Matrix expansion is UI-local and has no MCP setter. |
| **Plugin Stack**, palette kind `stack`, stable `groupId`, member keys / `stackRow` | `create_stack(count,width,x,y)` creates empty explicit lanes, width 1 or 2, total ≤128. `configure_stack` requires empty Stack and detached external wires. `load_stack` / `load_stack_file` asynchronously create independent hosted instances per lane. | Route through actual boundary Fanouts. `split_stack_lane` splits a zero-based stereo row to two mono rows, copying loaded state asynchronously. `unload_stack` retains empty boundary and lane bypass. `move_group` moves it; Stack dimensions follow lanes, and ordinary `resize_group` / `remove_group` reject it. For whole Stack deletion use explicit `delete_selection(groupIds=[...])` and inspect affected topology. |
| **Group**, stable `groupId`, ordinary container | `create_group(nodeKeys,childGroupIds,...)`, `set_node_group`, `set_group_parent` manage membership/nesting. `set_group_comment` edits its title annotation. | `move_group` includes descendants/Comments; `resize_group` sets ordinary bounds. `remove_group` removes the container while preserving processing members/promoting contents. `detach_group` and `splice_group_on_wire` operate supported two-boundary inline Groups. Group membership alone adds no processing or mixing. Each nested Group keeps independent input and output boundary Fanouts; the current implementation's default connected MAIN/SIDECHAIN cut uses that Group's own ports, with a separate input carrier for a hosted processor's connected SIDECHAIN bus. A parent does not substitute or adopt a child's port as its own. |
| **Group boundary Fanout**, owned `nodeKey` plus side/position | `add_group_fanout` adds an explicit port to a regular Group, not a Stack. Existing automatic/adopted ports must be read back. An eligible selected entrance Fanout may be reused as the Group input boundary, preserving its identity and branches; an external dry branch alone does not disqualify it. Confirm the exact owner, side and branch mapping. Automatic-cut coverage does not establish every connected-Fanout selection or all-node selection. | `connect_group_fanout` remains full-width MAIN without offsets or SIDECHAIN. For manual ranges, the current source allows existing `connect_bus` between one regular Group boundary with known nonzero local width and one ordinary unwrapped non-Sum peer: source MAIN to destination MAIN or SIDECHAIN, with both zero-based offsets and destination role preserved. The full range must fit both endpoints or rejects without truncation. A single MAIN lane uses `connect_channel`. Boundary width is one plus the greatest channel index on any incident local carrier wire, not its collapsed one-socket display or 128-channel processor capacity; holes remain addressable when another higher or opposite-side incident lane establishes the extent, while a wholly unbound width-zero boundary cannot be ranged. Stack/loose Fanout, Bundle, Merge, two logical endpoints and wrapped peers remain excluded. `move_group_fanout` repositions an existing Group or Stack port on its fixed side. Do not delete/recreate a boundary to mimic a cosmetic move. |
| **Independent Comment**, stable `commentId`, optional parent | `create_comment(x,y,w,h,text,parentGroupId)`; `set_comment_text`, `move_comment`, `resize_comment`, `remove_comment`. | Annotation only; enclosing a node visually does not change membership or routing. Distinct from a Group's title Comment. `move_selection` accepts nodes and optionally one Comment; use `move_group` for containers. |
| **Cable Pin**, palette kind `pin`, stable `pinId` | `add_cable_pin` attaches to one exact existing visible cable, including role/channel and aggregate branch/width identity when applicable. | `move_cable_pin` / `remove_cable_pin`; presentation only, no audio input/output. It cannot be created as a free-standing routing node. Details in layout reference. |
| **Spectrogram**, Analyzer palette kind `spectrogram`, `isSpectrogram`, stable `nodeKey` | `add_builtin(kind="spectrogram",channels=...)`; width is 1–128 equal I/O, defaulting to the active layout. | Normal channel/Snake connections, copy/paste, project state and resize. Graph corners resize the node; its upper-right expand button opens a resizable spectrum view. Full and Smoothed share fixed FFT8192/BlackmanStd, all-input coherent `/sqrt(N)` including channel 4, Coherent+Power and 0.13s logarithmic envelope. Max and independent LFE overlay are off; no FFT settings. −24dB applies only at final display; audio remains sample-identical. No claim of complete MiRA matching. |
| **Hosted plug-in**, ordinary stable `nodeKey` | `add_plugin` / `add_plugin_file` asynchronously load an exact requested width. Verify terminal operation and effective widths. `set_node_channels` is for detached ordinary symmetric nodes; `set_bus_format` negotiates role-bearing formats. | Channel/bus or compatible Snake routing, `splice_node`, `detach_node`, move/ordinary resize, parameter controls and removal. Editor request alone does not prove a visible window. Read parameters and effective format rather than guessing support. |
| **Native Graph Multi-mono wrapper**, `isMultiMono` | Native Graph context menu can convert/resize N mono instances. **No MCP conversion/lane-count/auto-sync/full-state-sync tools currently exist.** Ordinary exact-width loading is not this conversion. | Existing wrapper state can be inspected. Do not substitute Stack or `set_multi_link` while claiming wrapper equivalence. Native implementation requires mono-capable plug-ins; dedicated operations are a real coverage gap. |

To wrap only existing Groups, keep the required `nodeKeys` field as `[]` and
pass their live IDs in nonempty `childGroupIds`. Both selections empty are
invalid. A newer CLI's local schema does not prove an older running Host accepts
this form; retain an explicit owner rejection instead of adding a dummy node or
reparenting children to imitate the requested operation.

Read attached Fanout positions from resolved renderer geometry, not their raw
node `x`/`y`. Ungrouping a container with saved bounds releases adopted Fanouts
beside its current boundary, with the ordinary body outside the former frame:
the output aligns at the left edge, and the input at the right edge. A legacy
unbounded container retains the stored node position. Read back the surviving
ordinary Fanouts' actual geometry, identity, branches and signal routes; keep the
affected source-to-sink layout clear using the geometry-only workflow in
[layout.md](layout.md). Older running Hosts may still restore the stale anchor;
report that exact behavior instead of treating a newer helper as runtime proof.

After each Group creation, undo/redo that changes its boundary or crossing, and
restore, read back the complete cut: each Group's input/output ownership and
every crossing MAIN/SIDECHAIN wire, including its role-relative channel or aggregate-branch identity and
order. If readback is incomplete, report the exact Group, side and missing port
or crossing; do not delete/recreate ports or reroute a cable just to make the
drawing look regular. An intentionally authored bypass that skips a parent
Group is valid; preserve that saved route rather than automatically routing it
through the parent on restore.

Connected SIDECHAIN automatic cuts have focused software verification and are
included in the deployed Host; actual native Graph acceptance remains pending.
Current source also creates independent input/output boundary-carrier pairs for
each selected Router or channel Align when all selected routing members are
Router, channel Align or LFO and at least one selected Router/Align has real
MAIN inputs and outputs. LFO adds no audio ports. These carriers are internal
Group interfaces only; they do not connect selected members to each other or to
external sources/sinks. This configured-selection behavior has focused
source-engine software coverage and is included in the formally deployed Host;
confirm that a matching Host process has loaded the deployment before relying on it. The rule does not add
unresolved Fanout or unconnected Merge selections. Separate peerless Main/Web
software checks cover document Undo/Redo for two-channel Router/Align Group
creation with no or one-sided external wiring. They also cover unconnected Router+LFO and Router+Align mixed
selections, including independent audio interfaces and unchanged member state. Nested Main/Web checks
cover child-only and child+ordinary wrapping with independent parent/child
interfaces and complete document Undo/Redo. A separate peerless Main/Web
Group-only parent removal check covers retained child and ordinary contents,
exact two-channel route contraction, and document Undo/Redo. These checks do not establish
native gestures, CLI transport or REAPER acceptance.
Manual range reconnection is included in the formally deployed Host, but confirm
that the current matching Host process has loaded the deployment before using
it; installed package, resource and CLI metadata do not prove active-process
behavior. The source UI lets a contiguous selected MAIN range enter Group input
lane 0, or routes the Group aggregate output to a visible ordinary SIDECHAIN
input when the whole known width fits; Alt replacement refuses aggregate
overlap. The current wrapped MAIN UI hides SIDECHAIN input. Focused software and
peerless Main checks do not establish native Graph gesture acceptance, current CLI transport for this
operation, all-node/selection coverage, same-Chloe-session restart, or REAPER
acceptance; the command/schema did not change. After using a supported range,
read back the boundary owner and every role-relative channel edge.
`delete_selection` can remove an exact visible ordinary SIDECHAIN wire; that
does not imply other endpoint types can be reconnected.

Hosted nodes (including Stack members and native Multi Mono wrappers) also
support `set_bypass(nodeKey,on)`. Read back `bypassed` with the current Graph
tuple; bypass preserves MAIN signal and routing. See
[controls-and-plugins.md](controls-and-plugins.md) for scope and the M shortcut.

Table tool names without the prefix mean `chlora_graph_...`.

## Distinguish routing and control propagation

- **Parallel audio** requires explicit distribution and recombination edges.
  Fanout distributes; Merge sums. Stack lanes normally partition a channel
  span; they are not automatically dry/wet parallel branches. A Group adds
  ownership and boundaries, not an implicit parallel processor.
- **Multi Channel Strip** uses shared exact-width hosted slots with explicit
  start/channel span and placement layers; **Multi Mono Strip** uses mono slots
  on explicit lanes. Both are session modes selected by `chlora_set_mode`, not
  Graph palette nodes. Mode conversion may discard processing; do not switch
  modes just to approximate a missing Graph wrapper control.
- **Stack macro** is a hosted-parameter gesture from its first member, with
  compatible parameter layouts across lanes. `set_stack_macro` preserves
  relative offsets or applies absolute values as requested. List the actual
  first-member ID/layout before writing. `expose_parameter` exposes a writable
  control; `configure_parameters` captures native editor touches and its
  `exposed.configuring` readback. These do not alter audio wiring.
- **Multi Link** (`set_multi_link`) links compatible ordinary hosted nodes by
  exact parameter layout; **sync selection** (`set_sync_selection`) is transient
  parameter-target selection. Neither creates lanes, wraps ports or connects
  audio. Account for existing links before a parameter write. Details and
  verification belong to the controls reference.
- **Stack Names** (`set_stack_names`) is a visible WebUI preference, available
  for valid mono/stereo Stack lanes with identifiable incoming MAIN channels in
  an active session. Subsets and reordered lanes use their actual upstream
  channel names through Router, Snake, Fanout and symmetric hosted buses;
  differing origins at a sum, disconnected lanes and asymmetric hosted buses
  retain local numbers. Labels describe bus slots, not acoustic independence.
  Poll the operation and read `get_view_preferences.stacks[].namesAvailable/namesOn`;
  availability means at least one complete lane has names. Read it after wiring,
  rather than predicting it from Stack/session width equality. Names defaults on. No per-lane plug-in replacement
  or explicit Stack collapse action was found; do not invent either tool.

## Exact wires and safe edits

Read current visible wires and stable keys from `chlora_graph_get_summary` or
full Graph state. MAIN `connect_channel` is one zero-based channel edge;
`connect_bus` maps a contiguous MAIN source span to MAIN or SIDECHAIN inputs.
Connections are additive unless `replaceExisting` is requested. Preserve
unrelated destination routes; replacing part of an aggregate route requires
whole-branch handling. `disconnect_channel` cannot remove one hidden piece of a
logical aggregate cable; use `disconnect_snake` for that cable.

`insert_builtin_on_wire` creates Bundle/Merge/Fanout/Router on an exact visible
MAIN wire atomically; `splice_existing_builtin` uses a detached existing builtin
and retains its identity/state. Copy all source/destination channel and branch
fields from readback. Ordinary plug-in splice, wrapped plug-in splice and Group
splice have different schemas; select the matching primitive. SIDECHAIN
insertion is not implied by MAIN insertion support.

Use `delete_selection` for an explicitly requested mixed deletion, including
exact wires and explicit Group/Comment IDs. `remove_group` is ungrouping, not a
whole-subgraph deletion. Attached Stack members, owned sidecars and required
boundaries have native guards; a rejection is not authorization to dismantle
ownership through lower-level calls. Re-read state after any failure.

See layout reference for signed coordinates, renderer geometry/revision,
ordinary-node versus container sizing, port alignment, pins and wire styles.
These change presentation; verify that audio edge identities remain unchanged.

## Presets and clipboard

`copy_plugins` / `duplicate_plugins` take explicit `nodeKeys` and optional
`groupIds`; selecting members does not select a whole container. `paste_plugins`
is asynchronous. Fresh clones have fresh live identities.

Graph preset save, repeated recall, library revision guards, local identities
and copy-only placement are covered by [presets.md](presets.md). Presets and
clipboard are distinct from audio routing; recall/paste creates fresh live
identities and requires asynchronous operation readback.

## Source evidence and limits

This inventory is source-backed, not a live/audio acceptance receipt. Palette:
[palette source](../../../../apps/host/ui/host-surface.html) (lines 477–542); creation dispatcher
`emitGraphBuiltinDragDrop`. MCP schemas: [adapter](../../../../tools/chlora_mcp.py) named tool
`inputSchema` entries. Native mutation ownership:
[Graph dispatch](../../../../apps/host/juce/ChloraMcpGraph.h) (`executeChloraMcpGraph` handlers),
[engine](../../../../apps/host/juce/PluginHostEngine.h) (`createAdvancedStack`, `setAdvancedGraphGroupBounds`,
`removeAdvancedGraphGroup`). Native-only Multi-mono menu:
[native Graph menu](../../../../apps/host/juce/GraphEditorComponent.h) (lines 897–945); implementation
`PluginHostEngine.h:setAdvancedNodeMultiMono`,
`syncAdvancedMultiMonoStateFromVisible`, `setAdvancedMultiMonoAutoSync`.
Use symbols if later edits shift line numbers. Engine-internal hidden routing
nodes are not an additional user palette: do not fabricate creation/configuration
APIs for them. Native UI affordances do not establish MCP support.
