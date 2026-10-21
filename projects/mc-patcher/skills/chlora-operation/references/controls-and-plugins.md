# Controls, Strip, and hosted parameters

Choose the actual scope before changing “volume”, “mute”, “solo”, or “bypass”.
Session/mixer and Strip calls use the active session binding; Graph calls use
the Graph tuple. Reuse mutation state, refresh after asynchronous work, and use
[fastpaths.md](fastpaths.md) for topology. `graph_plan.py` is Graph-centered;
explicit mixer steps can operate within its same active Graph session. It is
not a standalone Strip planner.

## Volume and flags

| Requested scope | Tool and units | Readback / behavior |
|---|---|---|
| Input trim before Graph/FX | `chlora_set_pre_gain(gainDb)`; −30..+30 dB | `preGainDb`; one session-wide trim, smoothed in audio processing |
| One output channel fader | `chlora_set_channel_gain(channel,gainDb)`; −100..+12 dB | `channels[].gainDb`; selected-channel link behavior applies |
| Master after channel faders | `chlora_set_master_gain(gainDb)`; −100..+12 dB | `masterGainDb`; active session, not all sessions |
| Merge input branch | `chlora_graph_set_merge_gain(nodeKey,branch,gainDb)`; −100..+24 dB | Node `sumBranches[].gainDb`; zero-based existing branch |
| Merge output | Same tool, `branch:-1` | Node `sumOutputGainDb`; affects the complete sum |
| Plug-in input/output/wet control | Graph/Strip `list_parameters` → `set_parameter` | Vendor normalized value and display text; no generic dB law |

Mixer/master use linear amplitude `10^(dB/20)`; values ≤−99.5 dB are silent
and read back −100 dB. Pre-gain has no such silent sentinel. A normalized vendor
parameter value is not this amplitude formula. No separate native per-input
fader tool exists; input mute/solo and global pre-gain are distinct controls.
A regular Group/Stack frame has no generic audio fader; use its processor,
Merge branch/output, or output channel controls as appropriate.

For **only one output fader**, inspect `channels[].selected`. If the target is
selected together with other channels, `set_channel_gain` copies the same
absolute gain to every selected active output. Set an explicit single-channel
selection with `chlora_set_selected_channels(channels:[C],focusChannel:C)`,
or `chlora_clear_channel_selection` when clearing is the intended selection.
Do not pass an empty array to `set_selected_channels`. When selection changes
only to isolate this write, retain and restore the original selected members
and focus afterward (use the clear tool to restore an originally empty selection).
Write and check the affected rows. For a linked group, explicitly select its
members and write one selected member. This is absolute matching, not relative
offset preservation.

Output flags: `chlora_set_channel_mute(channel,on)` and
`chlora_set_channel_solo(channel,on,exclusive)`; read `channels[].muted/soloed`.
Input flags: `chlora_set_input_mute` / `chlora_set_input_solo`; read
`inputMuted[]` / `inputSoloed[]`. Channels are zero-based and must be active on
the corresponding bus. Mute wins over Solo. Multiple Solo flags ordinarily
remain active. `exclusive:true` clears that side's Solo flags before applying
the requested target value—even `on:false`; omit exclusivity to release only
one Solo. Input and output Solo banks remain separate. Output mute/solo calls
do not automatically fan out to the selected fader group.

Recipes:

- “Solo just this output”: resolve C → output Solo `on:true,exclusive:true` →
  inspect all active output Solo flags and the target's mute state.
- “Release this Solo”: same side, C, `on:false` without exclusivity.
- “Clear every input Solo”: `chlora_clear_channel_flags(scope:"input",flag:"solo")`.
  Clear output mute with `scope:"output",flag:"mute"`; clearing one flag does
  not clear the other flag or another side. These are active-bus resets.
- “Solo this wet branch”: resolve the exact Merge branch →
  `chlora_graph_set_merge_branch_solo(nodeKey,branch,on:true)` → read its branch
  bank. Merge has no exclusive-Solo argument: multiple soloed branches sum,
  mute wins. Clear other branches explicitly only if exclusivity was requested.
  Branch mute uses `on`; polarity uses `inverted` with
  `chlora_graph_set_merge_branch_polarity`.

