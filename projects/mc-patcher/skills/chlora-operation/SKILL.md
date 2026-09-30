---
name: chlora-operation
description: Operate a running Chlora session through MCP for Graph routing, Strip slots, mixer controls, and hosted plug-in parameters.
---

# Chlora MCP operation

Use this skill when an AI must inspect or change a running Chlora Host
through MCP. The MCP client is the control plane; do not infer support
from native UI controls. Read [graph-recipes.md](references/graph-recipes.md)
for topology recipes.

If the client exposes only eight Chlora tools, it is using the compact profile:
five direct reads and three discovery/invocation helpers.
The common reads `chlora_get_state`, `chlora_graph_get_summary`,
`chlora_find_plugins`, `chlora_list_plugins`, and `chlora_get_operation` remain
direct. For every other operation named below or in the references, call
`chlora_discover_tools` if the name is unknown, then
`chlora_describe_tool({"action": "chlora_..."})` for its exact schema, and
`chlora_invoke({"action": "chlora_...", "arguments": {...}})` to execute it.
The action name, argument rules, Host validation, and returned state are the
same as in the full profile. This lets a small model load only the schemas it
needs while retaining the complete control surface.

## Operating rules

1. Begin with `chlora_get_state`. In Graph mode, use
   `chlora_graph_get_summary` for later planning reads. Keep `activeInstanceId`
   as the tool's `instanceId`, plus `bindingGeneration`, graph topology/lifetime
   tokens, mode, and stable node keys. Use `chlora_find_plugins` to resolve an
   exact `uid` before a load; `chlora_list_plugins` also reports scan state.
   If the installed plug-in is absent from the cached catalog, use
   `chlora_rescan_plugins` only when a catalog scan is intended, then poll
   `chlora_list_plugins` until `scanning` is false and search again. If the
   exact installed VST3 path is known, `chlora_graph_add_plugin_file`,
   `chlora_graph_load_stack_file`, or `chlora_strip_load_plugin_file` can
   inspect and load that absolute local `.vst3` path without a catalog UID.
   For a Graph node supply `channels`, `x`, and `y`; for Strip supply
   `channel`, `slotIndex`, `channels`, and `start`; for an empty Stack supply
   its `groupId` and use its configured lane widths. Poll the returned
   operation ID; a queued file inspection is not proof of a loaded plug-in.
2. Use the fresh binding tuple in each synchronous write's returned state.
   After an asynchronous load, read state again. Slot indices can shift after
   insert/remove/move; node keys and graph tokens must be rediscovered after
   undo/redo or restore. Every bound `chlora_graph_*` call, including read-only
   parameter listing and layout inspection, needs the complete four-field
   tuple: `instanceId`, `bindingGeneration`, `graphTopology`, and
   `graphLifetime`. `chlora_graph_get_summary` is the no-argument exception
   and returns a fresh tuple. Preserve the last two as decimal JSON strings,
   never convert them to numbers. Refresh the tuple after each Graph mutation.
3. Poll `chlora_get_operation` for asynchronous plug-in loads and layout work.
   Do not issue another write while the host reports a pending load/layout.
4. Hosted parameter values are normalized `0..1`. Always use the exact
   `parameterId` and `parameterLayout` returned by the matching list call.
   Re-list after a stale-layout response. Meter and non-automatable parameters
   are read-only. A sandboxed parameter's `text: "..."` means vendor display
   formatting is still pending; re-list before interpreting its units or
   proving a wet-only setting.
   To show a Graph plug-in control on its node, call
   `chlora_graph_expose_parameter` with the listed ID and current layout token;
   read back `exposedId` and the node's exposed controls. Remove it by that
   exposed ID. There is no need to touch the native editor for this path.
5. Build multi-step procedures as individually checked writes. MCP does not
   make a recipe atomic. Read back state and use `chlora_undo` when a bounded
   recovery is appropriate; after undo/redo, rediscover identities and tokens.
6. Keep claims bounded: this skill does not establish realtime audition,
   complete DAW compatibility, AU behavior, or live deployment success.
