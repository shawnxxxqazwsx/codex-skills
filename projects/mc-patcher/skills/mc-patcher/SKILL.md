---
name: mc-patcher
description: >-
  Develop, diagnose, build, review, and verify the mc-patcher C++/JUCE
  repository. Use only when the current repository is identifiable as
  mc-patcher or the user explicitly asks to work on or apply mc-patcher; do not
  trigger for generic JUCE, VST3, or audio-product research. Covers MC Host,
  MC Bridge, multichannel routing, shared-memory IPC, Q-Link, wet return,
  latency, VST3/WaveShell hosting, realtime safety, targeted validation,
  explicit deployment, and honest reporting of untested DAW paths.
---

# MC Patcher

The Host/Bridge path consists of two products joined by a versioned realtime
protocol. Standalone utility plug-ins, including Pigora, have their own
processor/editor path and do not require a Bridge round trip for acceptance:

```text
DAW -> MC Bridge VST3 -> shared-memory IPC -> MC Host graph
DAW <- MC Bridge VST3 <- shared-memory IPC <- processed wet return
```

Read the current `README.md` and relevant `CMakeLists.txt` sections before relying on commands in this skill. The repository evolves; source files and configured targets are authoritative.

## Architecture boundaries

1. Keep the Bridge limited to DAW bus negotiation, transport, discovery, state, and latency reporting. Keep graph editing, plug-in hosting, routing, and most UI in the standalone Host.
2. Keep audio transport local and realtime-safe: shared memory plus lock-free SPSC structures. Use network or service discovery only outside the audio path.
3. Preserve discrete multichannel behavior through the core. Do not silently clamp a general graph or protocol type to stereo.
4. Keep allocation, locks, filesystem/network access, UI work, logging I/O, `shm_open`, and graph reconstruction off `processBlock` and equivalent realtime callbacks.
5. Rebuild or swap graph state on a control/message thread. Hand fixed-size messages or atomically published state to the audio thread.
6. Identify hosted plug-ins by stable IDs plus names and format metadata. Do not make session restore depend only on a shell bundle path that can change across versions.
7. Extend the protocol in `shared/` instead of creating a parallel transport path. Version ABI or behavior changes deliberately.

Open [references/architecture.md](references/architecture.md) only when the task needs product precedents, VST3/JUCE API anchors, or protocol design notes.

## Work by evidence

Follow the repository `AGENTS.md` for failure reproduction, hypothesis limits,
writer/build ownership, staged validation, deployment, and completion wording.
This skill adds only the product-specific architecture and verification matrix.

For concurrent plug-in or capture work, classify conflicts by the complete
resource set rather than by repository name. The user's audio-router lanes are
independent by standing contract: record routes for evidence, but never use
audio channels, Bridge/IPC routes, or capture activity to block, interrupt, or
contact another task. Source dependency closure, build directory, generated
artifact, production deployment, a mutating DAW/Host control plane, and global
device-setting changes remain possible conflicts. Independent lanes continue
without interruption while only a proven colliding phase waits. Use
`$orchestrator` for dedicated build lanes and handoff when two or more
tasks are active. Treat `build-juce` as a protected integration/deployment tree:
direct configure, CMake target builds, and CTest runs there are expected to fail
without the repository build-lane wrapper. A guard failure is not a reason to
contact another task; move routine work to the caller's dedicated lane.

## Validation matrix

Run only the rows touched by the change, plus at least one neighboring regression.
When a build tree may be stale, discover configured tests with `ctest -N`
through that task's build-lane wrapper, as shown in the verification reference.

Read [references/verification.md](references/verification.md) before selecting
exact CMake/CTest targets, local plug-in probes, deployment steps, or a DAW
matrix.

Pigora source, fitting contracts and product-specific verification now live in the independent local `pigora-eq` project. Use that project’s skills and `references/pigora-handoff.md`; do not resume its work from the Clara checkout.

| Change | Minimum evidence |
|---|---|
| Core protocol or portable logic | Configure/build the non-JUCE tree; run the relevant CTest case and then the portable suite when practical |
| SHM, ring, IPC, or Bridge realtime path | Relevant `ipc_smoke`, `shm_roundtrip`, `shm_multich`, multi-instance, wet-return, or click tests; inspect the changed callback for allocation/locks/blocking calls |
| Host engine, graph, prepare, FIFO | Build the Host and `mc_host_engine_verify` when its local plug-in prerequisites exist; exercise editor open/close during playback if that was the affected path |
| VST3 Bridge lifecycle or bus layout | Build `McBridge_VST3`; run PluginVal at strictness 5 or higher when installed; test at least two relevant bus/block/sample-rate combinations when possible |
| Wet return, click, delay, or PDC | A local regression plus a DAW-to-Bridge-to-Host-to-DAW wet-return check; record whether mount and steady state were both exercised |
| Plug-in scanning/loading or WaveShell | Load the named real plug-in/shell, open and close its editor, and verify a previously working plug-in still loads |
| High channel count or throughput | Inspect the current tests first. If no representative high-channel benchmark exists, add or run a bounded reproducible probe rather than presenting the lower-channel smoke test as 48/64/128-channel evidence |
| Host UI, Q-Link, or mixer | Build the Host or Theme Lab; inspect the actual surface at target size; test selection, parameter propagation, editor lifecycle, and any prior deadlock path |
| Pigora model, parameter adapter, or editor integration | Frozen fitting receipt plus the Pigora handoff matrix: effective controls, production audio/response agreement, point/full paths, restored hidden state, and applicable rack/host checks |

Local commercial/test plug-in probes are opt-in through `MC_PATCHER_ENABLE_LOCAL_PLUGIN_TESTS`. If prerequisites are absent, do not convert that absence into a product failure; report the integration layer as untested.

## Deployment ownership

The current repository `AGENTS.md` is authoritative for mandatory Host
deployment, VST3 destinations, deployment targets, version bumps, and
restart/rescan reporting. Inspect it rather than relying on copied policy here.

## Realtime review

When a diff touches an audio callback, verify all of the following:

- Buffers and containers are preallocated for the negotiated maximum.
- No mutex, file lock, condition wait, filesystem/network call, UI call, or log I/O is reachable.
- No implicit container growth, string formatting, shared ownership churn, or plug-in discovery occurs.
- Producer/consumer ownership is unambiguous; no double push/pop or unsafe lifetime handoff exists.
- Oversized blocks, sample-rate changes, channel reconfiguration, and peer teardown fail safely.
- Latency reporting covers the actual round trip and any hosted processing latency.

## Report results

Use the completion standard in `AGENTS.md`. Add the exact plug-in identity,
channel/block/sample-rate combination, or hosted path when those details are
material to the result.
