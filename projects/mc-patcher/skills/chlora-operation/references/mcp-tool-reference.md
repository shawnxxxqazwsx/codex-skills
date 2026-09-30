# Chlora MCP

Chlora MCP lets an MCP client inspect and control a running Chlora Host through
a local-only Unix socket. The Python adapter uses only the Python standard
library. It does not start Chlora or expose a general command interface.
Catalog scans and VST3 file loads run inside the bound Chlora Host when their
explicit MCP tools are called.

## Enable the Host service

In Chlora, **View > MCP Control** enables or disables the service. It is enabled
by default. Disable it there when local AI control is not wanted.

Each Chlora process listens on:

```text
/tmp/chlora-mcp-<uid>/host-<pid>.sock
```

The directory is owned by the current user with mode `0700`; the socket is
owned by the current user with mode `0600`. The adapter rejects sockets or
parent directories that do not have those ownership and permission properties.
The transport is local Unix IPC and does not open a TCP port.

## MCP client configuration

Use the adapter's absolute path in the MCP client's server configuration. This
is a generic `mcpServers` example; configure it in the client of your choice:

```json
{
  "mcpServers": {
    "chlora": {
      "command": "python3",
      "args": [
        "/absolute/path/to/mc-patcher/tools/chlora_mcp.py"
      ]
    }
  }
}
```

The adapter automatically connects only when exactly one live
`host-*.sock` is discoverable. It pins that socket path and filesystem identity
for the lifetime of the MCP subprocess. If that Host exits, restarts, disables
and re-enables MCP Control, or replaces its endpoint, calls continue to fail
against the original target instead of silently moving to another Host. Restart
the MCP client or its Chlora server subprocess to discover the new endpoint.

If more than one Chlora Host is running, pin the intended process explicitly:

```json
{
  "mcpServers": {
    "chlora": {
      "command": "python3",
      "args": [
        "/absolute/path/to/mc-patcher/tools/chlora_mcp.py",
        "--socket",
        "/tmp/chlora-mcp-<uid>/host-<pid>.sock"
      ]
    }
  }
}
```

Replace the UID and PID with the values on the current machine. List candidate
processes without entering MCP server mode:

```bash
python3 /absolute/path/to/mc-patcher/tools/chlora_mcp.py --list-hosts
```

This prints one JSON object to stdout. In MCP server mode stdout is reserved
exclusively for newline-delimited JSON-RPC messages; diagnostics go to stderr.

### Compact profile for a small model

The default `full` profile advertises all 143 individual tools. For a client
using a smaller model, add `--profile compact` to the adapter arguments:

```json
{
  "mcpServers": {
    "chlora": {
      "command": "python3",
      "args": [
        "/absolute/path/to/mc-patcher/tools/chlora_mcp.py",
        "--profile", "compact"
      ]
    }
  }
}
```

This profile advertises eight tools instead of 143. Five common reads remain
direct: `chlora_get_state`, `chlora_graph_get_summary`,
`chlora_find_plugins`, `chlora_list_plugins`, and `chlora_get_operation`.
Use `chlora_discover_tools` with a short query and optional `family` to find
another operation, then `chlora_describe_tool` to get its exact schema. Call
`chlora_invoke` with that `action` name and its `arguments`. The adapter checks
the same schema and sends the same Host request as the full profile; compact
mode does not remove any operation. Discovery and description are local reads
and do not require a connected Host. A client must restart its MCP server
process after changing the profile.
The compact dispatch path is verified against the adapter's private fake Host.
A Luna conversation also built two mono serial chains and a stereo dry/wet
reverb topology through an isolated built Host and synthetic Chloe session.
The deployed Desktop Host and audio/DAW paths remain unverified for this work.

Sandboxed plug-in parameter values are normalized to 0..1. The worker supplies
the plug-in's formatted display text asynchronously; an initial `"..."` means
that text is not ready, so re-list the parameter before interpreting its unit
or control direction. A displayed value alone may still be insufficient to
establish a wet-only return.
Parameter category metadata is preserved so meter parameters remain read-only.
After undo/redo, rediscover node keys and graph tokens from state. Plugin state
restoration may temporarily exceed the read timeout; retry only a read after
waiting, and never replay a timed-out write without first checking its outcome.

## Exposed tools

The default adapter advertises 143 tools; the compact profile advertises eight
entry points for the same operations. The table describes the supported
MCP contract; a native UI action is not automatically available through MCP.

