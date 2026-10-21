# Save and reuse Graph presets

Use presets for a reusable **Graph fragment**: processing state, built-ins,
selected Group closure, internal routing, and captured presentation. They are
not whole-session snapshots, Strip chain presets, mixer/pre-gain/master settings,
or arbitrary vendor program files. Consult [controls-and-plugins.md](controls-and-plugins.md)
for those separate controls and [fastpaths.md](fastpaths.md) for routing.

## Select the smallest requested fragment

`chlora_graph_save_preset(name,nodeKeys,groupIds)` requires both arrays, with a
nonempty combined selection. Use current live node keys and explicit live
Group IDs; `nodeKeys:[]` is valid when Group selection is nonempty. Selecting a
Group includes its descendants, members, and boundary routing; selecting loose
nodes does not silently include their containing Group. Native copy captures
internal wires, built-in state, plug-in chunks and supported associated
presentation. Edges to nodes outside the captured fragment do not become
external live attachments in a recalled copy. Inspect the saved preview rather
than assuming the requested list equals every captured physical node.

Recipe for “save this processing region for later”:

1. Resolve the current explicit nodes/Groups and check their internal routing.
2. Save once using that scope and the requested name. Host returns metadata
   with `presetId` and `revisionToken`; native transparent schematic thumbnail
   generation needs no WebUI screenshot or caller base64.
3. Get the preset to inspect its stored-local nodes, Groups, wires, comments,
   pins, geometry, and revision. Retain this ID for later recall. A preset saved
   successfully does not prove its external plug-ins will exist on another
   machine or accept another channel/rate configuration.

Names are user-facing text, not an identity selector. List by a bounded query
or exact known ID; do not create a duplicate just because a name matches.
Saving creates a new preset; current MCP has no rename or overwrite-content
operation. To author a changed DSP/routing version, save a new scoped fragment
and manage the old version only within the user's requested library changes.

## Library identity and revision

| Operation | Binding | Workflow |
|---|---|---|
| `chlora_graph_list_presets(query,start,count)` | None | Metadata only; count 1..64, default 32; `total,start,count,hasMore` paginate |
| `chlora_graph_get_preset(presetId,includeThumbnail)` | None | Get current revision and local preview; thumbnail omitted by default |
| `chlora_graph_save_preset` | Fresh Graph tuple | Live selection → new ID/revision/metadata; does not change live Graph topology |
| `chlora_graph_load_preset(presetId,revisionToken,x,y)` | Fresh Graph tuple | Exact revision → asynchronous native paste at signed coordinates |
| `chlora_graph_update_preset(presetId,revisionToken,layout)` | None | Update local geometry and regenerate thumbnail; returns new revision |
| `chlora_graph_delete_preset(presetId,revisionToken)` | None | Revision-guarded move to Trash; returns library metadata and deleted ID |

List rows use `id`; detailed metadata uses `presetId`. Get takes no revision
argument: it is how a caller obtains the current one. Load/update/delete
require the exact nonempty `revisionToken`. A stale rejection is a reason to
get and inspect the changed preview before forming a new request; do not
silently substitute the latest token and replay the old write. Library calls
have no arbitrary filesystem path argument.

## Recall once, or the requested number of times

Get the current preview → load with exact revision and `x,y` in native Graph
coordinates (−20000..20000) → poll the returned operation ID to success → use
its new `nodeKeys` and `groupIds` → refresh live Graph binding once and inspect
requested routing/state. `x,y` anchor the fragment placement origin; relative
captured geometry is retained unless a transient layout changes it.

A successful load creates independent live identities. The stored local IDs
never become live node keys. MultiLink relationships within a recalled fragment
are remapped to a fresh link group for that copy; do not join them to an earlier
copy by reusing the old link ID. If two copies were requested, finish and verify
the first before loading the second at its requested location with a fresh
binding. Do not recall twice as a default “verification”; it would create an
unrequested duplicate. Pending/failed/timed-out operations must not trigger a
blind second load. Plug-in load completion and copied parameters do not prove
realtime audio or complete vendor-state fidelity.

