# Host and Mixer Console UI

Apply this file when the product class is a standalone host, mixer, channel-strip bank, graph host, plug-in browser, or Q-Link-style console. A host shell is a repeated operational surface, not a creative effect faceplate.

## Priority jobs

| Priority | Job |
|---|---|
| P0 | See and grab channel gain, mute, solo, and selection across many strips |
| P0 | Identify the selected channel without obscuring meter and control state |
| P1 | Read live meters and clip or gain-reduction state |
| P1 | Load, route, bypass, and remove plug-ins without permanently starving the mixer |
| P2 | Inspect host, bridge, and performance health through secondary diagnostics |

Default to Clustered strip banks with restrained chrome. Personality should come from the console's geometry, grouping, meter language, labels, and material treatment, not from a hero animation.

For visual redesigns of an existing host, prefer **locked-zone skinning**: keep browser / routing / inserts / meters / mixer / master topology unless the brief explicitly moves a region. Materials, chamfers, fader caps, and route motifs may change aggressively inside those zones. See [graphic-composition.md](graphic-composition.md). If the surface is WebView-backed, also read [webview-ui.md](webview-ui.md).

## G1: Geometry

Pass this gate before color or LookAndFeel polish.

1. Budget the browser and strip bank from the narrowest supported window.
2. Start desktop channel strips around 36–44 logical pixels of usable content width and widen them when a separate meter, readable name, or touch support is required. Validate rather than treating the range as a standard.
3. Give a vertical fader a visually legible well and a larger invisible interaction target. A useful starting point is a 10–12 logical-pixel rail and a thumb or hit region at least about 24 by 12 logical pixels; scale and enlarge for touch or accessibility.
4. Reserve meter geometry even when the signal is idle. Never fake meter activity in a static mockup that is presented as live state.
5. Show selection with an edge, marker, value shift, or restrained surface change. Do not flood the whole strip with saturated accent.
6. Make the plug-in browser collapsible or resizable. A reasonable initial desktop constraint is roughly one quarter of the window, but content and minimum strip count decide the actual limit.
7. Give the master strip more width or a clear separator while retaining the same widget language.

### Strip anatomy

```text
┌────────┐
│ M  S   │  explicit on/off state, not color alone
│ meter  │  peak/RMS/loudness behavior named
│ ║  █   │  fader well, filled range, tactile thumb
│ 0.0 dB │  editable value and unit
│ ch 07  │  index plus useful name
└────────┘
```

Keep index and name distinguishable. For large banks, support scrolling, paging, grouping, or scalable strip density without losing the current selection.

## G2: Accent budget

Reserve the strongest brand accent for no more than two primary jobs, normally active mode and selection or focus. Use lower-chroma or lower-lightness variants for fader fill and hover.

Semantic colors are independent:

| Role | Typical meaning |
|---|---|
| `ok` | Connected, healthy, signal present |
| `warn` | Solo, approaching clip, degraded bridge |
| `bad` | Mute when operationally critical, clip, failed connection |
| `meterLow/Mid/High` | Signal magnitude only |

Always pair status color with text, icon, shape, or position. Verify grayscale and common color-vision-deficiency simulations.

## G3: Telemetry hierarchy

Fold CPU, core count, raw milliseconds, buffer diagnostics, and bridge logs into a compact status area or diagnostics panel. The first viewport should prioritize mode, routing or link state, bypass, clear/reset when relevant, and the strip bank.

Expose warnings when actionable. Do not keep a decorative PERF readout at the same prominence as gain or mute.

## G4: Repetition with difference

Repeated strips need enough variation to remain scannable:

- Stable channel indices and names
- Selected and focused states
- Live meter or signal-presence state
- Group or bus separators
- Clear master, aux, input, and output roles
- Muted, soloed, bypassed, disconnected, and clipped states

Test with realistic names, quiet and active channels, long banks, empty slots, and error states. Sixteen perfect clones with identical `0.0` readouts are not an adequate console evaluation.

## Interaction and accessibility

- Support click-drag, double-click reset, fine adjustment, direct value entry, and mouse wheel only where users expect it.
- For patch matrices and cable fields, verify identity routes plus adjacent crossings in both directions, fan-in, and fan-out. At shared endpoints, confirm the routes visibly separate beside the jack instead of remaining merged until the cable midpoint. Use a controlled small matrix and inspect every visible cable from jack to jack: any path that begins or ends in open canvas, breaks into a detached fragment, or misses its endpoint fails the visual gate. A screenshot containing only parallel 1:1 routes cannot validate endpoint tangents, crossover geometry, or overlapping-route selection, and one correct probe route cannot stand in for the whole composed cable field.
- A fan-out test must validate the first visible segment, not only a shared centre coordinate. Every route must remain one continuous path beginning at the exact jack centre; use distinct short departure segments or tangents so the paths are distinguishable by the time they clear one jack radius. Do not move path starts to circumference slots: that can produce apparently detached fragments. A test that merely checks identical `M` coordinates can pass while visible cables remain merged until mid-span.
- For panels that expand from a node inside a zoomable graph, test the composed panel at minimum, default, and enlarged Graph zoom together with at least one non-default UI scale, including a node near a viewport edge. Decide explicitly whether the panel belongs to graph-world geometry or screen-fixed chrome. A graph-world panel must scale with its node; a screen-fixed panel must be clamped to the viewport. Reject inverse-scale cancellation that makes the panel balloon relative to its node, clipping under drawers or outside the work surface, even when its isolated CSS dimensions and internal canvas tests pass.
- When the brief says to reuse an existing patchbay or widget, call its established geometry and visual primitives, but do not change the stable consumer merely to serve the new one. Keep a source-contract assertion for the original widget, apply orientation/fan-out adaptation only in the new consumer, and verify both the original hosted view and the adapted hosted view. Copying only constants or selectors is not reuse; changing the original widget without explicit authorization is a regression.
- Keep keyboard navigation within the plug-in editor or standalone window predictable and avoid stealing global DAW shortcuts.
- Give Mute, Solo, Bypass, and channel selection explicit accessible names, roles, values, and actions.
- Announce connection failures and destructive routing changes through text, not only a tint.
- Ensure a collapsed browser and diagnostics panel remain reachable by keyboard and assistive technology.

## Acceptance checklist

- [ ] Minimum-size geometry leaves the required number of usable strips
- [ ] Fader interaction target, meter, name, value, and M/S controls are distinct
- [ ] Selection remains clear in grayscale and without a full-strip glow
- [ ] Strong accent has no more than two primary jobs
- [ ] Semantic state does not depend on hue alone
- [ ] Diagnostics are secondary but actionable failures surface
- [ ] Master and bus roles are distinct without a second visual language
- [ ] Scrolling, paging, focus, and resize behavior have been exercised with realistic content
- [ ] No fractal, plasma, or unrelated hero display occupies mixer space