| Tool | Arguments | Result |
|---|---|---|
| `chlora_get_state` | `{}` | Complete active state, including session identity and binding generation |
| `chlora_list_plugins` | `{}` | Cached plug-in catalog; does not start a scan |
| `chlora_rescan_plugins` | `scope` (`new` or `full`) | Start catalog scan; poll `chlora_list_plugins` until `scanning` is false |
| `chlora_find_plugins` | `query`, optional `limit` | Compact cached catalog matches with exact plug-in UIDs; a current Host filters locally without sending the full catalog |
| `chlora_graph_get_summary` | `{}` | Compact Graph bindings, nodes, wires, Group Fanout sides, Comments, and pending-load status |
| `chlora_select_session` | `instanceId` | Complete state after selecting an existing session |
| `chlora_open_session` | Chloe `instanceId` (1..64) | Open or select a session and return its active state; a live Chloe producer must hold the ID or the Host can retire it |
| `chlora_close_session` | session binding | Persist and close only the bound active session |
| `chlora_clear_all` | session binding, `confirm: "clear"` | Clear the session's plug-ins and processing, then return updated state and `changed` |
| `chlora_close_editors` | session binding | Close native plug-in editor windows without changing audio routing |
| `chlora_set_meter_mode` | session binding, `target` (`mixer` or `master`), `mode` (`peak` or `rms`) | Set meter display mode and return state |
| `chlora_set_worker_threads` | session binding, `threads` (1..current `maxWorkerThreads`) | Set the Host worker pool size; state exposes the applied count and limit |
| `chlora_reset_perf_max` | session binding | Reset measured maximum processing time; active audio may raise it immediately |
| `chlora_set_zoom` | session binding, `percent` (75, 100, 125, 150, or 175) | Change Host UI scale and return `zoomPct` |
| `chlora_dismiss_failed_load` | session binding, failed Graph/Strip `loadId` from state | Dismiss only a completed failure notice bound to this session |
| `chlora_set_plugin_grouping` | session binding, `groupBy` (`vendor` or `channels`) | Set browser grouping and return the refreshed catalog |
| `chlora_set_plugin_favorite` | session binding, exact cached `pluginUid`, `on` | Idempotently update favorites and return the refreshed catalog |
| `chlora_set_plugin_preferred_channels` | session binding, exact cached `pluginUid`, verified `channels` (1..128), or `0` to clear | Remember a plug-in browser width before loading; returns the refreshed catalog |
| `chlora_clear_channel_flags` | session binding, `scope` (`input` or `output`), `flag` (`mute` or `solo`) | Clear all active matching channel flags in one undoable edit |
| `chlora_set_mode` | session binding, `mode` (`graph`, `multiChannel`, or `multiMono`), optional `allowPluginLoss` | Switch modes; a conversion that discards plug-ins/routing requires an explicit `allowPluginLoss: true` and may clear undo history |
| `chlora_set_channel_layout` | session binding, `channelLayoutToken`, `mode` (`native`, `unified`, `immersive`, or `auro`) | Set channel layout policy and return updated state |
| `chlora_set_insert_channels`, `chlora_set_output_channels` | session binding, `channelLayoutToken`, exact `channels` (1..128) | Set Insert or Output width and return actual updated state |
| `chlora_set_speaker_adaptation` | session binding, `channelLayoutToken`, `enabled` | Set hosted plug-in speaker adaptation |
| `chlora_set_qlink_auto_sync` | session binding, `on` | Enable or disable Strip Q-Link state propagation for the current selection |
| `chlora_set_selected_channels` | session binding, unique zero-based `channels`, member `focusChannel` | Select exact mixer lanes and MonoLink Q-Link targets |
| `chlora_set_selected_slots` | session binding, unique zero-based `slotIndices`, member `focusSlot` | Select exact Multi Channel Strip Q-Link slots |
| `chlora_set_input_channel_name`, `chlora_reset_input_channel_names` | session binding and `channelLayoutToken`; set also takes `channel` and `text` | Set/clear custom input channel names |
| `chlora_set_bypass` | `instanceId`, `bindingGeneration`, `on` | Complete updated state |
| `chlora_set_master_gain` | `instanceId`, `bindingGeneration`, `gainDb` | Complete updated state |
| `chlora_set_pre_gain` | session binding, `gainDb` (-30..30) | Complete updated state |
| `chlora_set_channel_gain` | `instanceId`, `bindingGeneration`, `channel`, `gainDb` | Complete updated state |
| `chlora_set_channel_mute` | `instanceId`, `bindingGeneration`, `channel`, `on` | Complete updated state |
| `chlora_set_channel_solo` | `instanceId`, `bindingGeneration`, `channel`, `on` | Complete updated state |
| `chlora_set_input_mute`, `chlora_set_input_solo` | session binding, zero-based `channel`, `on` | Complete updated state |
| `chlora_undo` | `instanceId`, `bindingGeneration` | Full state after the undo request is accepted |
| `chlora_redo` | `instanceId`, `bindingGeneration` | Full state after the redo request is accepted |
| `chlora_strip_load_plugin` | session binding, `channel`, `slotIndex`, `pluginUid`, `channels`, `start`, optional `replace`, `layer` | Pending operation; terminal result has committed slot index |
| `chlora_strip_load_plugin_file` | session binding, `channel`, `slotIndex`, absolute local `.vst3` `pluginPath`, `channels`, `start`, optional `replace`, `layer` | Pending file inspection and isolated load; terminal result has committed slot index |
| `chlora_strip_remove_plugin`, `chlora_strip_move_plugin` | session binding, `channel`, `slotIndex`; move also takes `toSlotIndex` | Complete updated state |
| `chlora_strip_set_bypass` | session binding, `channel`, `slotIndex`, `on` | Complete updated state |
| `chlora_strip_retry_worker` | session binding, exact `channel` and `slotIndex`, decimal-string `workerToken` and `workerRevision` from state | Request retry only if the same isolated worker and health revision remain current |
| `chlora_strip_set_span` | session binding, `channel: -1`, `slotIndex`, `start`, `channels` | Exact processed shared Strip span or error |
| `chlora_strip_set_layer` | session binding, `channel: -1`, `slotIndex`, `layer` | Complete updated state |
| `chlora_strip_list_parameters` | session binding, `channel`, `slotIndex`, optional `start`, `count` | Parameter descriptors, layout token and pagination |
| `chlora_strip_open_editor` | session binding, exact `channel` and `slotIndex` | Request one shared or MonoLink lane editor; the reply does not prove a window opened |
| `chlora_strip_sync_qlink_state` | session binding, focused selected source `channel` and `slotIndex` | Copy source plug-in state to the currently selected compatible Q-Link targets |
| `chlora_strip_set_parameter` | session binding, `channel`, `slotIndex`, `parameterId`, `parameterLayout`, `value` | Complete updated state |
| `chlora_strip_set_route` | session binding, `stage` (`input` or `post`), zero-based `src`, `dst`, `on` | Add/remove one exact Strip map edge while retaining other fan-in and fan-out routes |
| `chlora_strip_clear_route_destination` | session binding, `stage`, zero-based `dst` | Remove every edge feeding one destination |
| `chlora_strip_reset_routes`, `chlora_strip_clear_routes` | session binding, `stage` (`input`, `post`, or `both`) | Reset selected maps to identity or clear them to silence |
| `chlora_graph_add_plugin` | graph binding, `pluginUid`, `channels`, `x`, `y` | `{operationId,status:"pending"}` |
| `chlora_graph_add_plugin_file` | graph binding, absolute local `.vst3` `pluginPath`, `channels`, `x`, `y` | Pending file inspection and isolated load; terminal result has stable `nodeKey` |
| `chlora_graph_copy_plugins` | graph binding, 1..256 stable ordinary plug-in `nodeKeys` | Copy plug-in states into Chlora's Graph clipboard; result includes copied count |
| `chlora_graph_paste_plugins` | graph binding, native Graph `x`, `y` | Pending isolated paste; terminal result includes new stable `nodeKeys` |
| `chlora_graph_duplicate_plugins` | graph binding, 1..256 stable ordinary plug-in `nodeKeys` | Pending isolated duplicate with native placement offset; terminal result includes new stable `nodeKeys` |
| `chlora_get_operation` | `operationId` | `{operationId,status,error?,nodeKey?,instanceId}` |
| `chlora_graph_add_merge` | graph binding, `channels`, `inputs`, `x`, `y` | Full state; `mcpResult.nodeKey` identifies the new merge |
| `chlora_graph_create_stack`, `chlora_graph_configure_stack`, `chlora_graph_unload_stack` | graph binding; lane `count`, `width` (1 or 2), position for creation; stable `groupId` for configuration/unload | Create and resize an empty Stack, or unload its members while retaining its boundary |
| `chlora_graph_load_stack` | graph binding, empty Stack `groupId`, exact `pluginUid` | Pending operation; prepares and loads one plug-in instance per Stack lane |
| `chlora_graph_load_stack_file` | graph binding, empty Stack `groupId`, absolute local `.vst3` `pluginPath` | Pending file inspection and isolated load of one instance per Stack lane |
| `chlora_graph_split_stack_lane` | graph binding, Stack `groupId`, zero-based stereo `row` | Operation envelope; splits into two mono rows, copying loaded plug-in state when present |
| `chlora_graph_add_builtin` | graph binding, `kind` (`bundle`, `fanout`, `router`), optional `channels`, `x`, `y` | Full state with stable `mcpResult.nodeKey` |
| `chlora_graph_insert_builtin_on_wire` | graph binding, `kind` (`bundle`, `merge`, `fanout`, `router`), exact visible MAIN source/destination node keys and channels, `isBundle`, `channelCount`, branches, `x`, `y` | Atomically insert a new builtin composition on that wire; return stable primary `nodeKey` |
| `chlora_graph_splice_existing_builtin` | graph binding, detached builtin `nodeKey`, exact visible MAIN wire identity, `channelCount`, `x`, `y` | Atomically splice the existing builtin while preserving its stable identity and state |
| `chlora_graph_create_port_snake` | graph binding, compatible `ownerNodeKey`, `direction` (`input` or `output`), unique MAIN `channels`, `x`, `y` | Create an explicit Port Snake and return its stable `mcpResult.nodeKey` |
| `chlora_graph_set_snake` | graph binding, `nodeKey`, `wrapped` | Full state with `mcpResult.changed` and `nodeKey` |
| `chlora_graph_add_snake_output` | graph binding, `nodeKey` | Full state with mutation detail |
| `chlora_graph_add_snake_input`, `chlora_graph_remove_snake_branch` | graph binding, `nodeKey`; removal also needs `branch` | Full state with mutation detail |
| `chlora_graph_splice_node` | graph binding, `nodeKey`, `sourceNodeKey`, `destinationNodeKey`, zero-based `sourceChannel` / `destinationChannel` | Atomically insert a detached ordinary plugin into the selected MAIN wire range |
| `chlora_graph_detach_node` | graph binding, `nodeKey` | Bypass and detach an ordinary plugin, retaining it on the canvas |
| `chlora_graph_connect_snake` | graph binding, source/destination node keys and branches, optional `replaceExisting` | Full state with mutation detail |
| `chlora_graph_connect_group_fanout` | graph binding, attached boundary/ordinary source and destination keys, optional `replaceExisting` | Connect a Group boundary at its supported width without collapsing its Fanout identity |
| `chlora_graph_disconnect_snake` | graph binding, source/destination node keys and branches | Full state with mutation detail |
| `chlora_graph_connect_channel`, `chlora_graph_disconnect_channel` | graph binding, source/destination node keys and zero-based MAIN channels; connect optionally accepts `replaceExisting` | One exact channel route changed, or a no-op |
| `chlora_graph_connect_bus` | graph binding, source/destination node keys, zero-based channel offsets, `channels`, optional `destinationRole` (`main` or `sidechain`) and `replaceExisting` | Atomically connect the contiguous bus range or leave every lane unchanged |
| `chlora_graph_bundle_append_channels` | graph binding, Pack `bundleNodeKey`, `sourceNodeKey`, unique MAIN `channels` | Append sparse outputs as dense Bundle lanes |
| `chlora_graph_bundle_connect` | graph binding, populated Pack `sourceNodeKey`, empty Bundle `destinationNodeKey` | Connect one aggregate Pack-to-Unpack strap |
| `chlora_graph_bundle_fanout` | graph binding, Unpack `bundleNodeKey`, destination node key and first channel, optional role and replacement flag | Atomically fan every dense lane to MAIN or SIDECHAIN inputs |
| `chlora_graph_add_cable_pin`, `chlora_graph_move_cable_pin`, `chlora_graph_remove_cable_pin` | graph binding; exact wire endpoint keys/role/channels for creation, persistent `pinId` for move/remove | Create, reposition or remove a cable bend Pin |
| `chlora_graph_set_wire_style` | graph binding, exact visible cable identity and `style` (`curve` or `straight`) | Persist a visual wire route style without changing audio routing |
| `chlora_graph_set_multi_link` | graph binding, unique ordinary plug-in `nodeKeys`, `unlink` | Link compatible plug-in instances by parameter layout or remove their link memberships |
| `chlora_graph_set_sync_selection` | graph binding, unique ordinary plug-in `nodeKeys` (empty clears) | Set transient Graph parameter-sync selection; read back `graphSyncSelection` |
| `chlora_graph_add_group_fanout` | graph binding, regular `groupId`, boundary `side`, normalized `position`, branch count | Add an explicit regular Group boundary port; Stacks retain their fixed pair |
| `chlora_graph_move_group_fanout` | graph binding, Group or Stack `groupId`, stable Fanout `nodeKey`, normalized `position` | Move an existing boundary port along its fixed side |
| `chlora_graph_set_merge_gain` | graph binding, `nodeKey`, `branch`, `gainDb` | Full state with mutation detail |
| `chlora_graph_set_merge_inputs` | graph binding, Merge `nodeKey`, `inputs` (2..64) | Resize visible input banks; shrinking connected branches is rejected; connecting the last bank may add an empty spare |
| `chlora_graph_set_merge_branch_mute` | graph binding, `nodeKey`, input `branch`, `on` | Full state with mutation detail |
| `chlora_graph_set_merge_branch_polarity`, `chlora_graph_set_merge_protection` | graph binding, Merge `nodeKey`, input `branch` and `inverted`, or protection `on` | Full state with mutation detail |
| `chlora_graph_set_router_route` | graph binding, `nodeKey`, `input`, `output`, `on` | Full state with mutation detail |
| `chlora_graph_set_router_channels` | graph binding, Router `nodeKey`, `inputChannels`, `outputChannels` | Resize input and output width separately; connected ports/routes are guarded |
| `chlora_graph_clear_router_output`, `chlora_graph_reset_router` | graph binding, Router `nodeKey`; clear also takes `output` | Remove one output's crosspoints or reset the matrix to identity |
| `chlora_graph_set_node_channels` | graph binding, detached ordinary `nodeKey`, `channels` | Exact symmetric plug-in width or error |
| `chlora_graph_resize_node` | graph binding, ordinary `nodeKey`, CSS pixel `w`, `h` | Persisted visual size |
| `chlora_graph_remove_node` | graph binding, `nodeKey` | Remove a visible node or an attached Port Snake sidecar; Graph IN/OUT and other hidden nodes are guarded |
| `chlora_graph_move_node` | graph binding, `nodeKey`, `x`, `y` | Full state with mutation detail |
| `chlora_graph_move_selection` | graph binding, unique stable `nodeKeys`, optional `commentId`, native `deltaX`, `deltaY` | Move selected nodes and Comment in one undoable geometry edit |
| `chlora_graph_delete_selection` | graph binding, `nodeKeys`, `groupIds`, `commentIds`, `wires`; pass empty arrays for unused kinds and copy exact visible wire fields from Graph summary | Delete a mixed selection through one undoable Graph action; stale or ambiguous wire identities are rejected before mutation |
| `chlora_graph_splice_snake_node` | graph binding, detached wrapped plug-in `nodeKey`, exact aggregate wire `sourceNodeKey`, `destinationNodeKey`, `channelCount`, `sourceBranch`, `destinationBranch` | Replace that visible Snake wire with a serial wrapped plug-in, preserving branch identity |
| `chlora_graph_list_parameters` | graph binding, `nodeKey`, optional `start`, `count` | `{parameters,parameterLayout,total,start}` |
| `chlora_graph_open_editor` | graph binding, ordinary plug-in `nodeKey` | Request its native editor; the reply does not prove a window opened |
| `chlora_graph_retry_worker` | graph binding, ordinary plug-in `nodeKey`, decimal-string `workerToken` and `workerRevision` from state | Request retry only for the unchanged isolated worker |
| `chlora_graph_set_parameter` | graph binding, `nodeKey`, `parameterId`, `parameterLayout`, `value` | Full state with mutation detail |
| `chlora_graph_expose_parameter` | graph binding, plug-in `nodeKey`, exact writable `parameterId`, `parameterLayout` | Idempotently add the parameter to visible Graph controls and return its `exposedId` |
| `chlora_graph_set_stack_macro` | graph binding, Stack `groupId`, first-member `nodeKey`, `parameterId`, `parameterLayout`, `gesture`, normalized `sourceStart` and `value`, `absolute` | Apply one Stack macro gesture to compatible lanes and return updated state |
| `chlora_graph_remove_exposed_parameter` | graph binding, `nodeKey`, exact exposed control `id` from state | Remove one visible Graph control and return updated state |
| `chlora_graph_set_bus_format` | graph binding, `nodeKey`, `inputFormat`, `outputFormat`, optional `sidechainIn` | Full state after negotiating and persisting the hosted plug-in's role-bearing bus layout |
| `chlora_graph_create_group` | graph binding, `nodeKeys`, optional `childGroupIds`, `parentGroupId` | Full state; `mcpResult.groupId` identifies the new Group |
| `chlora_graph_set_node_group` | graph binding, `nodeKey`, `groupId` | Full state after assigning or ungrouping one node |
| `chlora_graph_set_group_parent` | graph binding, `groupId`, `parentGroupId` | Full state after nesting or promoting a Group |
| `chlora_graph_move_group` | graph binding, `groupId`, `deltaX`, `deltaY` | Full state after moving the Group contents |
| `chlora_graph_resize_group` | graph binding, `groupId`, `x`, `y`, `w`, `h` | Full state after setting persistent Group bounds |
| `chlora_graph_remove_group` | graph binding, `groupId` | Full state after removing the container and preserving its members |
| `chlora_graph_detach_group` | graph binding, inline Group `groupId` | Restore the predecessor-to-successor wire while retaining the Group's members and internal routes |
| `chlora_graph_splice_group_on_wire` | graph binding, detached Group `groupId`, exact visible MAIN source/destination keys and channels, `isBundle`, branch numbers | Atomically replace that wire through the Group's single left/right boundary Fanouts |
| `chlora_graph_set_group_comment` | graph binding, `groupId`, `text` | Full state after setting or clearing the Group title Comment |
| `chlora_graph_create_comment` | graph binding, `x`, `y`, `w`, `h`, `text`, optional `parentGroupId` | Full state; `mcpResult.commentId` identifies the new Comment |
| `chlora_graph_set_comment_text` | graph binding, `commentId`, `text` | Full state after setting or clearing standalone Comment text |
| `chlora_graph_move_comment` | graph binding, `commentId`, `deltaX`, `deltaY` | Full state after moving a standalone Comment |
| `chlora_graph_resize_comment` | graph binding, `commentId`, `x`, `y`, `w`, `h` | Full state after resizing a standalone Comment |
| `chlora_graph_remove_comment` | graph binding, `commentId` | Full state after removing a standalone Comment |
| `chlora_graph_get_layout_geometry` | graph binding | Pending operation; terminal result contains renderer geometry and `layoutRevision` |
| `chlora_graph_preview_layout` | graph binding, non-empty `layout` | Pending read-only operation; terminal result contains resolved geometry, metrics, and normalized layout |
| `chlora_graph_validate_layout` | graph binding, optional `layout` | Pending read-only operation; terminal result contains geometry and quality metrics for the current or proposed layout |
| `chlora_graph_apply_layout` | graph binding, non-empty `layout`, `layoutRevision` | Pending operation for one atomic layout transaction; terminal result contains committed geometry, metrics, and normalized layout |
| `chlora_graph_align_ports` | graph binding, `reference`, 1..128 unique `targets`, `axis`, `layoutRevision` | Pending atomic port-alignment operation with resolved layout in its terminal result |
| `chlora_graph_set_group_port_position` | graph binding, `groupId`, `nodeKey`, `side`, `position`, `layoutRevision` | Pending atomic Group-port update with resolved layout in its terminal result |
| `chlora_graph_get_view_preferences` | graph binding; visible WebUI | Pending read of camera, spatial meter display, and cable drag dead zone |
| `chlora_graph_set_viewport` | graph binding; `zoomScale` (0.15..8), `panX`, `panY` (CSS pixels); visible WebUI | Pending exact camera update; `(0.7,0,0)` resets to 100% |
| `chlora_graph_set_spatial_meter` | graph binding; `target` (`input` or `output`), `on`; visible WebUI | Pending per-instance display preference; enabling requires a speaker layout |
| `chlora_graph_set_cable_dead_zone` | graph binding; `pixels` (0, 16, 32, or 64); visible WebUI | Pending global cable drag preference update |

