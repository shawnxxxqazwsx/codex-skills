---
name: vst-plugin-ui
description: Design, review, and implement user interfaces for audio plug-ins and standalone audio hosts — VST3/AU/CLAP editors, JUCE LookAndFeel, WebView/WebUI (HTML/CSS/JS, React, Rive, Spline), faceplates, knobs, faders, meters, plug-in browsers, mixer or Q-Link consoles, complex material/graphic systems, resizable HiDPI layouts, accessibility, palettes, and processing visualizers. Use when a request concerns an audio-plugin or audio-host GUI, WebUI/WebView surface, MC Host skinning, references the UI, interaction, or visual language of products such as FabFilter, Valhalla, or Baby Audio, or asks to turn an audio-product brief into a wireframe, mockup, critique, or JUCE/Web implementation. Do not use for DSP-only work or generic marketing websites.
---

# Audio Plug-in and Host UI

Design the interface as a musical tool: classify the product, lock geometry and interaction, establish one distinctive visual idea and material language, then implement and verify it in the target host or WebView.

Act as design lead for a boutique audio house. Reject generic LLM faceplates, SaaS dashboards, and palette-only "finishes" that leave unusable rails and empty meters.

## Route the request

Read this file first, then read every relevant reference file completely.

| Need | Read |
|---|---|
| Host, mixer, Q-Link, channel-strip bank, plug-in browser | [references/host-console.md](references/host-console.md) |
| Complex materials, chamfers, mockup fusion, anti-AI graphic defaults | [references/graphic-composition.md](references/graphic-composition.md) |
| WebView / HTML/CSS/JS / React / Rive / Spline / hybrid shell | [references/webview-ui.md](references/webview-ui.md) |
| WebUI jank, IPC cost, bundle size, WebView startup, GPU idle | [references/webview-ui.md](references/webview-ui.md) § WebUI optimization cookbooks |
| Palette, perceptual color, contrast, semantic roles | [references/color.md](references/color.md) |
| Autonomous cross-domain palette research, current online cases, and palette transfer | [references/palette-research.md](references/palette-research.md), then [references/color.md](references/color.md) |
| Creative fractal or generative processing display | [references/fractal-visualizers.md](references/fractal-visualizers.md) |
| JUCE LookAndFeel, custom Components, scaling, RT-safe UI | [references/juce-implementation.md](references/juce-implementation.md) |
| Product cases, layout anchors, official and industry sources | [references/reference.md](references/reference.md) |

## Classify before designing

| Class | Typical work | Default structure |
|---|---|---|
| Plug-in faceplate | EQ, compressor, reverb, synth, creative effect | One dominant control or processing display plus supporting controls |
| Host console | Standalone mixer, strip bank, graph host, Q-Link shell | Repeated strips with restrained chrome; host gates override decorative faceplate rules |
| In-DAW utility | Gain, bridge insert, compact meter | Minimal and direct; no decorative visualizer |

If the class is a host console, apply [references/host-console.md](references/host-console.md) before choosing color or WebUI ornament. Never place a fractal or hero animation on a mixer shell merely to make it look designed.

A finished colour header or token table is **not** a finished UI. If hit targets, strip width, meters, and accent budget fail, reject the pass.

## Establish the brief

Infer reasonable defaults when safe, state them, and proceed. Capture:

```text
Product class and type:
Primary job in the first five seconds:
Sonic character and subject world:
Material language (shell / recess / light behavior):
One signature interaction or graphic system:
Primary, secondary, and advanced controls:
Target size, resizing, HiDPI, and host context:
Renderer (native JUCE / WebView / hybrid / filmstrip):
Technology and existing assets:
Accessibility and performance constraints:
Layout freeze? (zones locked vs structure may move):
```

The subject world must come from the product: circuit, tape, optics, room geometry, spectral surgery, modular patchbay, or another specific vocabulary. Avoid a style that could be reused unchanged for any effect.

When redesigning an existing host or editor, default to **locked-zone skinning**: art, materials, chamfers, and fader caps may change aggressively; functional zone order stays unless the brief explicitly moves a region.

## Lock geometry before paint

1. Draw a pixel-budgeted wireframe and record the fixed or resizable bounds.
2. Make primary controls larger or more central than secondary controls. Do not make every knob equal.
3. Reserve enough width and hit area for faders, meters, labels, and values. A visible rail may be narrow only when the interaction hit region remains comfortably larger.
4. Define selected, active, bypassed, focused, disabled, clipped, and error states without relying on hue alone.
5. Separate primary work from diagnostics and debug telemetry.
6. Test the layout at minimum size and common scale factors before token polish.
7. At every adaptive-content breakpoint, compare the outer component bounds
   with the visible content envelope on all four sides. Correct internal gaps
   do not excuse unexplained trailing space left by fixed or persisted minimum
   sizes; reserve that space only for an explicit control or declared future
   surface.

For a faceplate, choose one dominant structure: Hero, Asymmetric, Minimal, Immersive, or Clustered. Secondary structure may support it when the workflow requires it; do not combine patterns without a hierarchy.

Host starting points: strip content width often lands around 36–44 logical px before touch inflation; fader rail ~10–12 px with a larger thumb/hit region; browser column collapsible. Validate in product pixels rather than treating ranges as law.

