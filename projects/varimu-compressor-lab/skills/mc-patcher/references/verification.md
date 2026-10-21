# MC Patcher verification reference

Use the repository's current `CMakeLists.txt`, README, and configured build tree
as the source of truth. This inventory is a routing aid, not permission to run
every test for every change.

## Build trees

Run from the repository root. Replace the example lane suffix with the current
task's stable suffix and reuse its compatible lane. Configure only when needed;
select the changed target and focused test, not every command below. Every
configure/build/CTest invocation goes through the lane wrapper.

Portable core without fetching/building JUCE (focused example):

```bash
python3 tools/mc_build_lane.py run --lane core-TASK --build-dir build-lane-core-TASK -- cmake -S . -B build-lane-core-TASK -DMC_PATCHER_BUILD_JUCE_BRIDGE=OFF
python3 tools/mc_build_lane.py run --lane core-TASK --build-dir build-lane-core-TASK -- cmake --build build-lane-core-TASK --target mc_ipc_smoke -j 4
python3 tools/mc_build_lane.py run --lane core-TASK --build-dir build-lane-core-TASK -- ctest --test-dir build-lane-core-TASK -R '^ipc_smoke$' --output-on-failure
```

JUCE Host example (choose Bridge or Pigora targets only when those are in scope):

```bash
python3 tools/mc_build_lane.py run --lane host-TASK --build-dir build-lane-host-TASK -- cmake -S . -B build-lane-host-TASK -DMC_PATCHER_BUILD_JUCE_BRIDGE=ON
python3 tools/mc_build_lane.py run --lane host-TASK --build-dir build-lane-host-TASK -- cmake --build build-lane-host-TASK --target McHost -j 4
```

Do not assume an existing build tree was configured with the current options.
Inspect `CMakeCache.txt` or reconfigure deliberately.
Reserve `build-juce` for serialized integration/deployment through `--shared`.
Its busy lock defers that phase only; never bypass the guard or use another
task's build tree. The examples are not authorization to build or deploy.

## Current portable tests

Check the current CMake source before using this table because names and
coverage can change.

| Test | Primary coverage |
|---|---|
| `ipc_smoke` | Protocol validation, SHM ownership/compatibility, bounds and failure behavior |
| `shm_roundtrip` | Basic shared-memory audio round trip |
| `bridge_pdc_hostfx` | Bridge PDC and hosted-effect timing behavior |
| `instance_claim` | Stable instance ownership/claim semantics |
| `shm_multi_instance` | Multiple independent instances |
| `shm_multich` | Existing multichannel SHM round trip; inspect its configured channel count before making high-channel claims |
| `wet_return_wantret` | Wet-return request/response behavior |
| `click_softness` | Transition/click regression |
| `strip_remove_still_audible` | Audio continuity while removing a strip |
| `fanout_wet_correlation` | Fan-out and wet-path correlation |

Target a subset with CTest regexes, then run the relevant broader suite when
risk warrants it. The `mc_shm_audio_tests` aggregate build target exists for a
bounded SHM audio regression path where direct test execution is constrained;
verify its current dependencies before relying on it.

## Local plug-in integration

`mc_host_load_smoke` and `mc_host_engine_verify` depend on locally installed
test/commercial VST3 plug-ins. They are excluded from normal builds. Configuring
with `-DMC_PATCHER_ENABLE_LOCAL_PLUGIN_TESTS=ON` registers them with CTest;
otherwise build the explicit target and locate/run the produced executable.

Treat a missing local plug-in as an unavailable integration prerequisite, not
as proof of a Host regression. Record which plug-in, format, and path were
actually exercised.

## Graph and WebUI interaction

Before implementing a routing utility, freeze two separate cardinalities: the
number of logical ports shown by the module and the number of edges each port
may accept.  Do not turn connection multiplicity into extra sockets merely
because the engine stores per-edge branch identities.  For example, a Fanout
may expose one aggregate output endpoint with many outgoing edges, while a
Merge may expose one aggregate input endpoint whose incoming edges are assigned
to internal summing branches.  Verify simultaneous audible routes, reconnect
after deletion, state round-trip, and edge-specific removal; a configurable
2..N socket stack or source-pattern check does not prove either contract.

For Frame, Group, Comment, and annotation primitives, freeze the complete
lifecycle and ownership contract before styling: create, edit, move, resize,
delete, undo/redo, save/restore, and container-versus-content deletion.  A
grouping operation must preserve each member's stable engine identity and one
DOM instance; it must not recreate or duplicate a member.  Mixed selections
must state whether deleting the container preserves its contents or recursively
deletes them, and the emitted transaction must match that rule atomically.
Annotation text needs a reserved title area that cannot be covered by enclosed
nodes.  A movable border, clearable text, or green state round-trip alone does
not prove a usable annotation.