Current boundaries: MCP can open/select/close sessions and request native
plug-in editors, but editor creation is asynchronous and the request reply
does not confirm a visible window. A Stack can be created, configured while
empty, loaded across its lanes, split by stereo row, and unloaded. A tool call
returning updated state proves the state transition only; verify live audio
and DAW behavior separately.
Graph view preference calls fail when the WebUI is hidden or unavailable; they
change presentation only and do not create audio Graph undo entries.

A graph binding is the exact four-field tuple `instanceId`,
`bindingGeneration`, `graphTopology`, and `graphLifetime` from the most recent
`chlora_get_state` or synchronous graph-write result. The topology and lifetime
values are decimal **strings**; do not convert them to JSON numbers. Every
`chlora_graph_*` call, including `chlora_graph_list_parameters`, requires the
tuple and fails when it is stale. Read a fresh state after an asynchronous
plug-in load completes, because the operation result deliberately is not a full
state snapshot.
For a `.vst3` path load, `pendingPluginLoads` includes the queued file
inspection before the isolated plug-in load starts. Poll its operation ID;
session selection and other writes are rejected while that work is pending.

Copy and duplicate accept only ordinary plug-in nodes, using stable `nodeKeys`
from current state. Copy stores Chlora's in-memory Graph clipboard. Paste and
duplicate use the native isolated loader and return an operation ID; poll until
terminal status, then use its new `nodeKeys` and refresh the graph binding.
Those operations copy plug-in state and placement, not an inferred signal path;
connect the new nodes explicitly and inspect their wires.
Worker retry uses the exact `workerToken` and `workerRevision` exported for the
same Graph node or Strip slot. A successful request means recovery was queued;
read state again to confirm whether that worker became healthy. Graph sync
selection is transient and does not create a persistent Multi Link group.