7. Before changing an existing route, identify the exact affected wires and
   branch roles from the current state. A Group, Stack, or visual position does
   not imply an audio connection. Keep unrelated member identities and routes.
   For a requested exclusive destination, use `replaceExisting: true` on the
   exact channel, bus, or Snake connection and read back that no extra feed
   remains. This also clears extra feeds when the desired edge already exists.
   A channel or bus replacement cannot cut through an aggregate Snake branch;
   replace or disconnect that whole branch first, then use the exact channel
   or bus tool if needed. Connect and disconnect logical aggregate branches
   with the Snake tools, not with a single channel call. An ordinary extra
   channel feed beside a Snake branch can still be disconnected individually.
8. For requested fader or knob changes, first determine whether the control is
   a Chlora mixer value, a Merge branch gain, or a hosted plug-in parameter.
   Use the corresponding tool. Do not guess a normalized plug-in value from a
   displayed dB, frequency, or percentage without reading its parameter
   descriptor and checking the resulting readback.
9. `chlora_open_session` takes a Chloe instance ID from 1 to 64. After opening
   or selecting it, refresh `bindingGeneration` before any write. Close only
   the session whose ID and binding still match the user's request; closing
   persists that session and stops its Host processing. A live Chloe producer
   must hold that instance ID for the session to remain mounted. If no Chloe
   is connected, the Host can retire a newly opened session; after any timeout,
   read `chlora_get_state` before retrying or assuming the session exists.
10. Channel layout, speaker adaptation, and input-name writes require the
    current `channelLayoutToken` from full state. A layout change can invalidate
    that token, so read state again before the next layout-dependent write.
    `chlora_set_insert_channels` and `chlora_set_output_channels` set exact bus
    widths using the same token. Multi Mono locks Insert to Output; a linked
    Chloe Bridge can republish its Output width, so verify subsequent state.
11. For Q-Link, set the exact selection first with
    `chlora_set_selected_channels` (MonoLink) or `chlora_set_selected_slots`
    (Multichannel Strip), then set automatic sync if requested. Both selection
    tools require a focus member and return the resulting selection. Do not
    infer Q-Link targets from a prior UI selection. For a one-time chunk copy,
    call `chlora_strip_sync_qlink_state` only after the source slot/lane and
    selected compatible targets are explicit; inspect target parameters and
    do not claim full chunk equality from the MCP reply alone.
12. For Graph cleanup, use `chlora_graph_move_selection` to move stable node
    keys plus an optional Comment by one native-coordinate delta. Use
    `chlora_graph_delete_selection` for a mixed selection: pass `nodeKeys`,
    `groupIds`, `commentIds`, and `wires` arrays, leaving unused arrays empty.
    Copy each selected visible wire's exact endpoint/role/channel fields from
    `chlora_graph_get_summary`; bundle wires also need width and both branch
    fields. Refresh Graph state after deletion because node indices and
    topology change. Check the result before further edits.
13. Meter display, worker count, performance maximum reset, and Host zoom are
    session-bound controls. Read `maxWorkerThreads` before changing the worker
    count. A maximum reset may be followed immediately by new audio samples.
    Dismiss a load notice only when state shows a completed error and its
    `loadId` still belongs to the current session.
14. Resolve a cached plug-in UID before setting its favorite state. Use
    `chlora_set_plugin_favorite` with explicit `on` so retries do not toggle
    the opposite state. `chlora_set_plugin_grouping` changes browser grouping;
    both calls return the updated catalog.
15. Graph camera, spatial meter display, and cable drag dead zone are WebUI
    preferences. Use `chlora_graph_get_view_preferences` to read them, then
    `chlora_graph_set_viewport`, `chlora_graph_set_spatial_meter`, or
    `chlora_graph_set_cable_dead_zone` with the fresh Graph binding. Poll each
    operation ID and read back the preference. These calls require an open,
    visible Graph WebUI. A spatial meter can be enabled only when that side has
    an available speaker layout. Camera changes do not change audio routing;
    `(zoomScale: 0.7, panX: 0, panY: 0)` resets the view to 100%.
