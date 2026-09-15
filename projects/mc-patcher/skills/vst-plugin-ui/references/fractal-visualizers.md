# Fractal and Generative Visualizers

Use a generative display only when it explains or embodies a creative effect and remains subordinate to control usability. Do not use it on host consoles, utility gain plug-ins, or clinical tools as decoration.

## Choose a family

| Family | Visual character | Suitable mapping |
|---|---|---|
| Escape-time Julia or Mandelbrot variants | Organic filaments and nested structure | Reverb density, diffusion, delay feedback, morphing |
| IFS or kaleidoscopic folds | Crystalline and architectural | Rhythmic, modular, resonant, or geometric effects |
| Strange attractors | Flowing trajectories and ribbons | Modulation, stereo motion, evolving ambience |
| Ray-marched distance fields | Sculptural depth | A single high-budget hero surface with a GPU fallback |

Choose one family and one visual hierarchy. Do not combine a fractal, FFT, oscilloscope, and particle field unless each answers a distinct user question and the layout can support them.

## Map audio and parameters

Use three to five mappings that remain interpretable:

| Signal or parameter | Possible visual target | Guardrail |
|---|---|---|
| Low-band energy | Scale, displacement, or slow structural motion | Avoid full-frame pumping |
| Mid-band energy or modulation depth | Twist, detail, or trajectory spread | Preserve control legibility |
| Spectral centroid or high-band energy | Edge sharpness or restrained palette position | Never map directly to a flashing white level |
| Onset or beat | A short bloom envelope | Use soft attack/release and a reduced-motion fallback |
| Effect parameter | Julia constant, fold amount, attractor coefficient | Prefer deterministic mapping the user can learn |

Do not specify a smoothing coefficient without its filter equation and update rate. Prefer time constants in milliseconds or seconds and compute the coefficient from frame delta, for example `a = exp(-dt / tau)` for `y = a*y_previous + (1-a)*x`. Choose separate attack and release behavior when the display needs meter-like response.

Use the faceplate palette as a lookup table. A pitch-to-hue map is an optional artistic convention, not a psychoacoustic truth.

## Rendering architecture

1. Transfer only bounded analyzer state from the processor, using atomics, a lock-free FIFO, or a snapshot that never blocks the audio callback.
2. Smooth, aggregate, and generate visual geometry on a worker or message-side path.
3. Paint a cached image, vector path, or GPU texture from the UI thread.
4. Cap frame rate and complexity. Lower detail when the editor is small, hidden, or running on constrained hardware.
5. Stop or greatly reduce updates when the editor is closed or occluded where the framework permits it.
6. Provide a static or reduced-motion mode and prohibit hard full-field flashes.

JUCE OpenGL can work for shader-heavy visuals, but it is not a universal default: profile host compatibility, context lifetime, platform behavior, and fallback rendering. A cached CPU image can be safer for modest displays.

## Prototype sequence

```text
1. Confirm creative effect and user-facing purpose
2. Lock control wireframe and readable overlay zones
3. Choose one generative family and a token-derived palette
4. Prototype a still frame using real parameter ranges
5. Animate with deterministic test signals and frame-delta smoothing
6. Connect bounded analyzer data
7. Profile CPU/GPU use in standalone and target hosts
8. Verify reduced motion, resize, editor-close, and failure paths
```

## Acceptance gate

- The display changes in a way users can relate to the effect or signal.
- Controls and text remain readable at the minimum editor size.
- Motion contains no seizure-risk flashing and can be reduced.
- Analyzer and rendering work never executes on the real-time audio thread.
- The visualizer uses the product palette rather than a second rainbow brand.
- Closing the editor removes or minimizes visualization cost.