`chlora_find_plugins` searches the Host's installed plug-in list independently
of the browser's current filter and returns unique UIDs. On an older Host, the
adapter falls back to the browser catalog, which can reflect its current UI
filter. `chlora_graph_get_summary` is a read-only adapter view over complete
Host state. Use the exact `uid` from a catalog match as
`pluginUid`. The Graph summary omits meters and other large UI fields while
retaining the binding tuple and stable node keys. A synchronous Graph write
already returns full updated state, so the next call may use the binding in that
result without an additional read.

Strip tools use `channel: -1` for a shared Multi Channel insert and a zero-based
explicit channel for a Multi Mono lane. `slotIndex: -1` on a load appends;
nonnegative indices insert before that slot unless `replace: true` is set.
For a shared insert, `channels` is the exact processed width and `start` is the
first Insert-bus channel. Their sum must not exceed the current `insertChannels`.
For a Multi Mono lane, pass `channels: 1`, `start: 0`, and `layer: 0` (or omit
`layer`). Replacement requires an existing slot. A successful load returns a
pending operation; poll it before issuing another write, then read the current
slot table. Slot indices change after insert, remove and move. `toSlotIndex` in
`chlora_strip_move_plugin` is the index before removal, with the current count
meaning append. Parameter IDs and layout tokens are discovered by
`chlora_strip_list_parameters` and values are normalized 0..1.