`chlora_set_bypass(on)` is session master bypass. Hosted Graph nodes use
`chlora_graph_set_bypass(nodeKey,on)` with the complete current Graph tuple.
This is Host-owned MAIN passthrough with the node's reported latency retained,
independent of vendor parameters; it preserves wires and plug-in configuration.
Ordinary/wrapped nodes, Stack members, and native Multi Mono wrappers are
eligible; IO and built-in routing nodes are rejected. Set an explicit Boolean
`on`, never infer a toggle from stale state. Read back that exact node's
`bypassed`; a repeated value changes nothing and creates no undo step. State
persists through session save/restore, presets, and Graph copy/duplicate. The
surface indicates bypass with a dimmed node; it has no node Bypass button or
passthrough text.
With Graph canvas focus, `M` toggles the selected hosted nodes together, including
selected Stack members. Selecting a whole Stack (including a single click on its
loaded plug-in name) includes every eligible member. If every target is bypassed,
`M` restores them; otherwise it bypasses all targets in one undoable edit.
Text/control focus, modifiers, IME and repeats do not trigger this shortcut.
With no hosted target selected, `M` retains the existing Merge insertion shortcut.
Host bypass uses a 10 ms latency-aligned dry/wet ramp without rebuilding the
prepared Graph sequence. DSP and dry delay history continue during bypass, so
the processing cost remains. Undo/redo only changes the bypass targets and does
not reload plug-ins. A topology rebuild still has its separate transition path;
do not claim gap-free or click-free DAW output from UI state alone.
A vendor bypass parameter, if exposed and writable, can use Graph parameter
tools, but has vendor-defined behavior. Strip bypass is
`chlora_strip_set_bypass(channel,slotIndex,on)`. These do not mean mute,
processor removal, or gain zero. Inspect each corresponding bypass field.
Built-in routing and Merge gain use their own tools; do not assume a vendor
bypass parameter equals Host bypass. Merge converts dB to linear amplitude and treats −100 dB as silence.
No Merge overload-protection control is published; summing can raise signal level.

Source: [adapter ranges](../../../../tools/chlora_mcp.py),
[native mixer](../../../../apps/host/juce/PluginHostEngine.h) (`setOutGainDb`,
`setMasterGainDb`, `setPreGainDb`, `applyOutGainsInterleaved`),
[event mapping/state](../../../../apps/host/juce/MainComponent.h) (`setGain`,
`setSolo`, `setInSolo`, `exportWebSurfaceState`),
[Merge](../../../../apps/host/juce/AdvancedSumProcessor.h).

## Exact Strip loads and ordering

Read full state: Multi Channel uses `inserts[]` with `index,start,width,minLayer`;
Multi Mono uses `insertLanes[].channel/slots[]`. The flat `inserts[]` in Multi
Mono is only a focus-lane mirror. Slot indices shift after insert/remove/move;
there is no published stable Strip slot token. Rebind by current lane/index,
name/span and worker identity when present; do not require a nonzero worker
identity for an in-process plug-in.

Use `chlora_strip_load_plugin` with an exact cached `pluginUid`, or
`chlora_strip_load_plugin_file` with an absolute local `.vst3` path. Both require
explicit `channel,slotIndex,channels,start`; optional `replace` defaults false
and `layer` defaults zero. Await the operation; then inspect its actual slot
index and the new state before another write. A cached maximum channel claim
is not proof of actual processed width or vendor layout support.

| Mode | Target | Native constraints |
|---|---|---|
| Multi Mono | Explicit lane C≥0, slot S | `channels:1,start:0,layer:0`; shared `channel:-1` and stereo-width loads rejected |
| Multi Channel | Shared `channel:-1`, slot S | Exact contiguous span `[start,start+channels)` inside Insert width; vendor must accept the requested width |
| Graph | Stable node key | Use Graph load/routing/parameter tools, not Strip calls |

For “two processors in series on lane C”, load first at current S with mono
constraints → await/read lane → load second at the next intended current index
→ await/read actual ordered lane. To repeat on another lane, repeat only the
requested loads using that lane; selection is not an implicit load target.
For “stereo on channels 4–5” in zero-based terms, use shared `start:4,channels:2`.
Do not silently load several mono instances when one stereo instance was asked
for, or turn a stereo plug-in into a wider processor.

Multi Channel layers are **serial stages**. Non-overlapping spans packed into
one layer may run concurrently; they are not a wet/dry parallel sum on the same
channels. `chlora_strip_set_layer` sets a minimum packing layer, not a guaranteed
final row number. `set_span` is Multi Channel only and must fit Insert.
`move_plugin(toSlotIndex)` uses the destination index before removal;
`slot+1` is a no-op, and one-past-last appends. Inspect actual spans and ordering
instead of equating array order or a layer label with the entire audio path.