Treat persistent container geometry and attached border controls as their own
acceptance axis. Verify that content-driven layout can enlarge but never
silently contract a user-sized Frame, that all four corners respect the content
floor, that the saved bounds survive restore and border movement, and that each
attached Fanout/interface plus its incident wires follows every live resize
frame rather than jumping only after the native state round-trip.

For a collapsed or aggregate Graph endpoint, use one shared endpoint-geometry
function for drawing, hit testing, marquee selection, live rerouting, and drag
preview. A cable that is painted at an aggregate port but selected against its
hidden per-channel coordinates is a failed interaction even when the topology
and screenshot look correct.

When a report concerns Graph wire selection, deletion, or fan-out dragging,
add a deterministic UI regression that invokes the geometry and gesture
functions with multiple channel indices. Assert the emitted action and its
channel range as well as the rendered endpoint. Source-string checks alone do
not prove that converged wires can be selected or that a one-point multichannel
drag reaches one atomic engine mutation. After deployment, keep the exact
physical WKWebView gesture as a separate acceptance layer.

For an aggregate output-to-input connection regression, invoke the actual
input hit-test and drag-finish functions rather than only calling the engine
connection API. Assert that the emitted transaction carries independent source
and destination branch identities and that the engine commits exactly one
complete-width route. A direct engine connection test does not prove that a
collapsed plug-in or a multi-input routing node can be reached by the UI.

When product semantics make a collapsed Graph card itself the aggregate
module, test a drop on the card body as well as on the visible endpoint. For
overlapping cards, the body fallback must select the visually topmost DOM node,
and a known source/destination width mismatch must be rejected before emitting
the native mutation. Endpoint-only tests can stay green while the intended
card-body gesture does nothing or routes to an obscured node.

If a large Host verifier keeps many engine fixtures in one function, run the
built executable directly under the normal shell stack limit in addition to
CTest. Heap-allocate added engines when the direct path reaches
`___chkstk_darwin`; a CTest-only pass can hide a launcher-specific stack-size
difference.

When a collapsed node is dropped onto an aggregate Graph wire, keep that path
separate from ordinary per-channel insertion. The regression must prove that
logical-wire hit testing does not discard the aggregate, the gesture emits a
dedicated aggregate splice action, and the engine replaces the old logical
pair with two complete-width pairs in one rollback-capable transaction. A
green ordinary-wire splice test or a visual insert hint does not cover this
path.

For Bridge format/lifecycle changes, run PluginVal at strictness 5 or higher
when it is already available. Use Steinberg's test host when the change is
specifically about VST3 conformance. These format checks do not prove the live
wet-return path.

## Manual DAW path

Record at minimum:

- DAW and version;
- deployed Bridge build/version and whether the DAW was restarted or rescanned;
- sample rate, block size, negotiated input/output channels, and instance ID;
- Host build and hosted plug-in identity;
- dry/wet state, PDC report, mount behavior, steady state, and editor open/close;
- whether audio, clicks, underruns, deadlocks, state restore, and teardown were
  checked.

A simulator or PluginVal pass is not a substitute when the reported defect
requires DAW -> Bridge -> Host -> Bridge -> DAW.

## Deployment

Deployment is an explicit mutation outside the build tree:

```bash
python3 tools/mc_build_lane.py run --shared --lane integration-TASK --build-dir build-juce -- cmake --build build-juce --target mc_deploy_bridge
python3 tools/mc_build_lane.py run --shared --lane integration-TASK --build-dir build-juce -- cmake --build build-juce --target mc_deploy_host
python3 tools/mc_build_lane.py run --shared --lane integration-TASK --build-dir build-juce -- cmake --build build-juce --target mc_deploy_theme_lab
python3 tools/mc_build_lane.py run --shared --lane integration-TASK --build-dir build-juce -- cmake --build build-juce --target mc_deploy_silk_tape
```

Inspect the CMake deployment scripts for actual destinations and privileges.
Do not manually copy stale artifacts when the project target owns deployment.
Do not run `McHostBumpVersion` unless an intentional new deployed/release build
was requested.

For a live Desktop Host check after `mc_deploy_host`, treat process identity as
a separate gate from bundle identity. Record any running Chlora PID and
executable path before testing. A matching title, version string, deployed asset
checksum, closed window, or blank WebView does not prove that a pre-deployment
process exited or loaded the new resources. Quit normally, assert the old PID is
gone, launch the exact deployed bundle path, and confirm that the new process
path matches it and started after deployment. Verify one visible behavior or
text marker that is unique to the changed assets. If normal Quit leaves a
blank/stuck process after a bounded wait, terminate only that already-validated
stale PID, disclose the forced termination, then repeat the exact-path and
visible-marker checks. Do not involve another DAW merely to prove Host UI.