`chlora_graph_add_builtin` creates Bundle, Fanout or Router. Fanout has one
logical aggregate output that can accept multiple outgoing edges. Only Router
requires `channels`, meaning its 1..128-channel width. `chlora_graph_connect_channel`
addresses one MAIN channel pair. It does not infer a signal chain from node
positions, Group membership or names. The caller must verify each edge in the
returned `graphWires` or compact summary before continuing.

`chlora_graph_insert_builtin_on_wire` also supports Merge and requires the
selected visible MAIN wire's exact endpoint channels, aggregate flag, width,
and branch numbers from current state. It checks that wire before mutation;
the engine rolls back a failed insertion. Use the returned primary node key
and read back the complete inserted composition and both neighboring routes.
Multi-step routing recipes are individually undoable writes, not one atomic
transaction.
Bundle nodes attached to one Router or ordinary node may be reported as
`hiddenRoutingNode` after lane collection or fanout. Bundle-specific tools keep
addressing their stable `nodeKey`; ordinary node edits reject hidden routing nodes.
An attached Port Snake can also be used as a source or destination of
`chlora_graph_connect_snake` with branch `0`. Match its `bundleLaneCount` to
the peer width and verify the returned aggregate wire. Its stable key also
works with `chlora_graph_remove_node` when replacing a channel partition;
read back the remaining sidecars before creating a new one.

