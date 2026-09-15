# JUCE UI Implementation

Inspect the repository's JUCE version, wrapper formats, editor hierarchy, parameter model, asset pipeline, and existing tests before changing code. Prefer the project's established architecture unless it prevents the requested behavior.

If the UI is primarily WebView/HTML/CSS/JS, read [webview-ui.md](webview-ui.md) first and keep this file for native chrome, Relays/attachments, lifetime, scaling, RT-safety, and accessibility bridges.

## LookAndFeel versus custom Components

| Approach | Use |
|---|---|
| `LookAndFeel_V4` subclass | Shared knobs, sliders, buttons, labels, menus, and theme roles |
| Custom `Component` with `paint` and `resized` | EQ curves, transfer functions, XY pads, patch graphs, filmstrip controls, and product-specific displays |
| Hybrid | LookAndFeel for standard chrome and custom Components for the signature interaction |

Start from `LookAndFeel_V4` behavior and override only what the product needs. The [official tutorial](https://juce.com/tutorials/tutorial_look_and_feel_customisation/) and [LookAndFeel_V4 API](https://docs.juce.com/develop/classjuce_1_1LookAndFeel__V4.html) are the primary implementation references.

### Lifetime rules

- Ensure the LookAndFeel object outlives every component that references it. Member declaration order matters because C++ destroys members in reverse order.
- Clear component or editor references with `setLookAndFeel(nullptr)` before the LookAndFeel is destroyed.
- Keep font and image assets alive for every paint call that uses them.
- Avoid mutable global LookAndFeel state shared by unrelated plug-in instances unless the project explicitly owns that lifetime.

## Layout and scaling

Use `resized()` as the authoritative layout path. Express bounds from named design constants, a grid, or a small layout model rather than scattering magic numbers through paint code.

- Let the host call `AudioProcessorEditor::setScaleFactor`; JUCE documents it as a host notification for non-unity GUI scale. Do not repurpose it as a user zoom command. See the [AudioProcessorEditor API](https://docs.juce.com/master/classjuce_1_1AudioProcessorEditor.html).
- For user resizing, call `setResizable`, set sensible limits or an aspect-ratio constraint, and recompute layout from current bounds.
- A child-component design-coordinate transform can support fixed-coordinate zoom, but verify hit testing, popup placement, focus rings, accessibility bounds, host resizing, and bitmap sharpness. Prefer true responsive layout when practical.
- Use vector assets or appropriate resolution variants. Verify fractional scale factors, not only 100% and 200%.
- For a directional drawer that grows the editor outside an existing primary
  view, define the screen-space anchor before implementation. If the drawer
  opens left while the primary view must stay still, resize and reposition the
  top-level/host window as one transaction; preserving only the child's width
  is insufficient. Verify both the primary view's size and screen position in
  the real hosted wrapper, because component-local geometry tests cannot prove
  the host window anchor.
- Treat `AudioProcessorEditor::setResizeLimits` as a bounds-changing call: JUCE
  may immediately constrain the editor's current bounds. When two UI states
  have different limits, make both the old and target bounds temporarily
  legal, request the target size once, then install the final limits. Record
  every resize callback in the regression; checking only the final bounds can
  miss a host-visible intermediate size.
- A claimed fix for a one- or two-frame resize flash needs presented-frame
  evidence from the reported host. Capture only the plug-in wrapper without
  driving the user's input, inspect every source frame around repeated
  transitions, and fail or mark the result inconclusive if a transition was
  not captured. Component snapshots and before/after anchor samples verify
  settled layout, not compositor continuity.
- When the user defines a panel envelope between named upper and lower
  boundaries, audit every visible control inside that envelope. Do not exclude
  a device-family toolbar, utility strip, or footer merely because the generic
  grid does not own it; add a family-specific geometry check for those controls
  and their relationship to the main control field.
- When repeated controls are distributed through that envelope, also audit
  each title-control-value bundle as a visual ownership unit. Put a measured
  upper bound on the title/value distance from its knob or switch, and verify
  that one bundle's value cannot visually merge with the next bundle's title;
  evenly spaced component centres alone do not prove parameter association.

Test at minimum, default, and maximum supported bounds on each target platform and in representative hosts.

## Parameters and interaction

- Construct controls before attachments and ensure attachments do not outlive either the parameter state or controls.
- Use `AudioProcessorValueTreeState::SliderAttachment`, `ButtonAttachment`, or the project's equivalent to synchronize UI and parameters.
- Give parameters stable IDs, names, units, normalisable ranges, defaults, value text, and host-automation behavior.
- Implement double-click reset, fine adjustment, direct text entry, and wheel behavior intentionally rather than inheriting surprising defaults.
- Avoid modal UI for common creative operations. Keep undo, A/B, bypass, preset, and destructive reset semantics consistent with the product tier.
- When replacing a standard JUCE widget interaction, test through the public
  mouse, keyboard, or accessibility entry point that users and hosts invoke.
  A direct call to an overridden target such as `ComboBox::showPopup()` can
  bypass native pre-dispatch state. Exercise an open-close-open sequence and
  prove the replacement releases any native modal, popup, capture, or focus
  state before accepting the interaction.

## Real-time-safe feedback

The processor must not wait for the editor.

```text
audio callback
  -> atomics or bounded lock-free FIFO
  -> UI-side snapshot / aggregation
  -> timer, worker, or GPU update
  -> repaint cached state
```

- Do not allocate, lock, format strings, open files, render paths, or invoke OpenGL from the audio callback.
- Make FIFO overflow behavior explicit: drop old visualization frames or coalesce state rather than blocking.
- Use a timer or vsync-driven repaint at the lowest rate that communicates the measurement.
- Distinguish peak, RMS, loudness, and gain-reduction ballistics. Document attack, release, hold, integration, and reset behavior where relevant.
- Reduce work when the editor is hidden or closed.

## Accessibility

JUCE exposes native accessibility through `AccessibilityHandler`. The [official API](https://docs.juce.com/master/classjuce_1_1AccessibilityHandler.html) requires a role and supports actions plus value, text, table, and cell interfaces.

- Use standard JUCE controls when they already expose appropriate behavior.
- For custom controls, implement `createAccessibilityHandler()` with a meaningful role, title, description, help text, current value, range, and supported actions.
- Provide a deliberate keyboard focus order with a focus traverser where needed.
- Make keyboard and accessibility actions call the same underlying command path.
- Notify clients when values, focus, structure, or state change.
- Keep decorative visualizers out of the accessibility tree, but provide a textual value or summary when their information is necessary.
- Test with VoiceOver on macOS and Narrator on Windows when those platforms are in scope.

## Suggested project layout

```text
Source/ui/
  PluginLookAndFeel.h
  PluginLookAndFeel.cpp
  UiTokens.h
  layout/
  widgets/
  views/
  PluginEditor.h
  PluginEditor.cpp
Assets/
  fonts/
  images/
  web/                 # optional WebUI bundle
    index.html
    styles.css
    app.js
```

Follow the repository's naming and build system. Embed distributable assets through the project's binary-data or resource pipeline and verify licensing. For WebUI, serve Release assets through `withResourceProvider` and keep Debug hot-reload origins explicit.

## Verification matrix

- Standalone plus each requested VST3, AU, or CLAP wrapper
- Supported macOS and Windows scale factors
- Minimum/default/maximum editor sizes
- Light and dark host chrome where the editor border is visible
- Parameter automation during resize and editor reopen
- Preset restore, undo/redo, bypass, and sample-rate or block-size changes
- Editor closed while audio continues
- Accessibility focus and value changes
- Long sessions with analyzer or animation enabled

Capture screenshots and, for interactive regressions, add component or snapshot tests if the repository has a test harness.
