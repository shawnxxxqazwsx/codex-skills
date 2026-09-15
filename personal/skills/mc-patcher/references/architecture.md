# MC Patcher architecture references

Use this file only for architecture, plug-in-hosting, or protocol questions. Re-check external documentation before relying on version-sensitive behavior.

## Repository ownership map

| Area | Owns |
|---|---|
| `shared/` | Protocol headers, shared-memory rings, instance identity, layout helpers |
| `plugins/bridge/` | DAW-facing VST3/standalone bridge, bus negotiation, state, PDC, IPC attachment |
| `apps/host/` | Standalone application, JUCE hosting, graph, mixer/Q-Link UI, device/Bridge endpoints |
| `tests/` | Portable protocol/audio regressions and opt-in local plug-in integration probes |
| `docs/` | Architecture decisions, inventories, and user/developer notes |

Verify this map against the current tree before changing ownership.

## Product precedents

| Product or framework | Relevant idea | Boundary for this project |
|---|---|---|
| Flux SampleGrabber/SamplePush | DAW insert separated from a standalone consumer; discovery plus multichannel transport | MC Patcher needs a bidirectional wet return, not analysis-only capture |
| AudioGridder | Bridge/server split, latency compensation, plug-in isolation | Local SHM is the primary transport; network-first UI/audio is not a v1 requirement |
| Fiedler Armada | Multi-mono wrapping and linked parameter groups across many channels | Treat as a later hosting mode, not the base Bridge architecture |
| Waves WaveShell | One factory/container exposes many component IDs | Cache stable identities and tolerate shell-path/version changes |
| JUCE `AudioProcessorGraph` | Nodes, connections, graph I/O, hosted `AudioProcessor` instances | Topology changes and preparation must not synchronously stall the audio callback |

## VST3/JUCE implementation anchors

- VST3 processor and controller may be separate and communicate through connection points.
- Negotiate buses while inactive and handle hosts that provide null pointers for inactive buses.
- Empty or special process calls can still carry parameter/state work; do not assume every call contains audio.
- Keep the JUCE `AudioProcessor` wrapper thin enough that transport and graph logic remain testable outside a DAW.
- Discover actual plug-in IDs and format metadata through the hosting API; do not scrape display paths as identity.

Primary documentation:

- [Steinberg VST3 processing FAQ](https://steinbergmedia.github.io/vst3_dev_portal/pages/FAQ/Processing.html)
- [Steinberg VST3 Plug-in Test Host](https://steinbergmedia.github.io/vst3_dev_portal/pages/What+is+the+VST+3+SDK/Plug-in+Test+Host.html)
- [JUCE AudioProcessorGraph tutorial](https://juce.com/tutorials/tutorial_audio_processor_graph/)
- [Tracktion PluginVal](https://github.com/Tracktion/pluginval)
- [Real-time audio programming principles](https://www.rossbencina.com/code/real-time-audio-programming-101-time-waits-for-nothing)
- [Flux SampleGrabber documentation](https://doc.flux.audio/mira/SamplePush_SampleGrabber.html)
- [AudioGridder source](https://github.com/apohl79/audiogridder)

For a current technical claim, open the relevant primary page before citing it.