Graph node keys are positive decimal strings in the uint32 range. Branches are
zero-based. `sourceBranch` and `destinationBranch` range from 0 through 63.
`replaceExisting` is optional and defaults to `false` on Snake, exact channel,
and bus connects. The bus connect preserves already matching lanes and adds
missing lanes atomically. With `replaceExisting: true`, these tools remove
other feeds into the targeted destination channel or Snake input branch even
when the requested connection already exists. An already exclusive connection
is a no-op. Exact channel and bus replacements reject any destination range
that overlaps an aggregate Snake branch, including a full-width bus range;
disconnect or replace that branch with a Snake operation first. This avoids
leaving an invisible partial branch. `chlora_graph_connect_channel` rejects
logical Snake endpoint pairs because their channel offsets do not identify a
Snake branch; use `chlora_graph_connect_snake`. `chlora_graph_disconnect_channel`
rejects an exact lane of a visible aggregate branch; use
`chlora_graph_disconnect_snake`. An ordinary extra channel feed into the same
Merge bank can still be disconnected on its own. Unpack channel and fanout
connections to a Snake Merge are rejected; use a Snake connection for that
aggregate path. Read back the destination after the write; a multi-step routing
recipe is not atomic. Node positions range from 0 through 20,000.
Graph channel widths range from 1 through 128, and merge input counts from 2
through 64. Merge `branch: -1` addresses the output gain; input branches range
from 0 through 63. Merge gains range from -100 through +24 dB.

Bus-format keys are `mono`, `stereo`, `5_1`, `7_1`, `a_5_1_2`, `a_5_1_4`,
`a_7_0_2`, `a_7_1_2`, `a_7_0_4`, `a_7_1_4`, `a_7_0_6`, `a_7_1_6`,
`a_9_1_4`, `a_9_1_6`, `a_9_1_4_itu`, `a_9_1_6_itu`, `auro_9_1`,
`auro_10_0`, `auro_10_1`, `auro_11_1_71`, `auro_11_1_hc`, `auro_13_1`,
and `nhk_22_2`. `sidechainIn` accepts 0 through 127 channels. When it is
omitted, the Host preserves the node's current sidechain width; the schema's
zero default is a client-facing initial value. The Host rejects layouts that
the selected plug-in cannot support.

Parameter reads default to `start: 0` and `count: 128`; the respective limits
are 0..65,535 and 1..256. A descriptor's `parameterId` is opaque and must be
used with the exact `parameterLayout` returned by the same list call. Parameter
values are normalized finite numbers from 0 through 1. The Host rejects stale
layouts, unknown parameters, meters, and non-automatable parameters.

Group creation uses one or more stable `nodeKeys`, not transient UI node
indices. Up to 128 unique node keys and 128 unique optional child Group IDs are
accepted. `parentGroupId: 0` means top level. `chlora_graph_set_node_group`
uses `groupId: 0` to remove a node from every Group, while
`chlora_graph_set_group_parent` uses `parentGroupId: 0` to promote a Group.
Removing a Group deletes its owned boundary Fanouts but preserves its member
nodes; child Groups and Comments are promoted according to the existing Chlora
Group lifecycle contract.
`chlora_graph_create_group` creates its initial left and right boundary
Fanouts. `chlora_graph_splice_group_on_wire` requires exactly one boundary on
each side and no existing external boundary crossings; use the initial pair
for a simple inline Group. `chlora_graph_detach_group` restores the supported
one-predecessor/one-successor external route without deleting the Group.
An attached Group Fanout shows one aggregate MAIN socket in the UI, while its
physical boundary can carry multiple channel lanes. A two-channel Router peer
has native wire-level verification. Do not infer a signal route from visual
grouping; connect the boundary explicitly and read back every expected lane.

The layout tools operate in native graph coordinates, where three graph units
equal one world CSS pixel. A `layout` is a strict object with optional `nodes`,
`groups`, and `groupPorts` arrays; unknown fields at either level are rejected.
Preview and apply plans must contain at least one entry. Pass the same proposed
`layout` to validation when checking a candidate; omitting it or passing `{}`
inspects only the current graph.

- `nodes` has at most 256 `{nodeKey,x,y}` entries. Coordinates are finite and
  range from -20,000 through 20,000.
- `groups` has at most 128 `{groupId,x,y,w,h}` entries. Coordinates use the
  same range; finite width and height range from 1 through 40,000.
- `groupPorts` has at most 256
  `{groupId,nodeKey,side,position}` entries. `side` is `left` or `right`, and
  `position` is a finite normalized number from 0 through 1.

Stable identities may occur only once per array: `nodeKey` for nodes,
`groupId` for Groups, and `nodeKey` for Group ports. Port
references are strict `{nodeKey,direction,branch}` objects, where `direction`
is `input` or `output` and `branch` is an integer from 0 through 63. Alignment
targets must be unique and `axis` is `x` or `y`.

All six layout tools use asynchronous operation envelopes. The immediate result
is `{operationId,status:"pending"}`. Poll `chlora_get_operation`; a successful
terminal envelope includes a nested `result` with the applicable
`layoutRevision`, actual geometry, quality metrics, and normalized or resolved
layout. Geometry comes from the renderer's production node, Group, port, bound,
and cubic-path calculations. Metrics document their sampling and tolerances and
exclude intended shared ports.

