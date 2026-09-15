# Audio Plug-in UI Reference Library

Use references to identify transferable interaction and graphic ideas, not to copy another product's skin. Browse official product and framework pages before describing a current feature or version. Research date context for this library refresh: August 2026.

## Layout archetypes

| Archetype | Structure | Good fit |
|---|---|---|
| Hero | One dominant control or processing view with a small supporting set | Filter, pitch, lo-fi, or focused creative effect |
| Asymmetric | Two or three clusters with deliberate negative space | Modulation and multi-effect workflows |
| Minimal | A few essential controls with very clear values and state | Utility, simple dynamics, compact filter |
| Immersive | Processing view occupies most of the editor and controls frame it | EQ, spectral tools, reverb, or delay when the view carries information |
| Clustered | Proximity groups organize a dense but stable surface | Channel strip, amp, distortion, synth, or host bank |

Choose a dominant archetype. A secondary structure may support a real workflow; the rule is hierarchy, not purity. A host often combines a Clustered strip bank with Minimal shell chrome.

Practitioner definitions and examples: [BeatConnect layout patterns](https://docs.beatconnect.com/design/layout-patterns).

## Case library — native faceplates and consoles

| Product house | Transferable strength | Avoid copying blindly |
|---|---|---|
| [FabFilter](https://www.fabfilter.com/) | Processing display as direct manipulation, strong feedback, resizing, undo/A-B consistency | Feature density inappropriate for a small effect |
| [Valhalla DSP](https://valhalladsp.com/) | Few controls, clear hierarchy, memorable color and typography | Minimalism that omits feedback needed by the algorithm |
| [Soundtoys](https://www.soundtoys.com/) | Material personality, tactile controls, recognizable silhouette | Fixed or decorative hardware conventions that reduce scaling and accessibility |
| [oeksound](https://oeksound.com/) | Live processing visualization plus progressive disclosure | Turning every advanced feature into permanent main-panel chrome |
| [Klanghelm](https://klanghelm.com/) | Metering craft and coherent hardware-adjacent themes | Ornament that competes with values and state |
| [u-he](https://u-he.com/) | Dense tools with learnable spatial memory and theming | Contact-sheet density without strong groups |
| [Arturia](https://www.arturia.com/) | Educational hardware mapping and material storytelling | Skeuomorphism with tiny hit targets or illegible fixed text |
| [Tokyo Dawn Labs](https://www.tokyodawn.net/tokyo-dawn-labs/) | Restrained, technical clarity and informative metering | A generic settings-panel grid when the product needs character |
| [Xfer Records](https://xferrecords.com/) | Intentional synth density with a clear oscillator focus | Copying tab and control counts without the same workflow |
| [Baby Audio](https://babyaud.io/) | Thick chamfers joining light shell to deep black wells; sparse colorful filaments; modern instrument silhouette | Exact radii, logos, or marketing layouts pasted onto a dense host IA |
| [Bitwig The Grid](https://www.bitwig.com/the-grid/) | Neutral patch field, restrained category identity, readable ports and signals across a dense modular graph | Copying its module colors or visual identity instead of adapting the category/neutral relationship |
| [Kilohearts Snap Heap](https://kilohearts.com/docs/snap_heap) | Consistent modular lane anatomy, compact module headers, and hierarchy that survives serial/parallel routing | Importing the complete Snapin card system into a node graph with different interaction needs |
| [Ableton Live](https://www.ableton.com/en/manual/first-steps/#theme-colors) | Treating tone, brightness, intensity, hue, grid visibility, and high contrast as separable palette axes | Assuming a user-adjustable DAW theme is a finished product-specific art direction |

When a user says "FabFilter-style", "Valhalla-style", or "Baby Audio-style," translate it into behavior and material strategy: direct manipulation and feedback; compact all-visible controls and strong identity; or chamfered shell/well contrast with restrained filaments. Do not reproduce trademarks, exact artwork, or a confusingly similar faceplate.

## Case library — WebUI / WebView

| Case | Stack | Transferable strength | Guardrail |
|---|---|---|---|
| [JUCE WebViewPluginDemo](https://juce.com/blog/juce-8-feature-overview-webview-uis/) | React + JUCE Relays | ResourceProvider, hot reload, spectrum push, parameter attachments | Demo look is not a product identity |
| [Sound-Field](https://github.com/mbarzach/Sound-Field) | React + Three.js in JUCE 8 WebView | Creative WebGL hero with analyzer events and Web Relays | Do not put immersive 3D on a mixer shell |
| [Faceplate UI Designer](https://marketplace.juce.com/products/faceplate_ui_designer) | Visual HTML/CSS/JS exporter for WebView2 | Rapid bundle iteration and parameter IDs | Exported widgets still need geometry and host gates |
| [juce-webview-tutorial](https://github.com/JanWilczek/juce-webview-tutorial) | Plain/web tutorial series | Setup, ResourceProvider, distribution prerequisites | Follow current JUCE docs for API drift |
| ADC Wardell Web Tools talk | Rive + Spline + JUCE WebUI | Designer-owned motion/3D with live iteration | Profile cost; keep one signature system |
| MC Host Web surface (repo pattern) | Plain HTML/CSS/JS in hybrid shell | Locked workspace grid, CSS tokens, cream shell + black wells, instrument faders | Functional zones stay host-console; art may move |

Deep rules for these paths: [webview-ui.md](webview-ui.md) and [graphic-composition.md](graphic-composition.md).

## Cross-domain research pools

Use these pools to widen visual judgment, not to turn an audio tool into a
website. Follow the wide-scan and layer-transfer rules in
[palette-research.md](palette-research.md).

| Pool | Starting sources | What to extract |
|---|---|---|
| Semantic design systems | [Material 3 theming](https://developer.android.com/codelabs/m3-design-theming), [Adobe Spectrum color](https://spectrum.adobe.com/page/color-fundamentals/), [Spectrum tokens](https://spectrum.adobe.com/page/design-tokens/), [Carbon color](https://v10.carbondesignsystem.com/guidelines/color/overview/) | Role-based tokens, surface ladders, interaction states, accessible contrast, theme architecture |
| Curated web and editorial discovery | [Siteinspire](https://www.siteinspire.com/) and the original sites it links to | Contemporary palette rhythm, typography, grids, negative space, transitions, and visual voice; verify the original page before using it |
| Professional visual tools | Official pages and manuals for current 3D, video, CAD, mapping, scientific, data, and developer tools | Dense hierarchy, graph navigation, inspectors, search, multiscale views, long-session legibility |
| Industrial and physical design | Official product photography and manuals for instruments, cameras, test gear, broadcast equipment, furniture, transportation, packaging, and signage | Material boundaries, tactile affordance, labeling, state lamps, accent placement, durable identity |
| Culture and image systems | Architecture studios, museums, fashion/editorial work, print, film titles, photography, and generative art from attributable original sources | One concrete motif, colour temperature, composition, texture, or motion idea |

Design-system documentation is evidence for roles and accessibility, not proof
that its default visual style fits the product. Curated galleries are useful for
divergent discovery, not proof that a spectacular page has usable application
interaction. Maintain one direct operational analogue in every deep shortlist.

## Product-to-layout starting points

```text
Utility -> Minimal
EQ or spectral processor -> Immersive or Clustered, depending on direct graph editing
Compressor -> Minimal or Clustered with a clear gain-reduction story
Delay or reverb -> Hero or Immersive when visualization explains time/space
Distortion or amp -> Clustered with one lead Drive or Gain control
Modulation -> Hero or Asymmetric
Host mixer -> Clustered bank plus Minimal chrome
WebUI creative viz -> Immersive/Hero only when the display explains processing
WebUI host shell -> Clustered/Minimal; materials from graphic-composition, not SaaS cards
```

These are prompts for exploration, not category rules. The primary job, control count, and signature decide the final structure.

## Design and engineering sources

### Plug-in-specific craft

- [BeatConnect layout patterns](https://docs.beatconnect.com/design/layout-patterns) — archetype vocabulary; practitioner guidance
- [BeatConnect anti-patterns](https://docs.beatconnect.com/design/anti-patterns) — crowding, hierarchy, naming, settings-panel failure modes
- [BeatConnect choosing visualizers](https://docs.beatconnect.com/design/choosing-visualizers) — match viz family to personality; skip viz when it adds no value
- [Voger Design: synth UX patterns](https://vogerdesign.com/blog/basic-ux-patterns-in-the-development-of-synthesizer-plugins-awesome/) — control size, frequency of use, platform checks
- [Matt Medley: UX for Power, Not Politeness](https://medley.ltd/blog/ux-for-power-not-politeness/) — interaction density and expert music tools

### WebUI, motion, and designer pipelines

- [JUCE 8 Feature Overview: WebView UIs](https://juce.com/blog/juce-8-feature-overview-webview-uis/) — official architecture, Relays, ResourceProvider, caveats
- [WebBrowserComponent](https://docs.juce.com/master/classjuce_1_1WebBrowserComponent.html) and [Options](https://docs.juce.com/master/classjuce_1_1WebBrowserComponent_1_1Options.html)
- [ADC: web tools and JUCE WebUI (Ryan Wardell)](https://conference.audio.dev/accelerate-ui-development-seamless-designer-developer-collaboration-with-web-tools-ryan-wardell/) — Rive/Spline collaboration patterns
- [Rive Web runtime](https://rive.app/docs/runtimes/web/web-js), [state machines](https://rive.app/docs/runtimes/web/state-machines), [Spline](https://spline.design/) — designer-owned 2D/3D interactive assets
- [Faceplate on JUCE Marketplace](https://marketplace.juce.com/products/faceplate_ui_designer) — WebView2 visual export workflow
- [Playful Tones pixel-perfect JUCE pipeline](https://playfultones.com/blog/reflections-on-building-a-pixel-perfect-ui-pipeline-in-juce-applications---part-1) — PSD/metadata, hitboxes, sort layers
- [ADC: PSD to DAW](https://conference.audio.dev/psd-to-daw-building-a-pixel-perfect-ui-pipeline-bence-kovacs-adc-2025/) — associated talk listing

### WebUI complex graphic effect cookbooks

Primary index with effect→source routing: [webview-ui.md § Complex graphic effect cookbooks](webview-ui.md#complex-graphic-effect-cookbooks).

- CSS/SVG: [MDN compositing](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Compositing_and_blending), [filters](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Filter_effects), [masking](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Masking), [`conic-gradient`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/gradient/conic-gradient), [`@property`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@property), [`backdrop-filter`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/backdrop-filter), [web.dev blend modes](https://web.dev/learn/css/blend-modes)
- Canvas/WebGL: [MDN Canvas](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API), [WebGL Fundamentals](https://webglfundamentals.org/), [WebGL2 Fundamentals](https://webgl2fundamentals.org/), [Book of Shaders](https://thebookofshaders.com/), [Three.js docs](https://threejs.org/docs/), [Shadertoy](https://www.shadertoy.com/) (inspiration only)
- Audio→picture: [MDN Web Audio visualizations](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Visualizations_with_Web_Audio_API), [noisehack visualizer](https://noisehack.com/build-music-visualizer-web-audio-api/), [Codrops Three.js audio viz](https://tympanus.net/codrops/2025/06/18/coding-a-3d-audio-visualizer-with-three-js-gsap-web-audio-api/)

### WebUI optimization cookbooks

Primary index with symptom→fix routing: [webview-ui.md § WebUI optimization cookbooks](webview-ui.md#webui-optimization-cookbooks).

- Rendering: [web.dev rendering performance](https://web.dev/articles/rendering-performance), [CSS animations](https://web.dev/articles/animations-guide), [compositor layers](https://web.dev/articles/stick-to-compositor-only-properties-and-manage-layer-count), [paint complexity](https://web.dev/articles/simplify-paint-complexity-and-reduce-paint-areas), [CSS Triggers](https://csstriggers.com/)
- Canvas/WebGL: [web.dev canvas performance](https://web.dev/articles/canvas-performance), [MDN rAF](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame), [MDN WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices)
- Bundles: [Developer Way bundle investigation](https://www.developerway.com/posts/bundle-size-investigation)
- Hosted WebView: [Microsoft WebView2 performance](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/performance), [JUCE emitEvent bottleneck thread](https://forum.juce.com/t/webview-components-emitevent-bottleneck/66748), [JUCE ResourceProvider guidance thread](https://forum.juce.com/t/the-new-webbrowsercomponent-and-valuetrees/61061)

### Color and distinctive graphic systems

- [Ottosson: Oklab](https://bottosson.github.io/posts/oklab/) — perceptual foundation
- [Evil Martians: OKLCH in CSS](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl) — token ramps and gamut-aware CSS
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) and [non-text contrast](https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html) — contrast heuristics
- [Anthropic frontend-design skill](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) — anti-templated identity, two-pass critique; adapt, do not import web-marketing heroes into mixers

### JUCE native pipeline

- [JUCE LookAndFeel tutorial](https://juce.com/tutorials/tutorial_look_and_feel_customisation/) and [LookAndFeel_V4 API](https://docs.juce.com/develop/classjuce_1_1LookAndFeel__V4.html)
- [JUCE AudioProcessorEditor API](https://docs.juce.com/master/classjuce_1_1AudioProcessorEditor.html) for resize and host scale behavior
- [JUCE AccessibilityHandler API](https://docs.juce.com/master/classjuce_1_1AccessibilityHandler.html)

Treat third-party talks and blogs as implementation experience, not normative requirements. Verify API behavior in the JUCE version actually used by the repository.

## General interaction foundations

| Resource | Application to plug-ins |
|---|---|
| Norman, *The Design of Everyday Things* | Affordance, mapping, feedback, and control-to-result relationship |
| Cooper et al., *About Face* | Goal-directed design for expert workflows |
| Krug, *Don't Make Me Think* | Scanability during time-constrained mixing |
| Schoger and Wathan, *Refactoring UI* | Digital hierarchy, spacing, and contrast; adapt rather than copying web-card patterns |
| Industrial HMI progressive disclosure (e.g. ISA-101 style guides) | Host diagnostics hierarchy only; never force SCADA aesthetics onto creative faceplates |

General UI guidance is insufficient by itself. Combine it with audio parameter semantics, automation, metering, host behavior, real-time constraints, and musician testing.

## Research gaps

- There is no single normative standard for audio plug-in typography, control diameter, or faceplate density.
- Accessibility remains uneven across plug-in products and hosts; test the actual wrapper and assistive technology.
- DPI and resize behavior remain host- and platform-sensitive.
- Bitmap filmstrips, WebView UIs, and GPU rendering have different failure modes; choose from the product and host matrix, not fashion.
- WebView best practices are still evolving after JUCE 8; prefer official docs over tutorial residue when APIs disagree.
