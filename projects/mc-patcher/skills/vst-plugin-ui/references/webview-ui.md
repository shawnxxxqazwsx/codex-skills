# WebView / WebUI for Audio Products

Use this file when the UI runs inside `juce::WebBrowserComponent`, a hybrid native+WebView shell, or a designer pipeline that exports HTML/CSS/JS, Rive, Spline, or similar web assets into a plug-in or host.

WebUI is a production path, not a free pass to build a SaaS dashboard. Classify the product first; host consoles still obey [host-console.md](host-console.md). Creative faceplates still obey geometry, signature, and [graphic-composition.md](graphic-composition.md).

## Choose the renderer honestly

| Path | Prefer when | Avoid when |
|---|---|---|
| Native JUCE `LookAndFeel` + custom `Component` | Dense host chrome, low overlay risk, existing C++ widget tree | Designer needs hot-reload 3D/shader faceplates every hour |
| Full-window WebView | Faceplate identity is web/CSS/WebGL-native; frontend owners exist | Tiny utilities where WebView cold-start and host quirks dominate |
| Hybrid shell | Host keeps RT/engine native and paints only the work surface or browser in WebView | Every strip control becomes a separate browser instance |
| Filmstrip / PSD metadata loader | Skeuomorphic knobs already authored as frames | Continuous resize with photoreal assets and no resampling plan |

