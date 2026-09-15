# Color for Audio Plug-in Interfaces

Choose color after geometry and interaction states are clear. Use color to reinforce hierarchy, not to rescue an undifferentiated layout.

When the direction is not approved and the agent is expected to research or
choose it, first follow [palette-research.md](palette-research.md).

## Perceptual workflow

1. Choose a subject-derived base palette: tape oxide, anodized aluminum, oscilloscope phosphor, room darkness, surgical overlay, or another product-specific source.
2. Define roles before hex values.
3. Build lightness and chroma ramps in a perceptual space such as OKLCH or HSLuv.
4. Convert to sRGB or the platform target, gamut-map deliberately, and inspect the converted colors.
5. Check text, control boundaries, focus, disabled state, meters, and semantic states at target sizes.
6. Capture grayscale and common color-vision-deficiency simulations.

Do not assume equal HSL lightness means equal perceived brightness. OKLCH is a useful working space, but equal hue-angle steps do not guarantee equally pleasing harmony and out-of-gamut conversion can change the result. Inspect rather than trusting wheel arithmetic.

Primary references: [Ottosson on Oklab](https://bottosson.github.io/posts/oklab/) and [Evil Martians on OKLCH in CSS](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl). For WebUI, prefer `oklch()` source tokens with sRGB fallbacks when the host WebView requires them.

## Converge taste on the real surface

When the palette is not already approved, do not serially guess one hex value,
rebuild the product, and call each result a design pass. Treat subjective taste
as a controlled visual audition:

1. Capture the actual target page at a representative size and state. Freeze
   geometry, content, meter activity, selection, and surrounding chrome so
   palette candidates are the only meaningful variable.
2. Present a small labelled comparison set on that real surface, normally a
   baseline plus 2–4 candidates. Vary one main axis at a time—lightness,
   chroma, hue/temperature, or surface contrast—and include both the whole
   composition and a 1:1 control crop when material detail matters. Avoid
   isolated swatches as the decision artifact.
3. Label candidates with role tokens and perceptual coordinates, not mood words
   alone. Translate requests such as “darker” or “less saturated” into a stated
   relative change from the baseline, while keeping room for the user to reject
   the direction on taste.
4. Treat a user-supplied exact color as an audition candidate unless they say
   to lock or ship it. Preserve that base value exactly; derive raised, header,
   border, text, hover, and selected roles around it instead of silently
   shifting the requested color.
5. Separate three gates: implementation proof (tokens are wired and readable),
   preference approval (the user chooses the visual direction), and product
   acceptance (the approved palette is verified in the real app/host). A CSS
   assertion that contains a candidate hex proves implementation only.
6. During exploration, test stable invariants such as role-token wiring,
   required states, contrast, and source-to-bundle identity. Freeze literal
   palette values in a regression only after the user or product specification
   has approved them; otherwise the test creates churn without proving quality.

For token-driven WebUI, prefer an ephemeral CSS-variable override, Theme Lab,
or equivalent preview harness that can render the comparison set in one real
page session without mutating production source for every candidate. Keep the
baseline restorable, record the complete token set behind each candidate, and
write/build the production palette only after selection. A preview harness must
not bypass the later real-bundle and host acceptance gate.

Every shown preview needs provenance. Before capture, verify the intended page
and UI state, the current source tokens, and the rendered/bundled tokens. Derive
the filename, caption, and candidate label from those verified values rather
than reusing a previous preview variable. Discard any capture whose page, state,
label, source, or bundle identity does not agree. Keep unapproved candidates in
preview builds; do not deploy or describe them as final.

## Role tokens

| Group | Suggested roles |
|---|---|
| Surfaces | `background`, `panel`, `panelRaised`, `sunken`, `border` |
| Text | `text`, `textDim`, `textDisabled` |
| Controls | `track`, `body`, `handle`, `value`, `focus` |
| Brand emphasis | `accent`, `accentDim` |
| Status | `ok`, `warning`, `error`, `bypass` |
| Meters | `meterLow`, `meterMid`, `meterHigh`, `clip`, `gainReduction` |

Three or four chromatic brand colors can be a useful discipline, but do not count neutrals or required semantic colors as brand accents. Warm and cool colors may coexist when their roles are intentional. The real gate is hierarchy, not an arbitrary total color count.

## Harmony and temperature

| Strategy | Appropriate use | Risk |
|---|---|---|
| Monochromatic | Minimal utilities and dense tools | Weak state separation if lightness range is too small |
| Analogous | Cohesive creative effects | Controls can merge with the visualizer |
| Complementary accent | Strong single focus or selected state | Accent inflation when reused everywhere |
| Split-complementary or triadic | Rich generative displays | Competing focal points and inaccessible state coding |

Sonic associations such as amber for compression, blue for precision, or purple for reverb are starting hypotheses, not defaults. A distinctive product should derive temperature and material from its own character rather than repeat category stereotypes.

## Contrast and accessibility

WCAG is written for web content, so a native JUCE editor should not claim WCAG conformance solely from ratios. The ratios are still useful minimum visual heuristics:

- Aim for at least 4.5:1 for ordinary text and 3:1 for large text.
- Give the visual information required to identify a control, its state, and focus roughly 3:1 contrast against adjacent colors.
- Inactive or purely decorative chrome need not be forced to the same contrast.
- Pair every hue-coded state with value, shape, position, icon, label, or motion-independent treatment.
- Keep a visible keyboard focus treatment even when hover is present.

See [WCAG 2.2](https://www.w3.org/TR/WCAG22/) and the [non-text contrast explanation](https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html) for the exact web criteria. Apply them as design evidence, then also test platform accessibility.

## JUCE handoff

- Convert final palette values to explicit sRGB hex or ARGB and document the source OKLCH values.
- Centralize role tokens in one palette or LookAndFeel layer; avoid per-component magic colors.
- Derive hover, pressed, focus, and disabled variants from roles rather than applying global alpha blindly.
- For gradients and animated displays, interpolate in a suitable perceptual space off the audio thread, then upload or paint cached values.
- Check the same colors in the standalone app and at least one dark and one light host chrome when the plug-in border is visible.

## Reject these failures

- Equal neon accent on every knob, tab, fader, and outline
- Hue-only mute, solo, bypass, or selected state
- Random rainbow visualizer unrelated to the product palette
- Low-contrast tiny labels justified as "subtle"
- A token file that is complete while fader rails, focus, and disabled states remain unspecified
- Warm/cool prohibition that prevents necessary semantic or meter information