## Build the visual system

Read [references/graphic-composition.md](references/graphic-composition.md) for complex graphic work.

When the user delegates visual direction or no palette has been approved, do
not wait for hex values or rely on memory alone. Research current, relevant
cross-domain cases and synthesize an adapted palette through
[references/palette-research.md](references/palette-research.md). A request to
choose and apply autonomously authorizes selection and in-scope implementation,
not unrelated redesign or deployment outside the task's existing authority.
Websites, editorial systems, industrial products, and other non-audio sources
may shape colour rhythm, typography, material, spacing, and motion. Keep
operational hierarchy and interaction grounded in the real audio tool.

- Name one memorable signature. Spend visual emphasis there and keep the surrounding chrome quieter.
- Define a depth grammar: shell, raised plate, instrument panel, recess/well, cap/thumb, filament, readout.
- Define surface, text, control, accent, focus, semantic-status, and meter roles. Brand colors, neutrals, and semantic status colors are separate budgets.
- Build ramps in a perceptual space such as OKLCH, then convert to sRGB/ARGB and gamut-check the result.
- Use WCAG contrast ratios as useful minimum heuristics for native plug-ins, not as a claim of web conformance. Preserve readable text, control boundaries, focus indication, and non-color state cues.
- Use a coherent widget family. Mix vector, bitmap, skeuomorphic, CSS, and WebGL elements only when the material transition is deliberate.
- Make meters and visualizers explain processing. Motion needs a job, a performance budget, and a reduced-motion or static fallback.
- Keep labels in musician language and retain units where values would otherwise be ambiguous. Remove copied web-app vocabulary and decorative process numbers.

Reject the common defaults: cyan-purple glow on every edge, equal neon on all controls, rounded SaaS cards with fake stats, generic vintage panels with unusable hit areas, cream-serif-terracotta or acid-green-on-black templates used without a subject reason, or a creative display pasted onto a clinical utility.

### Accent rationing

Reserve the strongest brand accent for no more than two primary jobs on hosts (typically mode and selection/focus). Fader fills and hovers use quieter relatives. Semantic status colors are independent and always paired with shape, text, or position.

## Choose the production path

- This skill owns the audio-product information architecture, interaction,
  accessibility, host constraints, and acceptance contract. Figma, Superdesign,
  or another canvas skill owns only its canvas mechanics and must preserve that
  frozen contract.
- For a design-only page or flow, use an available design canvas when it materially helps. Apply this skill's audio-domain and geometry constraints to the canvas output.
- For a requested bitmap faceplate, texture, or visual variant, use available image generation after the wireframe and token plan are fixed. Generated imagery is an asset brief, not the interaction specification.
- For complex graphic redesigns: real layout capture → style references → **fusion into the real IA** → tokens → implementation. Reject comps that invent a new information architecture.
- For WebView/WebUI, read [references/webview-ui.md](references/webview-ui.md). Prefer one material token source shared with any native chrome.
- For native code, use [references/juce-implementation.md](references/juce-implementation.md) and inspect the existing component hierarchy before editing.
- For a scaled designer handoff, prefer structured design metadata, hitbox masks, and explicit layers over unexplained `setBounds` constants.

## Implement in two passes

1. Produce a compact plan: role tokens, type hierarchy, depth grammar, dominant layout, ASCII or canvas wireframe, signature, and interaction states.
2. Critique whether the same plan would fit any competing product or collapse into an AI default. Revise the generic axis.
3. Implement LookAndFeel / CSS tokens for shared widgets and custom Components or canvases for unique displays or gestures.
4. Keep analyzer data transfer lock-free or bounded; never render, allocate, lock, call into a WebView, or iterate visual effects on the audio thread.
5. Capture screenshots at minimum and representative sizes. Verify in the standalone build and relevant plug-in hosts.

## Acceptance gate

- Primary controls are immediately reachable and visibly prioritized.
- Values, units, reset, fine adjustment, hover/pressed/disabled, bypass, and automation behavior are coherent.
- Keyboard focus order and shortcuts work; meaningful custom controls expose JUCE accessibility roles, names, values, and actions (and WebUI equivalents where applicable).
- Focus and state are not encoded by color alone. Text and required control cues retain usable contrast.
- Resize behavior, host DPI, and asset sharpness are verified rather than inferred.
- Peak, RMS, loudness, and gain-reduction meters use ballistics appropriate to the measurement; idle geometry remains present.
- Motion can be reduced and does not flash; rendering remains off the audio thread.
- Host consoles pass all geometry, accent, telemetry, and repetition gates in [references/host-console.md](references/host-console.md).
- WebUI paths pass the checklist in [references/webview-ui.md](references/webview-ui.md).
- Complex graphic work passes the critique checklist in [references/graphic-composition.md](references/graphic-composition.md).
- The result has one recognizable signature and no competing decorative visualizers.

## Response shape

Lead with the proposed product class, primary job, geometry, material language, and signature. Follow with the control hierarchy, token roles, renderer choice, interaction/accessibility behavior, build plan, and verification evidence. Show only enough rationale for the user to evaluate the tradeoffs.
