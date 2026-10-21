# Arrange the Graph and simplify wiring

Use this when the request includes 整理线路, 简洁排版, fewer visible jumps,
alignment, Comments, Pins, or camera changes; also apply it while an authorized
Graph operation or test setup creates or changes nodes and wires. Keep the
affected area readable throughout. Build isolated QA graphs in source-to-sink
order with clear parallel lanes and visible jacks/owned Group boundaries from
the first node. For a current project or production Graph, preserve its
intentional arrangement outside the authorized change. Do not change signal
routes, add/remove wrappers, or alter Group membership solely for appearance.
A simpler drawing must not merge independent processors, sum channels
accidentally, or replace a sidechain.

## Choose a layout from the topology

| Shape | Arrangement decision |
|---|---|
| Serial bus | Left-to-right stages, ports near a shared horizontal axis |
| Parallel branches | Split at one point; one row per branch; gather once downstream |
| Dry/wet return | Short wet chain; dry bypass outside node bounds, Pins only if needed |
| Selected-channel processing | Dense aggregate connections around a subset processor/Stack; preserved channels remain legible |
| Repeated mono/stereo lanes | Stack if that is the requested independent processing unit; do not convert existing nodes just to reduce lines |
| Sparse or remapped channels | Ordered Bundle/PortSnake and explicit Router mapping; annotate the mapping when helpful |
| Group or nested region | Move containers and their owned contents as a unit; show boundary ports clearly |
| Feedback/sidechain | Separate return/auxiliary lane and explicit role; retain intended junctions |

Order stages from the actual directed routes, not current x coordinates. Keep
parallel branches aligned and enough room for intrinsic node dimensions. Minimize
unnecessary crossings, node obstacles and detours; intentional fanout junctions,
shared cable paths and container/member overlaps are allowed. Do not require
zero total `wireIntersections`. No fixed coordinate grid or piano layout applies.

“Fewer wires” can mean fewer *visible aggregate cables*, not fewer audio lanes.
Use existing compatible Snake/Bundle/PortSnake boundaries first. Introducing a
new wrapper changes topology and may clear incident edges: reconstruct only the
explicit affected scope, verify equivalence, and retain unrelated mappings.
Do not introduce Group/Stack conversions solely for decoration.

## Use actual renderer geometry

1. Begin with `chlora_get_capabilities({})`: require schema2, a ready renderer,
   supported plan fields/quality/projection and sufficient limits. This unbound
   native preflight establishes connected Host support; static schemas do not.
2. Request `chlora_graph_get_layout_geometry` with `detail: "nodes",
   representation: "compact", includePorts: false`. Follow every continuation
   with the same binding/projection/revision until null. Validate offsets,
   returned counts, totalItems and unique identities before planning; pages may
   shrink to fit1MiB. Inventory covers up to4096 committed objects/128 Groups.
   `items` records nodes, Group/Stack, Comment and Pin ownership. Hidden routing
   nodes have no visible footprint. Await pending loads before collecting.
3. Positions/bounds use native Graph world units, **3× world CSS**. `position`
   is the move anchor; `bodyBounds` is actual card size; `bounds` includes Snake
   extensions. Place the next anchor using its envelope-to-anchor offset as well
   as the preceding right edge and gap. Node `size:{wCss,hCss}` is stored CSS
   sizing; intrinsic controls may enlarge its actual body. Group `position` and
   `frameSize`, and Comment `position` and `size`, are stored native geometry.
   The66-unit grid/fractional cells are metadata; preserve free dragging.
4. Build a mixed plan with loose `nodes`, frame edits `groups`, boundary
   `groupPorts`, absolute saved Group origins `containers`, `comments`, `pins`
   and CSS `nodeSizes`. Container translation moves owned descendants once;
   exclude independent descendant position rows and nested moved containers.
   Hidden/attached/Stack-owned nodes and boundary ports are not independent
  moves/resizes. Stack boundary sides are fixed. Containers need a saved frame.
   A saved container frame that cannot contain its rendered contents must be
   updated before translation; preview rejects that mismatch before any write.
5. Preview once with `quality: "bounds"`, then apply its exact normalized delta
   and observed revision with `quality: "none"`. Both validate identity,
   ownership, ranges and revisions; a mixed commit adds one undo snapshot and
   does not publish audio topology. Bounds compares affected ordinary node
   envelopes against all ordinary visible obstacles, with250000 pair-test
   budget and explicit partial status. It does not score wires. `full` remains
   the default and retains global256-visible-node/512-wire and path budgets;
   a small proposal does not bypass those limits. Use full only when its
   wire-quality scope and budget are appropriate.