16. For a live route, prove the least familiar connection on disconnected
    nodes before replacing IN-to-OUT continuity. In particular, connect one
    attached Port Snake to its intended aggregate peer and inspect the actual
    `isBundle`/width readback before creating a large sidecar partition. If a
    preflight fails, restore the original route before source investigation.
    Use each write's returned state as the next binding; avoid a separate
    summary both before and after every deterministic write. Re-read summary
    after asynchronous work, stale binding, ambiguous structure, or when a
    specific readback is absent from the write result. Prefer the documented
    tool schema and this skill to repeated source searches during a live edit.

## Surface routing

Use the state/session/mixer tools for session opening, selection, closing,
mode changes, Insert/Output width, channel layout, speaker adaptation, input
channel names, exact selection, Q-Link automatic sync, bypass,
pre/master/channel gain, input/output channel mute/solo, undo, and redo.
`chlora_clear_channel_flags` clears all active input or output mute/solo flags
when the user requests a full reset of that flag.
Meter mode, worker count, performance reset, zoom, and failed-load notice
controls use the same session binding. Strip
operations cover exact slot load, remove, move, bypass, span, layer, and
Strip/MonoLink parameter inventory and writes. Strip input and post-insert
channel maps use exact edges; `chlora_strip_set_route` preserves other edges
feeding the same destination. Graph operations cover plug-in and builtin
creation, exact MAIN and SIDECHAIN bus routing, Bundle packing,
Snake and Merge editing, Router crosspoints, Stack creation and loading, Group
Fanout creation and supported-width connection, Port Snake creation, Multi Link,
cable Pins, comments, layout, and Graph parameters. Keep
Strip channel `-1` for a shared Multichannel slot and provide an explicit lane
for a MonoLink slot.

Before loading repeated plug-ins in Graph, choose the user's processing unit.
If one stereo plug-in should process several adjacent stereo channel pairs as
one named channel group, create a Plugin Stack with `count` equal to the pair
count and `width: 2`. A Stack loads one independent plug-in instance per lane;
it does not turn a stereo plug-in into a multichannel processor. Prefer this
over loose identical nodes when the pairs share a purpose and parameter law.
Use a regular Group only for an explicitly requested visual or routing boundary
around unlike nodes. For 9.1.6 ITU, verify the current channel names before
assuming the six height channels are zero-based 10..15; three stereo lanes
then represent FTL/FTR, MTL/MTR, RTL/RTR. Read
[graph-recipes.md](references/graph-recipes.md) for this Stack route. Do not
plan six-channel routing as three separate cables merely because the plug-in
itself is stereo.

For a route request, first decide whether each path is a one-channel MAIN edge,
a contiguous bus, a SIDECHAIN feed, a sparse Bundle, or a Snake branch. Choose
the matching MCP tool and use the exact zero-based endpoints. A parallel effect
needs separate dry and wet branches, an explicit Fanout after Graph IN's
single compact Snake output, and an explicit Merge. Do not create a second
Graph IN Snake output merely to split the signal. Confirm the
processor's return is wet-only from its parameter descriptor and readback
before connecting it beside an independent dry branch. If wet-only behavior
cannot be established, leave that routing goal unresolved. A serial per-channel
chain needs one plug-in node per channel unless the requested plug-in and layout
support the declared multichannel width. Read back every edge and parameter
after the sequence; the current tool set does not offer a single atomic recipe.

`chlora_strip_open_editor` and `chlora_graph_open_editor` request one native
plug-in editor. Their replies confirm only that the request was queued;
verify the visible window separately if that is part of the task.
`chlora_clear_all` removes the active processing
setup and requires `confirm: "clear"`; use it only when the user asks to clear
that session. `chlora_set_mode` defaults to retaining plug-ins and routing. A
destructive conversion needs
`allowPluginLoss: true`, which may clear undo history; use it only after the
user explicitly asks to discard the current setup. Open or select the intended
session before writing. Do not substitute a visually similar Graph construction
for an unsupported operation.
Read [the MCP tool reference](references/mcp-tool-reference.md) when an exact
argument range or current feature boundary matters.