To recall only part of a stored fragment, supply **both** `presetNodeKeys` and
`presetGroupIds` using IDs from get. Their combined selection must be nonempty;
omitting both recalls the full fragment. Stored node keys are decimal local
indices and can include `"0"`; live keys cannot be substituted. Group selectors
bring their closure. Unknown local IDs are rejected, not interpreted as live
selection. Native sidecar closure can add required physical routing nodes.

## Insert a preset into an existing MAIN wire

Prefer ordinary recall when the request is to create a detached region.
For requested inline insertion, get metadata and inspect `spliceEligible` and
`spliceWidth`. Then load with `insertWire` copied from the exact current live
wire: source/destination keys, `fromRole:"main",toRole:"main"`, zero-based
`fromCh,toCh`, `isBundle`, `snakeBranch,snakeInputBranch`. This schema does not
accept `bundleWidth`; check width from current wire/preview instead. Ordinary
wires use branch zero. Sidechain insertion is unsupported by this preset API.

Native insertion requires one root Group with exactly one left and one right
boundary Fanout, sealed from existing external attachments. Boundary widths
must agree and match the target route. For a Snake aggregate, the exact branch
and every channel of the original aggregate must still exist. For ordinary
routing, the required contiguous channel band from the specified starts must
exist **without gaps** and fit both buses; one visible single-channel edge is
not enough to splice a wider preset. When no boundary width is established,
native inference stops at the first missing contiguous connection. A gap or
width mismatch is a rejection, not permission to invent feeds or resize the
preset. Do not use this path to insert loose unrelated nodes or several root
Groups. A failed native commit rolls back its publication/routing transaction;
still inspect the operation result and live state before attempting recovery.

## Geometry: transient versus persistent

Optional `layout` on load changes only the recalled fragment. `update_preset`
changes its stored geometry/revision and thumbnail. Both use stored-local IDs:
`nodes:[{nodeKey,...}]`, other categories `groups/comments/pins:[{id,...}]`.
Rows may provide only selected axes or dimensions, but require at least one
geometry field. Unknown properties, duplicate IDs, missing targets, and empty
layout are rejected. Node `w/h:0` preserves native auto-size; Group/comment
sizes must be positive. Signed x/y use native coordinates. Do not copy live
renderer bounds or CSS resize units indiscriminately into stored-local geometry.

Example workflow: get → choose a local Group ID → load with
`layout:{groups:[{id:LOCAL_GROUP,x:NEW_NATIVE_X}]}` for a one-off relocated frame.
For a persistent edit, pass that local layout to update with the current
revision → retain returned new revision → get/read back → future load uses the
new token. This is geometry editing, not preset rename or replacement of its
DSP/routing contents.

## Source and current limits

Authority: [adapter schema/validation](../../../../tools/chlora_mcp.py)
(`PRESET_*`, selector pairing, partial-layout validation),
[native capture/library adapter](../../../../apps/host/juce/ChloraMcpPresets.h),
[storage/revisions/local selection](../../../../apps/host/juce/GraphPresetStore.h)
(`preview`, `loadSelection`, `update`, `remove`),
[async live paste](../../../../apps/host/juce/MainComponent.h)
(`beginMcpPresetLoad`, `beginIsolatedGraphClipboardPaste`),
[native splice/identity isolation](../../../../apps/host/juce/PluginHostEngine.h)
(`copyAdvancedPlugins`, `commitPreparedGraphClipboard`,
`spliceAdvancedGraphGroupOnWireLocked`).

Current unsupported operations include preset rename, replacement of saved DSP
contents by update, Strip/session preset CRUD, arbitrary library path import,
and sidechain wire insertion. Current supported behavior is fragment reuse
through native save/get/load and geometry update; do not describe it as every
vendor's complete preset manager.