Geometry, preview, and validation are read-only. Preview restores temporary
renderer state and caches and never publishes a graph or UI mutation. Apply,
alignment, and Group-port positioning require a non-empty `layoutRevision`
string of at most 128 characters. The Host compares it with current
geometry-affecting state immediately before committing one validated
transaction. Explicit MCP IO coordinates are saved with the graph and protected
from native-editor resize placement, including during session restoration;
automated plug-in values, Merge gain/mute controls, and worker telemetry do not
invalidate a geometry revision, while inline control row-count changes do;
an outdated but well-formed revision is therefore a Host guard,
not a wire-schema error. Empty or malformed plans are rejected before reaching
the Host, and stale plans cannot partially mutate the graph.

The short title rendered on a Group border is its Group Comment and is written
with `chlora_graph_set_group_comment`. A standalone canvas annotation is a
separate Comment object managed by the five `*_comment` tools. Both text fields
accept 0 through 2,048 characters, so an empty string clears the text. Group and
Comment coordinates and movement deltas range from -20,000 through 20,000.
Group dimensions range from 0.001 through 20,000; standalone Comments require
at least 72 by 48 and at most 20,000 by 20,000. Each successful mutation returns
the complete state, including `graphGroups` and `graphComments`; exact no-ops
return `mcpResult.changed: false` without adding an undo snapshot.

Operation IDs are strings from 1 through 100 characters. Operation status is
exactly `pending`, `succeeded`, or `failed`; `error`, `nodeKey`, `instanceId`,
and the layout operation's nested `result` appear only when applicable to that
operation state.

`chlora_select_session` is the one state-changing tool that takes only
`instanceId`: it selects an already open session and returns the new full state,
including the binding generation required by subsequent mutations.

`instanceId` is an integer from 1 through 2,147,483,647.
`bindingGeneration` is an integer from 0 through 9,007,199,254,740,991 copied
from the latest state.
Channels are zero-based integers from 0 through 127. Gains are finite numbers
from -100 through +12 dB. Booleans must be JSON booleans. Unknown or missing
fields are rejected before a request reaches Chlora.

Channel gain uses Chlora's existing selected-channel linked behavior, so one
request can update other channels when linking is active. Read the returned full
state instead of assuming only the named channel changed. Undo and redo accept
an asynchronous state restoration request; their immediate result is a full
snapshot with `stateRestoreInFlight: true`, not the completed restored state.
Poll `chlora_get_state` until `stateRestoreInFlight` is false before sending
another mutation.

Insert and Output widths are distinct from the native/unified layout policy.
Multi Mono locks Insert width to Output width. A connected Chloe Bridge may
publish an authoritative Output width after a local change; read back the
subsequent state before relying on that width for a plug-in load or route.

Except for `chlora_select_session` and `chlora_open_session`, every non-graph mutation is bound to both
the intended session and the state generation the caller observed. Graph calls
also bind the graph topology and lifetime as described above;
`chlora_graph_get_summary` is the no-argument exception that returns the
current tuple. A stale binding fails
instead of being retargeted. The adapter sends each mutation once and never
retries it automatically. If a mutation times out after transmission, its
outcome is unknown; call `chlora_get_state` and inspect the result before
deciding whether to retry.

The API exposes only the listed, typed operations. It has no general UI-event
bridge, arbitrary command execution, raw plug-in command endpoint, or
runtime-invocation escape hatch. Its three file-load tools accept only an
absolute local `.vst3` plug-in path.

## Pure-MCP parallel reverb workflow

Start with the Chloe instance ID. Call `chlora_open_session` if it is not
already open, or `chlora_select_session` if it is, then `chlora_get_state`
and require `mode: "graph"`. `chlora_set_mode` can switch a suitable Strip
session to Graph; inspect the returned state and honor its plug-in-loss guard.
Keep the returned binding tuple and locate the Graph IN and OUT `nodeKey` values
in `chlora_graph_get_summary`. Each synchronous graph write returns a full state; use its new
binding tuple for the next write.

Before mutation, compare Graph `inputChannels`, `outputChannels`, the requested
route width, and the chosen plug-in's supported widths. Choose one width that
IN, reverb, Merge, and OUT can all carry, or stop and plan an explicit channel
map. Do not leave a partly loaded parallel route because the widths disagree.

1. Call `chlora_find_plugins`, choose the exact reverb row, and pass its `uid`
   as `pluginUid` to `chlora_graph_add_plugin`. If the installed VST3 is not
   in the catalog but its absolute local bundle path is known, use
   `chlora_graph_add_plugin_file` with `pluginPath`. The requested `channels` must be
   supported by that plug-in and the current graph. Supply required `x` and
   `y` in the `0..20000` creation range. On a blank canvas, `x: 600, y: 300`
   for the reverb and `x: 900, y: 300` for the later Merge are valid initial
   positions; inspect existing geometry first if the canvas is occupied.
2. Store the returned `operationId`. Poll only `chlora_get_operation` until its
   status is `succeeded` or `failed`. On success, retain its `nodeKey` and call
   `chlora_get_state` to obtain the post-load graph binding. On failure, report
   its `error`. Do not retry an add after a timeout until state and operation
   status establish the outcome.
3. Call `chlora_graph_list_parameters` for the reverb node. Inspect the returned
   descriptors by `name`, `label`, current `value`, and `text`; do not guess a
   parameter ID from a product name. Establish a wet-only return by writing
   the discovered Mix/Wet and separate Dry controls to values whose displayed
   meanings the plug-in confirms. Pass the exact returned `parameterId` and `parameterLayout` to
   each `chlora_graph_set_parameter` call. Re-list parameters to confirm the
   plug-in's actual, possibly quantized values and displayed text. Normalized
   endpoints mean wet-only or dry-silent only when the descriptors and readback
   confirm those meanings. If wet-only output cannot be established, stop this
   parallel recipe before routing a second dry branch; report the processor
   setting as unresolved.
