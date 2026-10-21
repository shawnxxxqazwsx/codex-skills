# Discover exact Chlora MCP tools

The current connection's schemas and Host validation are authoritative. This
reference routes operations instead of copying the full tool catalog, which
can drift from the implementation.

Before coordinate layout, call unbound `chlora_get_capabilities({})` to check
the native Host version, renderer readiness, supported mixed plan fields,
quality modes and limits. A ready retained renderer can answer geometry while
hidden. Canonical compact geometry uses structuredContent once and a short
text summary; read the structured result for complete coordinates.

## Full and compact clients

In a full profile, use `tools/list` once and cache the needed input schemas.
The compact profile retains common state/Graph summary/plugin search/catalog/
operation reads directly and offers these helpers for the remaining surface:

1. `chlora_discover_tools` when the action name is unknown; inspect its schema
   for supported filtering rather than guessing arguments.
2. `chlora_describe_tool({"action":"chlora_..."})` for the exact input schema.
3. `chlora_invoke({"action":"chlora_...","arguments":{...}})` to execute.

Use the exact `chlora_...` action names in the workflow references. Bound reads
also need their schema's binding tuple. Do not treat tool count or a truncated
compact list as a missing native capability. Conversely, a native UI feature
without a published tool remains unsupported through MCP.

When no connector is exposed, the repository adapter `tools/chlora_mcp.py`
supports stdio with `--socket /absolute/current-host.sock --profile full`.
Bind the socket to the verified current Host/process/session and preserve its
filesystem identity; stale sockets can survive another Host run. The Graph
helper's persistent client handles initialization, schema caching and a unique
transcript. Don't start another MCP process per write.

## Operation owners

- Builtin entities and connection semantics: [nodes.md](nodes.md).
- Serial/parallel/subset/Stack compositions: [fastpaths.md](fastpaths.md).
- Sidechain, reordering and mixed buses: [graph-recipes.md](graph-recipes.md).
- Gain, Solo/Mute, hosted node/slot bypass and parameter controls: [controls-and-plugins.md](controls-and-plugins.md).
- Preset/library revision and stored/live identities: [presets.md](presets.md).
- Renderer geometry, wire Pins and view settings: [layout.md](layout.md).

## Session, format and service controls

`chlora_open_session`, `chlora_select_session`, `chlora_close_session` operate on
explicit current IDs/binding. Open/select requires a fresh binding before writes.
A session depends on a connected Chloe producer; opening without one may retire
it. Closing persists that session and stops Host processing. After a timeout,
inspect state before assuming success or retrying.

`chlora_set_mode` ordinarily retains compatible setup. `allowPluginLoss: true`
can discard processing/undo history: use only within an explicit discard request.
`chlora_clear_all` requires `confirm: "clear"` and an intended session reset.
Neither is needed for routine layout, preset recall or parameter changes.

`chlora_set_channel_layout`, `chlora_set_speaker_adaptation`,
`chlora_set_insert_channels`, `chlora_set_output_channels`,
`chlora_set_input_channel_name` and `chlora_reset_input_channel_names` require
current layout tokens. Multi Mono locks Insert to Output; a linked Bridge can
republish Output width. Read effective subsequent layout/width before routing.

Meter mode, worker count, performance maximum reset, Host zoom and dismissing a
failed-load notice are session controls. Consult schemas for exact targets/ranges;
read `maxWorkerThreads` and match the current load ID. New processing samples can
immediately increase a reset maximum. Native-editor open replies only queue a
request; inspect a visible window if visibility is part of acceptance.

For plugin browser grouping/favorites/preferred channel widths, resolve catalog
UID first and set explicit desired states. Search cached catalog before scanning;
scan only when discovery requires it, await scanning false, then resolve again.
Exact local VST3 file loading can bypass a missing catalog UID, but must be polled.

`chlora_get_host_preferences` / `chlora_set_host_preferences` are global and use
`preferencesToken`, not a session binding. Preserve unrelated fields; per-session
Graph camera and display controls are in layout.md. Undo/redo accepts history
operations, not an instant restoration guarantee; refresh identities afterward.