6. Await operations and collect fresh compact pages. Verify original requested
   anchors/sizes, effective envelopes/ownership, unchanged unrelated objects and
   semantic wire multiset including hidden routes. Scoped replies may omit
   large container descendants with explicit affected/returned/omitted counts
   and `readbackRequired`; fresh pages complete verification. Stale revisions
   require recomputation. A timeout has unknown outcome: retain transcript and
   operation ID; never blindly replay a write.

The deterministic helper provides the complete coordinate workflow:

```bash
python3 .agents/skills/chlora-operation/scripts/graph_layout.py collect --socket /absolute/verified.sock --socket-identity DEVICE:INODE --transcript collect.jsonl --output inventory.json
python3 .agents/skills/chlora-operation/scripts/graph_layout.py plan --inventory inventory.json --spec spec.json --output plan.json
python3 .agents/skills/chlora-operation/scripts/graph_layout.py execute --socket /absolute/verified.sock --socket-identity DEVICE:INODE --transcript execute.jsonl --plan plan.json --output result.json
```

Derive DEVICE:INODE from the verified intended Host socket; do not pick the
newest socket or create a session automatically. Use new output/transcript paths.
`spec.json` supports `row` with nodeKeys/origin/gap, `parallel` with explicit
lanes and rowGap, visible MAIN DAG `topology` with complete semantic state,
or `explicit` with a mixed layout. Cycles, sidechains, dependent/owned nodes
and ambiguous layouts need an explicit plan. Finite planners do not establish
optimal readability for arbitrary graphs. The helper keeps one stdio connection,
validates complete pagination and readback, and preserves audit evidence. A truncated pure-container preview can be
projected from complete before geometry and checked after apply; a truncated
nonlinear mixed resize/relative edit stops before writing and needs a smaller
proposal. Independent card sizing applies to plugin nodes, including internal
processors; fixed built-in routing modules keep their intrinsic sizing.

`chlora_graph_align_ports` aligns current port descriptors to a reference on
x or y; request ports explicitly and use rendered ordinals0..255, distinct
from Snake branch indices0..63. `chlora_graph_set_group_port_position` places one current boundary port
on its side; both use the observed renderer revision. Topology-level
`chlora_graph_move_group_fanout` updates the native boundary position without
that renderer API. Keep Stack left/right boundary alignment where helpful;
do not invent extra Stack boundary Fanouts.

## Pins, Comments and exact presentation scope

Pins bend one exact visible wire. `chlora_graph_add_cable_pin` needs live endpoint
keys, channels, destination role, and for an aggregate the width and both branch
numbers. Keep returned `pinId`; move/remove with `chlora_graph_move_cable_pin` /
`chlora_graph_remove_cable_pin`. Set `curve` or `straight` using
`chlora_graph_set_wire_style` on the same exact identity. Re-read after topology
changes, since a former wire/pin identity may no longer exist.

Use `chlora_graph_create_comment`, `chlora_graph_set_comment_text`,
`chlora_graph_move_comment`, `chlora_graph_resize_comment` and
`chlora_graph_remove_comment` for independent annotations. A Comment can label a
branch or encompass a region; keep its header/control affordances away from
processor controls. `chlora_graph_set_group_comment` edits a Group's title.
Stack labels are not a routing operation; use a separate Comment if the desired
annotation is not rendered on that container. Optional `parentGroupId` attaches
an annotation to an allowed ordinary Group; do not assume Stack nesting support.

For mixed removal, `chlora_graph_delete_selection` takes explicit nodeKeys,
groupIds, commentIds and exact wires (unused arrays empty). Group removal and
node deletion have different native semantics; inspect membership/owned routes
before choosing a cleanup operation. Never delete an audio node to remove its
annotation. `move_selection` shifts nodeKeys and optionally one Comment by a
delta; container moves use Group tools.

## Camera and display preferences

`chlora_graph_get_view_preferences`, `chlora_graph_set_viewport`,
`chlora_graph_set_spatial_meter`, `chlora_graph_set_cable_dead_zone` and
`chlora_graph_set_stack_names` operate through the visible Graph WebUI and are
asynchronous. Read back the preference after polling. Stack Names requires the
incoming channel identity; see nodes.md. Spatial meters require an available
speaker layout on that side. Camera pan is in CSS units, separate from node
native coordinates; `(zoomScale: 0.7, panX: 0, panY: 0)` resets the view to 100%.
Preserve the camera during unrelated edits; frame/reset only as requested or
when needed to show the result. Keep the changed path within a readable viewport
when the authorized operation permits it, and read back any camera change.

Visual quality and unchanged semantic routing are separate checks. Inspect the
rendered result when available; stored anchors, sizes, counts and metrics do not
prove actual cable readability. If geometry omits an owned/attached visible
endpoint or jack, use an already-authorized rendered UI/fallback inspection
path; otherwise record that exact element as unverified. Do not invent ports or
detach an owner to make it appear covered.