4. Before adding routes, call `chlora_graph_set_snake` for the Graph IN, reverb,
   and Graph OUT nodes when they are not already wrapped. A wrapping change
   removes that node's incident routes by contract; a no-op succeeds with
   `mcpResult.changed: false`. Keep one compact Graph IN Snake output and add
   a separate `fanout` builtin for the explicit parallel split.
5. Add an explicit Fanout with `chlora_graph_add_builtin`, `kind: "fanout"`,
   unless one was atomically inserted on the existing IN-to-reverb aggregate
   wire with `chlora_graph_insert_builtin_on_wire`. Keep its returned `nodeKey`.
   Add a two-input Merge with `chlora_graph_add_merge`, supplying required
   `channels` at the intended width, `inputs: 2`, and planned `x` and `y`; retain
   `mcpResult.nodeKey`. Connect Graph IN branch 0 to Fanout input 0, Fanout
   output 0 to both reverb input 0 and Merge dry input 0, reverb output 0 to
   Merge wet input 1, and Merge output 0 to Graph OUT input 0. One Fanout
   aggregate output can feed both destinations. Use `replaceExisting: false` unless replacing
   a conflicting input is an explicit part of the request. The Merge may create
   an empty spare input bank when its last visible bank is connected; the wires
   identify which banks carry dry and wet signal.
6. Set the dry and wet input levels with `chlora_graph_set_merge_gain` on merge
   branches 0 and 1, and set the merge output with `branch: -1`. Use the user's
   specified levels or report explicit starting values of 0 dB dry, -6 dB wet,
   and 0 dB output. After every
   call, inspect the returned `mcpResult.changed` and full graph state before
   continuing.
7. To label the wet processor, call `chlora_graph_create_group` with its stable
   `nodeKey`, retain `mcpResult.groupId`, then call
   `chlora_graph_set_group_comment` with that ID and the desired title. Reuse
   the full-state binding returned by Group creation; its automatic boundary
   Fanouts change graph topology.

When the wet-only readback and all returned wires and gains match, this
sequence establishes the intended dry and wet Graph state through MCP alone.
The state result does not establish realtime audio or level matching.

## Protocol and limits

The stdio side supports MCP protocol versions `2025-11-25` and `2025-06-18`,
including `initialize`, `notifications/initialized`, `ping`, `tools/list`, and
`tools/call`. Successful calls include both a JSON `structuredContent` object
and an equivalent text content item. Host connection and execution failures are
returned as tool results with `isError: true`; malformed JSON-RPC and unsupported
methods use JSON-RPC errors.

The adapter opens one Host connection per call and sends one newline-terminated
UTF-8 JSON request:

```json
{"name":"chlora_get_state","arguments":{}}
```

The Host replies with one success or error object:

```json
{"ok":true,"result":{}}
{"ok":false,"error":"description"}
```

Host requests are limited to 64 KiB, replies to 4 MiB, and each Host call to
five seconds. These limits are enforced without retrying a mutation.

The implementation follows the official MCP
[stdio transport](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports),
[lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle),
and [tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
contracts. Compatibility behavior for the older pinned revision follows its
[2025-06-18 lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)
and [tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
definitions.

## Coverage review and remaining work

The current tools cover session selection, channel widths and names, master and
channel gain/mute/solo, exact shared and MonoLink slots, plug-in parameters,
Strip routing, Graph plug-in and built-in creation, channel/Bundle/Snake/Group
boundary routes, Graph controls, node/group/comment/cable geometry, undo/redo,
and async loads. Selected paths have native tests and have been exercised
through MCP against a dedicated-lane Host with a synthetic 2-channel Chloe
Bridge fixture. The fixture emits no audio, so these results establish the
control plane only. Development receipts for parallel reverb routing, per-channel serial chains,
mixer readback, and compact search establish the control plane only. They do
not establish that the recipient's installed Host or DAW audio path works.

The UI still has operations without equivalent MCP contracts:

| UI operation | Current MCP path or gap |
|---|---|
| Exposed-parameter configuration by touching a native editor control | Exact parameter-ID exposure/removal now exists; editor gesture capture remains UI-only |
| Plug-in file chooser | `chlora_graph_add_plugin_file`, `chlora_graph_load_stack_file`, and `chlora_strip_load_plugin_file` accept an absolute local `.vst3` path; file inspection and isolated loading return an operation ID and must be polled |

Deployment and acceptance are separate: install a binary built from this
contract, verify its executable identity, then exercise a live Chloe session
through MCP. Test exact Strip slot/span loading, parameter readback, a parallel
reverb Graph, multichannel series routing, Graph save/restart restoration and
audio behavior. A native unit test or an old Host socket does not prove those
runtime paths.

## Verification

Run the dependency-free adapter verification directly:

```bash
python3 /absolute/path/to/mc-patcher/tests/chlora_mcp_verify.py
```

It checks both protocol handshakes, the 143 full-profile tool names, and the
compact-profile discover/describe/invoke path in a real
stdio subprocess, plus selected schemas, nested layout and port bounds,
duplicate and unknown-field rejection,
graph guard types, asynchronous operation forwarding, request and notification
error handling, disconnected behavior, private Unix-socket calls and Host
errors, request size enforcement, and ambiguous multi-Host discovery. It does
not connect to or mutate a real Chlora process.

### Live plugin insertion and detachment

`chlora_graph_splice_node` uses the plugin's negotiated width and preserves other
channels and the node's position. The plugin must be detached, and the selected
MAIN wire range must already exist. These two tools currently target ordinary
plugin nodes; aggregate Snake endpoints keep their dedicated routing tools.
Read fresh binding/topology tokens before each operation. Each successful change
uses the existing undo snapshot path.

Live routing edits use a 20 ms fade down and drain the IPC return queue before
latency publication, allow the graph's
latency buffers to settle, then fade up over 20 ms. This low-latency policy adds
no permanent delay, but deliberately permits a brief level dip (longer for
high-latency paths). It does not promise continuous reverb tails or a seamless
crossfade between two independently running processing graphs.
