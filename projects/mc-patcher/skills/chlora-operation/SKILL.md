---
name: chlora-operation
description: >-
  Operate a running Chlora through MCP for built-in Graph nodes, routing and
  layout, presets, Strip slots, mixer gain/mute/solo, and hosted plug-in parameters.
---

# Chlora operation

Use MCP state and supported operations to carry out the user's requested change.
Clara in conversational requests refers to this Chlora operation skill. Native UI
controls alone do not prove MCP support. Existing task authorization covers its
necessary operations; do not request approval again for a generated plan.

## Read only the relevant workflow

| User intent | Reference |
|---|---|
| Choose or manipulate an internal Node, wrapper, container or link | [nodes.md](references/nodes.md) |
| Serial, parallel, subset or repeated-lane routing | [fastpaths.md](references/fastpaths.md) |
| Sidechain, sparse/reordered channels, linked copies, uneven widths | [graph-recipes.md](references/graph-recipes.md) |
| Faders, input trim, Merge branch gain, Solo/Mute, node/slot Bypass and plug-in controls | [controls-and-plugins.md](references/controls-and-plugins.md) |
| Save, find, recall, repeat, insert, update or delete a preset | [presets.md](references/presets.md) |
| Arrange nodes, keep Graph operations/setups readable, simplify wires, Pins, Comments, camera or port alignment | [layout.md](references/layout.md) |
| Tool discovery, exact schemas, session/layout and Host settings | [mcp-tool-reference.md](references/mcp-tool-reference.md) |

These workflows compose. For “parallel reverb, then selected-channel delay and
clean layout,” combine routing, controls and layout; do not restart discovery
for each stage or read every reference by default. For any authorized Graph
operation or test setup that adds or changes nodes or wires, keep the affected
area readable as it is built: order paths source-to-processing-to-sink and keep
parallel lanes and owned boundaries clear. Use layout.md instead of postponing
readability until the end.

## Bind once, reuse current state

1. Begin with `chlora_get_state`: identify the intended active session, mode,
   channel names/widths and selection. Later Graph planning usually needs only
   `chlora_graph_get_summary`. Use stable node keys and explicit Group/Comment
   IDs; names and screen positions are not identities.
2. Session tools require `instanceId` (state's `activeInstanceId`) and
   `bindingGeneration`. Bound Graph tools additionally require `graphTopology`
   and `graphLifetime` as **decimal strings**. Use each mutation's returned
   binding/state for the next call. Refresh after async completion, restore,
   undo/redo, a stale token or a missing result. Do not add a summary before and
   after every deterministic mutation.
3. `chlora_graph_get_summary` is unbound. Preset list/get/update/delete and
   global Host preferences are also unbound; their own revision tokens apply.
   Layout/name/Insert/Output changes require current `channelLayoutToken` from
   full state. Exact schemas determine which tokens each call needs.
4. Poll `chlora_get_operation` for async loads, paste, renderer/layout and view
   operations. Finish pending work before dependent writes. Timeout means an
   unknown outcome: retain operation/transcript and inspect state; never blindly
   replay a load, paste or other write. Multi-step recipes are not transactions.
5. Cache needed schemas for the current connection. In the compact profile,
   common reads remain direct; other tools use `chlora_describe_tool` then
   `chlora_invoke`. Discover names only when unknown. See the tool reference for
   full-profile and stdio execution.

## Choose the signal operation before writing

- Work at any channel count supported by the current session and processor.
  Derive source width, destination width and each path/subset width separately;
  never infer one from the other. Use current channel names or explicit indices,
  validate each offset/span, and preserve mapping order. Unequal widths, odd
  counts and mixed mono/stereo/wider partitions need explicit routing, not
  padding to an immersive format or silently dropping leftover channels.
- Resolve the affected channel names/order, MAIN or SIDECHAIN role, branch
  identity and actual bus widths. Mono, stereo and wider buses use the same
  decision process; no fixed immersive channel numbering is assumed.
- Serial insertion replaces one path; parallel splitting duplicates a signal;
  Merge sums; Bundle packs; Router maps. Visual grouping, a Strip layer or a
  plug-in Stack does not itself establish parallel summing or an external wire.
- Distinguish parallel processing from a **dry plus wet-only return**. Only the
  latter requires establishing the effect's wet-only parameter state before
  connecting it beside an independent dry path. Use explicit gains if requested;
  any chosen starting balance must be reported.
- Preserve unrelated feeds and state. Copy exact replaced wire identities from
  current state. `replaceExisting: true` applies only to an intended exclusive
  destination. An aggregate Snake must be disconnected/replaced as a whole;
  restore any unselected channels that shared the replaced aggregate.
- Snake wrapping changes incident wiring. Record all affected edges before
  wrapping an already connected node. Prefer native exact-wire splice/insert
  operations when they express the change without reconstruction.
- Use an isolated capability probe only for an unfamiliar or unverified bus or
  endpoint combination that the current schema/state cannot establish. Ordinary
  supported routing does not require a disconnected test graph first.

## Scope controls and verify the requested result

Resolve a volume/solo/mute request to input, output, master, Merge branch, Strip
slot or hosted parameter before selecting a tool. Set explicit values and flag
states rather than toggling. Account for selection/Q-Link/Multi Link before
writes so unrelated channels or copies are not changed. Hosted parameters use
listed IDs, layout tokens and normalized values; display units are not a linear
normalization rule. Read the controls reference when making these changes.

Verify the affected topology, widths, effective parameters/flags, preserved
neighboring routes and identities. For layout, use the paged coordinate planner/executor in layout.md: native
capability preflight, lightweight inventory, one bounded preview, atomic delta
apply and complete coordinate/semantic-wire readback. Renderer quality coverage
and actual rendered bounds remain distinct from stored anchors/sizes. MCP state alone does not
prove listening, realtime performance, native-editor visibility or DAW acceptance.
For partial failure, inspect the last confirmed state and choose a bounded
recovery; undo/redo requires fresh identities and tokens afterward.

## Deterministic Graph planning

[scripts/graph_plan.py](scripts/graph_plan.py) can generate composable offline
plans or execute exact steps through one persistent stdio connection:

```sh
python3 .agents/skills/chlora-operation/scripts/graph_plan.py --state current.json --spec recipe.json --output plan.json
python3 .agents/skills/chlora-operation/scripts/graph_plan.py --apply plan.json --socket /absolute/current-host.sock --socket-identity DEV:INO --transcript unique.jsonl --output receipt.json
```

The second form performs authorized writes. Use the socket for the verified
current Host, not a remembered PID. The helper rejects a changed initial binding,
checks schemas, stops at failure and does not replay writes. Its finite templates
are described in fastpaths; explicit native steps cover other supported Graph
operations. Planned checks are intent, not a success certificate. Standalone
Strip/session workflows use MCP directly rather than this Graph-centered planner.