JUCE 8 treats WebViews as a first-class UI option: hot reload, React/Vue/Svelte or plain HTML/CSS/JS, and WebGL. Official caveats still apply: JUCE does not ship a widget kit for the page; platform WebView engines differ; value formatting often lives in the frontend unless you expose native helpers. Primary source: [JUCE 8 WebView UIs](https://juce.com/blog/juce-8-feature-overview-webview-uis/).

## Architecture that stays musical

```text
AudioProcessor / Host engine (C++)
  -> atomics or bounded lock-free FIFO for meters / spectra
  -> message-thread aggregator or timer
  -> WebBrowserComponent emitEvent / evaluateJavascript / ResourceProvider
  -> HTML/CSS/JS (or React/Vue/Svelte) paint + interaction
  -> nativeFunction / eventListener / Web*Relay back to parameters
```

Never compute layout, allocate JS strings, or call into the WebView from the audio callback.

### Required JUCE options (verify against the repo's JUCE version)

From the official overview and [WebBrowserComponent::Options](https://docs.juce.com/master/classjuce_1_1WebBrowserComponent_1_1Options.html):

- `withNativeIntegrationEnabled` for the JS shim
- `withResourceProvider` for bundled assets and dynamic data
- `withNativeFunction` / `withEventListener` for command and gesture bridges
- Windows: WebView2 backend plus a User Data Folder; CMake `NEEDS_WEBVIEW2` and static loader linking when the project requires it
- Debug: optional localhost/Vite/webpack origin with `allowsOriginIn`
- Release: `goToURL(WebBrowserComponent::getResourceProviderRoot())` and BinaryData / zip assets

Parameter wiring: `WebSliderRelay` + `WebSliderParameterAttachment` (and toggle/combo equivalents). JS side uses `Juce.getSliderState` / native functions. Keep gesture begin/end paired so host automation records correctly.

## Design rules unique to WebUI

1. **Lock zones before CSS art.** Grid areas, strip width, fader wells, and browser fraction are product geometry. Do not "improve" them with flex experiments during a visual pass.
2. **One material language across the page.** Cream shell + black wells, anodized metal, phosphor glass, surgical overlay — pick one. CSS cards, drop-shadow stacks, and marketing gradients are not a material language.
3. **Tokens live in one place.** Prefer `:root` CSS variables or a tiny theme module that mirrors the C++/design-token names. Do not invent a second brand in the WebView while native chrome keeps another.
4. **Meters are data, not decoration.** Continuous or segmented fills must document peak/RMS/GR ballistics. Idle meters stay geometrically present; never fake live activity in a "final" mock that will be implemented as static CSS.
5. **Motion budget.** Prefer CSS/WebGL motion that explains level, selection, or processing. Provide `prefers-reduced-motion` fallbacks. Cap frame cost when the editor is hidden.
6. **Hit targets beat pixel chrome.** Narrow visual rails need larger invisible hit regions. Touch and trackpad need tested drag thresholds inside the WebView.
7. **Text is musician language.** Units, bypass, mute, solo, route. Reject webhook / dashboard / KPI copy.
8. **Arbitrate printable shortcuts and text focus.** An unmodified letter shortcut must not auto-focus a text field that accepts the same letter while also expecting the repeated key to remain a command. Keep the shortcut in non-interactive context and let a deliberate click transfer ownership to text entry, or choose a modifier/non-printable shortcut. Verify the transition in the real WebView: open/toggle from a non-interactive surface, repeat the shortcut without focus moving, then click the field and confirm the same character is typed rather than intercepted.

## Hybrid host pattern (validated by MC Host work)

When a standalone host mixes native engine UI and WebView:

```text
┌─ optional Web chrome (unscaled) ──────────────────────────────────────┐
├─ Web browser column ─┬─ native or Web work surface (may be scaled) ───┤
│  catalogue / search  │  inserts · mixer · routing · master            │
└──────────────────────┴────────────────────────────────────────────────┘
```

Rules learned from real host redesigns:

- Product class remains **host console**. Clustered strips beat Immersive shaders.
- Functional zone order is locked unless the brief explicitly moves a region. Art, materials, chamfers, and fader caps may change aggressively inside those zones.
- Selection, mute, solo, and bridge health need non-hue cues that survive cream/black material shifts.
- Telemetry stays secondary. Do not rebuild PERF as a hero widget in HTML.
- Drag from WebView into native Components is a separate engineering problem; do not assume DOM drag equals JUCE drag.
- Platform quirks are part of the design: WKWebView may swallow modifier keys, suppress `dblclick` after `preventDefault` on `pointerdown`, ignore `window.prompt`, or finish-load more than once. Design interactions that do not depend on fragile browser prompts.

## Complex graphic stacks in the browser

| Stack | Good fit | Guardrails |
|---|---|---|
| Plain HTML/CSS/JS | Host consoles, dense strips, token-driven materials | Keep DOM shallow; virtualize huge lists |
| React / Vue / Svelte | Parameter-heavy faceplates, component libraries | Bundle size, boot time, and host reopen cost |
| Canvas 2D / WebGL / Three.js | Immersive analyzers and creative heroes | One hero family; RT-safe data only; reduced-motion still |
| [Rive](https://rive.app/) | Stateful 2D motion design owned by a designer | Map artboard inputs to parameters; profile CPU |
| [Spline](https://spline.design/) | Interactive 3D faceplate moments | Keep 3D as signature, not every knob; provide flat fallback |
| Visual exporters such as [Faceplate UI Designer](https://marketplace.juce.com/products/faceplate_ui_designer) | Rapid WebView2 bundle iteration | Treat export as starting point; still pass geometry and a11y gates |

ADC practitioner path for designer-owned web motion into JUCE WebUI: [Ryan Wardell, ADCx Gather 2025](https://conference.audio.dev/accelerate-ui-development-seamless-designer-developer-collaboration-with-web-tools-ryan-wardell/). Companion setup material often referenced from that talk: [juce-webview-tutorial](https://github.com/JanWilczek/juce-webview-tutorial).

## Complex graphic effect cookbooks

Use these sites when implementing materials, meters, masks, shaders, or audio-reactive heroes inside a WebView. Prefer official docs and teaching sites over SEO roundups. Still obey product-class gates: a host console rarely needs a fullscreen shader.

### CSS / SVG material and instrument chrome

| Site | Use for | Notes |
|---|---|---|
| [MDN: CSS compositing and blending](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Compositing_and_blending) | Panel overlays, filament on metal, ink on phosphor | `background-blend-mode` vs `mix-blend-mode`; watch stacking contexts |
| [MDN: CSS filter effects](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Filter_effects) | Soft focus, glow restraint, SVG filter chains | Prefer subtle material cues over Instagram filters |
| [MDN: `backdrop-filter`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/backdrop-filter) | Frosted glass over analyzers or modal sheets | Needs partial transparency; mask ancestors can kill the effect |
| [web.dev: blend modes](https://web.dev/learn/css/blend-modes) | Practical blend recipes and isolation | Good companion to MDN when choosing modes |
| [web.dev: backdrop-filter](https://web.dev/articles/backdrop-filter) | OS-style frosted panels | Profile cost on dense strip banks |
| [MDN: CSS masking](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Masking) | Donut meters, arch cutouts, irregular hit silhouettes | Combine with gradients; keep hit targets separate from mask art |
| [MDN: `conic-gradient()`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/gradient/conic-gradient) | Circular meters, knobs, phase rings | Drive stops from CSS variables / `@property` |
| [MDN: `@property`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@property) | Animatable meter/progress custom properties | Typed custom props enable smooth CSS transitions |
| [MDN: SVG filter primitives](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/feDisplacementMap) | Turbulence, displacement, bevel-like treatments | Start from MDN element pages (`feTurbulence`, `feGaussianBlur`, etc.) |
| [MDN: advanced styling effects](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Advanced_styling_effects) | Shadows, filters, blend primer | Teaching overview before diving into modules |

### Canvas, WebGL, and shader learning

| Site | Use for | Notes |
|---|---|---|
| [MDN: Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API) | 2D meters, scopes, EQ curves, custom knobs | Lowest-risk custom drawing path in WebView |
| [MDN: WebGL API](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API) | GPU hero surfaces and texture uploads | Check host WebView WebGL availability |
| [WebGL Fundamentals](https://webglfundamentals.org/) | Vertex/fragment mental model without framework magic | Prefer [WebGL2 Fundamentals](https://webgl2fundamentals.org/) when targeting WebGL2 |
| [The Book of Shaders](https://thebookofshaders.com/) | Noise, patterns, shaping, generative fragment looks | Map 3–5 uniforms to parameters; provide reduced-motion fallback |
| [Shadertoy](https://www.shadertoy.com/) | Inspiration and GLSL snippets | Exploration only; strip demo noise before shipping in a plug-in |
| [Three.js docs](https://threejs.org/docs/) | Scene-graph heroes, materials, `DataTexture` spectrum feeds | One hero scene; dispose on editor close |
| [noisehack: music visualizer](https://noisehack.com/build-music-visualizer-web-audio-api/) | Spectrum → texture → fullscreen fragment shader pattern | Adapt data source to JUCE analyzer events, not only Web Audio |
| [Codrops: Three.js + GSAP audio visualizer](https://tympanus.net/codrops/2025/06/18/coding-a-3d-audio-visualizer-with-three-js-gsap-web-audio-api/) | End-to-end creative WebGL faceplate case | Practitioner article; profile before host shipping |

### Audio → picture data paths

In a JUCE WebView, prefer C++ analyzer snapshots pushed over events/ResourceProvider. The following still teach the **picture side** of the pipeline:

| Site | Use for | Notes |
|---|---|---|
| [MDN: Visualizations with Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Visualizations_with_Web_Audio_API) | Oscilloscope and frequency-bar drawing loops | Replace `AnalyserNode` reads with host-fed arrays when inside a plug-in |
| [MDN: `AnalyserNode`](https://developer.mozilla.org/en-US/docs/Web/API/AnalyserNode) | FFT size, smoothing, byte/float buffers | Useful vocabulary even when analysis stays in C++ |
| Three.js `DataTexture` / WebGL `texImage2D` examples in the shader links above | Pack spectrum/waveform rows into GPU textures | Coalesce updates; never block the audio thread |

### Designer-owned motion / 3D runtimes

| Site | Use for | Notes |
|---|---|---|
| [Rive Web runtime](https://rive.app/docs/runtimes/web/web-js) | Embed `.riv` on a canvas, HiDPI resize | Bind state-machine inputs to parameters |
| [Rive state machines (web)](https://rive.app/docs/runtimes/web/state-machines) | Hover/press/bypass/mode choreography | Prefer data-binding over brittle frame seeking |
| [Rive parameters](https://rive.app/docs/runtimes/web/rive-parameters) | Constructor options and lifecycle | Dispose/reset when the editor closes |
| [Spline](https://spline.design/) + viewer embed docs on that site | Interactive 3D moments | Keep as signature, not every control; flat CSS fallback |
| [Faceplate UI Designer](https://marketplace.juce.com/products/faceplate_ui_designer) | Component canvas → WebView2 bundle | Still run geometry/a11y gates after export |

### Effect → recommended first source

| Desired effect | Start here | Then |
|---|---|---|
| Recessed fader well / beveled cap | CSS gradients + inset shadows in [graphic-composition.md](graphic-composition.md) | MDN filter/blend only if material needs it |
| Circular GR / phase meter | [conic-gradient](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/gradient/conic-gradient) + [`@property`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@property) | Canvas if needle physics get complex |
| Arch / cable cutouts | [CSS masking](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Masking) or SVG paths | Keep separate larger hit regions |
| Frosted overlay on spectrum | [`backdrop-filter`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/backdrop-filter) | Disable under reduced-motion / weak GPUs |
| Phosphor scope / bar spectrum | [MDN Web Audio visualizations](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Visualizations_with_Web_Audio_API) drawing loop | Feed arrays from JUCE |
| Plasma / noise / fractal hero | [Book of Shaders](https://thebookofshaders.com/) | [fractal-visualizers.md](fractal-visualizers.md) mapping rules |
| 3D creative body | [Three.js docs](https://threejs.org/docs/) + Codrops case | One scene; pause when hidden |
| Designer-animated knob/switch | [Rive web docs](https://rive.app/docs/runtimes/web/web-js) | Parameter/state-machine binding |

### Implementation discipline for effects

1. Choose the lightest stack that can express the signature (CSS → Canvas → WebGL/Three → Rive/Spline).
2. Drive visuals from product tokens and 3–5 interpretable parameters or analyzer channels.
3. Cap DPR, FPS, and shader cost; stop or idle when the editor is hidden.
4. Provide `prefers-reduced-motion` and a static frame.
5. Verify inside the real WebView engine (WKWebView / WebView2), not only Chrome desktop.

## WebUI optimization cookbooks

Plug-in and host WebViews share a machine with the DAW and the audio callback. Optimize for **editor open cost**, **steady-state CPU/GPU while mixing**, and **IPC volume**, not only Lighthouse scores in a browser tab.

### Rendering pipeline (CSS / DOM)

| Site | Use for |
|---|---|
| [web.dev: Rendering performance](https://web.dev/articles/rendering-performance) | Pixel pipeline: JS → Style → Layout → Paint → Composite; ~10 ms animation budget |
| [web.dev: High-performance CSS animations](https://web.dev/articles/animations-guide) | Prefer `transform` / `opacity`; avoid layout-triggering animation props |
| [web.dev: Compositor-only properties & layer count](https://web.dev/articles/stick-to-compositor-only-properties-and-manage-layer-count) | Promote layers sparingly; `will-change` is not free |
| [web.dev: Simplify paint complexity](https://web.dev/articles/simplify-paint-complexity-and-reduce-paint-areas) | Shrink paint areas; blur/shadow cost; Paint Flashing / Paint Profiler |
| [CSS Triggers](https://csstriggers.com/) | Quick lookup of which properties force layout/paint/composite |

Audio-host rules of thumb:

- Animate fader caps, selection edges, and mode settles with `transform`/`opacity` when possible.
- Keep expensive `box-shadow`, `filter`, and `backdrop-filter` off rapidly updating meter chrome; put them on static shells.
- Do not `will-change` every strip. Promote only proven hot layers after profiling.
- Virtualize long plugin trees; avoid 16× deep DOM trees that restyle on every meter tick.

### Canvas / WebGL

| Site | Use for |
|---|---|
| [web.dev: Canvas performance](https://web.dev/articles/canvas-performance) | Offscreen pre-render, fewer state changes, `requestAnimationFrame` |
| [MDN: `requestAnimationFrame`](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame) | VSync-tied loops; pause when hidden; use frame timestamps |
| [MDN: WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices) | Avoid sync `getError`/`getParameter` in the hot path; batch draws; smaller back buffers |
| [WebGL Fundamentals](https://webglfundamentals.org/) / [WebGL2 Fundamentals](https://webgl2fundamentals.org/) | Correct mental model before micro-optimizing frameworks |
| Cap DPR | Prefer `Math.min(devicePixelRatio, 2)` (or lower) for heroes; full DPR only where sharpness is required |

### Bundle and framework cost

| Site | Use for |
|---|---|
| [Developer Way: Bundle size investigation](https://www.developerway.com/posts/bundle-size-investigation) | Analyzer-driven dependency cuts (Vite/Rollup visualizer workflow) |
| Vite / Rollup tree-shaking practices | Named ESM imports; avoid `import *` of large libs; mark `sideEffects` honestly |
| React code-splitting | Lazy-load settings/about/debug panels; keep the first faceplate paint lean |

For plain HTML/CSS/JS hosts (MC Host style), prefer **no framework** on the critical path. If React/Vue is required, measure gzipped first paint and editor reopen time in the real WebView.

### JUCE ↔ WebView IPC and lifecycle

| Source | Guidance |
|---|---|
| [JUCE 8 WebView overview](https://juce.com/blog/juce-8-feature-overview-webview-uis/) | Relays for parameters; ResourceProvider for assets/data; hot reload is Debug-only |
| [JUCE forum: emitEvent bottleneck](https://forum.juce.com/t/webview-components-emitevent-bottleneck/66748) | Large `emitEvent` JSON stringify/escape can dominate; keep payloads small |
| [JUCE forum: WebBrowserComponent & ValueTrees](https://forum.juce.com/t/the-new-webbrowsercomponent-and-valuetrees/61061) | Prefer small observer events + ResourceProvider fetch for bulky/binary data |
| [WebBrowserComponent::Options](https://docs.juce.com/master/classjuce_1_1WebBrowserComponent_1_1Options.html) | Default blank-on-hide saves resources; `withKeepPageLoadedWhenBrowserIsHidden` trades memory for reopen speed — choose deliberately |

Practical IPC policy:

```text
parameters / gestures  -> Web*Relay or small nativeFunction calls
meters @ UI rate       -> coalesced snapshots (e.g. 20–60 Hz), not per-sample
spectra / images       -> ResourceProvider or shared buffer pattern, not giant emitEvent JSON
debug telemetry        -> on demand only
```

Never call into the WebView from the audio thread. Drop or coalesce visualization frames under load.

### Platform WebView (startup, memory, process)

| Site | Use for |
|---|---|
| [Microsoft: WebView2 performance](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/performance) | Cold start, User Data Folder location, share environments, avoid redundant instances, content weight |
| WebView2 Feedback (startup threads) | Hidden pre-warm can hide init cost; measure `EnsureCoreWebView2` / first navigation on target machines |
| Apple WKWebView / WebKit behavior (verify per OS) | Background throttling of timers/`rAF`; test editor hide/show and DAW window occlusion |

Windows checklist: Evergreen WebView2 runtime, UDF on a fast local disk, one environment when multiple views exist, do not put the first-run critical path behind an uninitialized WebView if a native splash/shell can show sooner.

### Symptom → first move

| Symptom | First move | Source cluster |
|---|---|---|
| Janky fader/selection motion | Switch animation to `transform`/`opacity`; Paint Flash | web.dev rendering / animations |
| Meter updates stall UI | Coalesce IPC; separate meter paint from layout; lower Hz | JUCE IPC forums + canvas perf |
| Editor open feels multi-second | Preload/reuse WebView; shrink bundle; ResourceProvider over localhost | WebView2 performance + bundle guides |
| GPU fans on idle mixer | Pause WebGL/`rAF` when hidden; kill decorative blur on strips | MDN WebGL practices + paint guides |
| Large spectrum push spikes | Stop JSON `emitEvent`; use ResourceProvider / binary path | JUCE WebView forum threads |
| Many strips + filters | Flatten DOM; virtualize lists; ration `backdrop-filter` | web.dev paint / compositor articles |

### Optimization acceptance

- [ ] Animation hot path avoids layout thrash (profiled, not assumed)
- [ ] Meter/spectrum rate and payload size are bounded and documented
- [ ] WebGL/Canvas stops or idles when the editor is closed/occluded
- [ ] Production bundle is measured (raw + gzip) and free of Debug-only servers
- [ ] WebView hide/show policy is intentional (blank vs keep-alive)
- [ ] Standalone + one real DAW host checked under audio load

## Case anchors

| Case | What to steal | What not to copy |
|---|---|---|
| [JUCE WebViewPluginDemo](https://juce.com/blog/juce-8-feature-overview-webview-uis/) | ResourceProvider, Relays, spectrum push, hot reload | Demo aesthetics as a product identity |
| [Sound-Field](https://github.com/mbarzach/Sound-Field) | React + Three.js hero viz with Web Relays and analyzer events | Putting a 3D blob on a mixer shell |
| Faceplate designer exports | Drag-drop WebView2 bundles and parameter IDs | Assuming marketplace widgets pass host-console density gates |
| MC Host Web surface | Cream tooling shell, black instrument wells, CSS variables, locked workspace grid | Marketing cards, neon strip gel, fake meters |
| Filmstrip→metadata pipeline ([Playful Tones / ADC](https://playfultones.com/blog/reflections-on-building-a-pixel-perfect-ui-pipeline-in-juce-applications---part-1)) | Structured design source of truth, hitbox masks, sort layers | Manual magic `setBounds` transcription |

## Implementation checklist

- [ ] Backend and frontend share parameter IDs, units, and normalized ranges
- [ ] Gesture start/end and automation handoff are tested from the WebView
- [ ] Analyzer traffic is coalesced; overflow policy is explicit
- [ ] Debug localhost origin and Release ResourceProvider both work
- [ ] Windows WebView2 runtime / macOS WebKit / Linux WebKit2 expectations are documented for distribution
- [ ] Overlay and focus behavior with native sibling Components is verified
- [ ] Keyboard focus, names, and values are exposed; decorative canvases are excluded or summarized
- [ ] Screenshots captured at minimum size, default size, and a HiDPI scale factor
- [ ] Optimization acceptance items above are checked when the UI is animated, meter-heavy, or WebGL-backed

## Acceptance gate

- The WebUI still reads as the chosen product class.
- Geometry and interaction survive the skin.
- For overlapping interactive layers, fragment or source-pattern checks are not sufficient acceptance. Mount the composed surface or exercise the real WebView and verify hit-testing/z-order, focus ownership, pointer-capture loss/cancellation, context switches, and teardown leave no stale editor or gesture state.
- For marquee and higher-order operations such as grouping, duplicate, delete, or move, include attached handles/ports/sidecars that the same rectangle can hit. Filter non-ownable auxiliary elements before inferring parentage or committing the operation, and verify the composed selection payload rather than only the ideal node-only case.
- For create/edit popovers, test the empty-commit contract separately: an empty new value may cancel creation, while an empty edit often means clear/remove and must not be silently discarded.
- No audio-thread WebView or JS work.
- Hot-reload is a development convenience, not a substitute for host verification.
- Complex graphics have one signature system and a reduced-motion path.
- Steady-state and open-cost budgets are credible under DAW load (see optimization cookbooks).
