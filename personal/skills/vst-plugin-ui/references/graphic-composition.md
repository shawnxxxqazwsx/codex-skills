# Complex Graphic Composition for Audio UIs

Use this file when the brief needs more than a palette swap: instrument materials, chamfered shells, routing graphics, layered meters, generative heroes, mockup-to-code fusion, or any faceplate/host surface that must feel designed rather than themed.

Audio UI graphic design is **composition under operational constraints**. Beauty that breaks strip alignment, hit targets, or state legibility is a failed pass.

## Design lead stance

Act as design lead for a boutique audio house. Every product needs a visual identity that could not be mistaken for a generic LLM faceplate. Adapted from [Anthropic frontend-design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) and specialized for musical tools:

1. Ground the look in the product's subject world.
2. Take one justified aesthetic risk.
3. Spend boldness once; keep surrounding chrome quiet.
4. Critique the plan against "would this fit any competing product?" before building.
5. Prefer screenshots and real host pixels over prose self-congratulation.

## Subject world → material language

Pick one concrete world and derive materials from it. Do not paste a landing-page aesthetic onto a mixer.

| Subject world | Material cues | Typical products |
|---|---|---|
| Precision lab | Matte graphite, thin rules, cool phosphor accents | Surgical EQ, analysis, utility |
| Warm hardware | Cream plates, oxide, ivory caps, soft bevels | Consoles, vintage dynamics, tape |
| Future instrument | Thick chamfers joining light shell to deep black wells, sparse neon filaments | Modern creative hosts/effects |
| Optics / spectral surgery | Dark glass, overlay grids, restrained cyan/magenta readout | Spectral tools |
| Modular / patchbay | Cables, jacks, arch bridges, panel screws as quiet rhythm | Routers, multichannel hosts |
| Organic space | Soft gradients, diffusion fog, no hard SaaS cards | Reverb, ambient |

Write the material language in one sentence before drawing:

```text
Material language: <shell> + <recess> + <metal/plastic language> + <light behavior>
Signature graphic: <the one memorable constructed form>
Forbidden leftovers: <dashboard cards / equal neon / generic dark theme>
```

## Depth grammar (build once, reuse everywhere)

Complex graphics read as coherent when every elevation shares a grammar.

| Layer | Job | Typical treatment |
|---|---|---|
| App shell | Outer product body | Soft plate gradient, restrained outer shadow |
| Raised plate | Browse/settings clusters | Lighter fill, 1px top highlight, short warm/cool shadow |
| Instrument panel | Mixer, meters, master | Near-black family, microtexture, dark rim |
| Recess / well | Fader tracks, displays | Inset shadow, 1px low-contrast lip |
| Cap / thumb | Graspable control | Bevelled body, grip cue, compact cast shadow |
| Filament / hairline | Brand or route cue | Sparse colored strokes; never outline every widget |
| Readout | Values and meters | Tabular figures, semantic fills, no fake segment glitter |

Rules:

- Chamfers and thick rounded joins can marry a light shell to a black well. Steal the **join strategy**, not a competitor's logo or exact radii.
- Microtexture is a low-opacity repeating gradient or noise, not a JPEG plastered on every panel.
- Glossy plastic, bloom, and multi-layer neon outlines are guilty until proven necessary.
- CSS/WebUI: prefer a small set of gradients and shadows that encode elevation. Native JUCE: prefer LookAndFeel roles that mirror the same elevation names.

## Composition systems for complex layouts

### A. Locked-zone skinning (hosts and dense tools)

1. Freeze functional regions: browser, routing, inserts, meters, mixer, master, chrome.
2. Redesign materials, corners, faders, and route graphics **inside** those regions.
3. Allowed structural tweaks are brief-explicit only (example: routing bars become arch bridges; meters move under the arches).
4. Acceptance: a musician who knows the old layout can still drive it blind.

This is the validated path from MC Host redesign work: art may change aggressively; zone topology usually must not.

### B. Hero construction (creative faceplates)

1. Choose Hero / Immersive / Asymmetric from [reference.md](reference.md).
2. Build the hero as a **constructed graphic system** (curve editor, patch field, generative field, 3D body), not a stock screenshot of a waveform.
3. Surround with 3–5 supporting controls max for Hero, or edge-floating controls for Immersive.
4. Map audio with 3–5 interpretable links; see [fractal-visualizers.md](fractal-visualizers.md) when the hero is generative.

### C. Cluster storytelling (amps, strips, multi-FX)

1. Proximity groups beat bordered settings sections.
2. Each cluster has one lead control size.
3. Signal flow left→right or top→bottom must be readable at a glance.
4. Per-stage bypass and meters attach to the stage they explain.

### D. Graphic motif systems

Use motifs that scale across many repeated strips:

| Motif | Use | Failure mode |
|---|---|---|
| Arch / bridge routes | Multichannel patch aesthetics | Decorative cables that hide jack targets |
| Filament ticks | Scale marks, tempo grids | Rainbow ticks on every control |
| Bezel rings | Focused displays | Nested rings that steal fader width |
| Segment lamps | Vintage meters | Fake activity and unreadably tiny segments |
| Monoline icons | Mode/status | Icon soup without text backup |

## Mockup → fusion → implementation pipeline

For complex graphic redesigns, especially with GenerateImage or designer comps:

```text
1. Capture the real product layout (screenshot or wireframe with pixel budgets)
2. Author or generate style references (material, fader, chamfer, motif)
3. Fuse style into the real layout — reject comps that invent a new IA
4. Extract tokens: surfaces, inks, recess, accent, meter semantics
5. Implement in the real stack (CSS variables / LookAndFeel / WebUI assets)
6. Screenshot at min/default size; compare to fused target
7. Fix geometry regressions before more art polish
```

When the user asks to reproduce a reference that changes grouping or order,
freeze a structural-delta checklist before changing materials or tokens: zone
proportions, control grouping and order, repeated separators, and side utility
areas. Do not claim the reference is reproduced from palette, gradient, or knob
styling while any listed structural delta remains. If the reference simplifies
the product controls, preserve every production parameter and move secondary
controls into explicit utility groups instead of deleting or hiding them.

If the user loves a generated fader or panel, treat it as an **asset brief**, then rebuild it with real hit targets and live meter data. Do not ship a flat image where a control must move.

## Anti-defaults for AI graphic passes

Reject plans that land on these without an explicit brief:

- Warm cream `#F4F1EA` + terracotta + serif poster typography used as a generic "premium" mask
- Near-black field with one acid cyan/green gel on every interactive edge
- Broadsheet hairlines and dense newspaper columns as fake sophistication
- Equal neon on tabs, faders, knobs, and cards
- Rounded SaaS cards, KPI strips, and fake activity charts on a console
- Creative fractal/plasma hero pasted onto a host mixer
- Palette file marked complete while rails stay 5px and meters are empty

Host pathology to remember: a complete colour header with thin rails, hue-only selection gel, and PERF competing with gain is not a finished UI.

## Typography and numeric graphics

- Pair a restrained product face with a highly legible UI/data face. Hosts may stay on a system UI stack when density and native feel matter more than display typography.
- Use tabular lining figures for dB, frequency, and time.
- Uppercase micro-labels need tracking and contrast discipline; do not shrink below readable sizes to "look pro."
- Values beat ornament. If a decorative scale mark collides with a readable `-6.0 dB`, cut the ornament.

## Motion as graphic composition

Motion is part of the composition only when it has a job:

| Job | Example |
|---|---|
| Ballistics | Meter attack/release, GR trail |
| State settle | Mode/page crossfade under 200–300 ms |
| Affordance | Cap depression, switch throw |
| Processing story | Hero field responding to density/feedback |

Always provide reduced-motion/static fallbacks. No seizure-risk full-frame flashing. No audio-thread animation math.

## WebUI material recipes (starting points, not skins)

```css
/* Elevation roles — replace hex with product tokens */
:root {
  --shell: #faeed9;
  --plate: #f2e5d1;
  --ink: #342a25;
  --panel: #08090a;
  --panel-raise: #151719;
  --recess: #030405;
  --cap: #e7dccb;
  --meter: #75e4d2;
  --warn: #e9c34f;
  --clip: #ff6259;
}

.panel {
  background:
    repeating-linear-gradient(0deg, rgb(255 255 255 / .02) 0 1px, transparent 1px 2px),
    linear-gradient(180deg, var(--panel-raise), var(--panel));
  box-shadow: inset 0 0 0 1px rgb(255 255 255 / .05);
}

.well {
  background: var(--recess);
  box-shadow: inset 0 1px 4px rgb(0 0 0 / .85), inset 0 0 0 1px rgb(255 255 255 / .04);
}

.cap {
  background: linear-gradient(180deg, #fffaf0, var(--cap));
  border: 1px solid #aa9d8b;
  box-shadow: inset 0 1px 0 #fffaf0, 0 2px 4px rgb(0 0 0 / .35);
}
```

Rebuild these from the product tokens. Do not ship the cream/black example as a universal theme unless the brief asks for that world.

## Critique checklist before coding

- [ ] Subject world and material language are named
- [ ] One signature graphic exists; second hero candidates were cut
- [ ] Depth grammar is consistent across panels and wells
- [ ] Repeated strips remain scannable with live/idle/error states
- [ ] Accent budget still ≤2 primary jobs on hosts
- [ ] Mockup fusion preserves real IA and hit targets
- [ ] Reduced-motion and non-hue state cues exist
- [ ] The blurred-thumbnail silhouette is recognizable
- [ ] The plan would not fit an arbitrary competing product unchanged

## Sources for craft

- BeatConnect [layout](https://docs.beatconnect.com/design/layout-patterns), [anti-patterns](https://docs.beatconnect.com/design/anti-patterns), [visualizers](https://docs.beatconnect.com/design/choosing-visualizers)
- [Anthropic frontend-design skill](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) — distinctive identity, anti-default calibration, two-pass critique
- [Ottosson Oklab](https://bottosson.github.io/posts/oklab/) and [Evil Martians on OKLCH in CSS](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl) — perceptual ramps and CSS tokens
- [Voger Design synth UX patterns](https://vogerdesign.com/blog/basic-ux-patterns-in-the-development-of-synthesizer-plugins-awesome/) — control size vs frequency of use
- [Playful Tones pixel-perfect pipeline](https://playfultones.com/blog/reflections-on-building-a-pixel-perfect-ui-pipeline-in-juce-applications---part-1) — structured design metadata and hitboxes
- Industrial HMI hierarchy ideas (progressive disclosure, status over decoration) are transferable to host diagnostics only; do not turn a creative plug-in into a SCADA screen
- For WebUI effect implementation cookbooks (blend, mask, conic meters, WebGL, Rive), see the tables in [webview-ui.md](webview-ui.md#complex-graphic-effect-cookbooks)