Strip route maps use `chlora_strip_set_route(stage:"input"|"post",src,dst,on)`.
Input map precedes pre-gain/inserts; post map follows inserts and precedes
faders. Adding an edge preserves other feeds to that destination, causing
linear fan-in summation. For an exclusive remap, clear the exact destination
with `chlora_strip_clear_route_destination` first, then add its intended edge.
Reset/clear routes can select input, post, or both; use full reset only when
requested. Actual dry/wet parallel processing belongs to explicit Graph
Fanout/branches/Merge routing, with proven wet-only effect state.

Source: [exact Strip handlers](../../../../apps/host/juce/ChloraMcpStrip.h),
[asynchronous loader/state](../../../../apps/host/juce/MainComponent.h)
(`beginMcpStripPluginLoad`, `insertLanes`),
[layer process plan](../../../../apps/host/juce/PluginHostEngine.h) (`stripLayers`).

## Parameters and Q-Link

List only relevant pages with Graph `nodeKey` or Strip `channel,slotIndex`.
Inventory returns `parameterId,parameterLayout` plus `name,label,value,text,
defaultValue,steps,isDiscrete,isBoolean,automatable`. Treat the ID as opaque and
the layout as current to that instance. Write finite normalized `value:0..1`
with the matching ID/layout; re-list to check actual quantization and text.
Non-automatable and meter-category parameters are rejected even if a control
is visible. A generic `readOnly` flag or a complete enum-label table is not
promised by the inventory.

For booleans use verified off/on values; for a discrete vendor control inspect
`steps` and current text. `steps` does not provide all textual choices or prove
which step means “quarter note”. The current API has no set-by-display-text,
set-by-dB, vendor program-select, or “synchronise delay to quarter note” tool.
Use an established vendor mapping with bounded normalized writes/readback, or
inspect its editor when the task needs unresolved vendor semantics. Do not
exhaustively probe an audible control just to reverse-engineer it. Sandbox
`text:"..."` means vendor formatting is pending; re-list before interpreting it.
Wet-only verification must include actual wet/dry descriptors and effective
values; names alone are insufficient.

For one exact MonoLink parameter write, the native handler temporarily selects
only its explicit lane and restores the user's selection. Shared Strip
parameter writes can follow compatible selected-slot Q-Link behavior; verify
target scope before writing. For a one-time full-state copy, explicitly select
compatible targets and source first: MonoLink
`set_selected_channels(channels,focusChannel:source)`; Multi Channel
`set_selected_slots(slotIndices,focusSlot:source)`. Then
`chlora_strip_sync_qlink_state(channel,slotIndex)`: MonoLink source must be
focused and selected; shared source slot must be selected. Target plug-ins
must be compatible. Read parameters on each target; the reply does not expose
complete vendor chunk equality. `chlora_set_qlink_auto_sync(on)` controls
continuing state synchronization for the current selection, not a one-off copy.
Enable it only when ongoing linking was requested.

Graph Config (`chlora_graph_configure_parameters`) enables/disables editor
capture; enabling requests its editor. For known controls, prefer
`chlora_graph_expose_parameter` → capture returned `exposedId` → remove by that
ID. Config false may leave `exposed:null`; handle nullable state. For a requested Stack macro, list the first member's current descriptor and
use `chlora_graph_set_stack_macro` with its groupId/nodeKey, ID/layout,
`gesture`, `sourceStart`, `value`, and explicit `absolute`. The source is the
first member; native compatibility gates retain relative or absolute control
across lanes. Read each affected lane rather than treating a frame label as
one generic volume knob. Graph MultiLink
is a different explicit state-sharing operation; parameter writes can propagate
to compatible linked instances. Check current link membership when independent
copies were requested. Stack loads are independent per lane; do not infer
shared state solely from matching names.

Source: [parameter inventory/write](../../../../apps/host/juce/PluginHostEngine.h)
(`getStripMcpParameters`, `setStripMcpParameter`, `getAdvancedMcpParameters`,
`setAdvancedMcpParameter`, `syncQLinkStateFromVisible`),
[Strip selection isolation](../../../../apps/host/juce/ChloraMcpStrip.h).
