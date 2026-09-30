# Post-processing — the TSL catalogue

The legacy `EffectComposer` chain gives you bloom, bokeh and a handful of
filters. The TSL catalogue in `three/addons/tsl/display/` gives you 45 files
exporting 47 entry points, including ground-truth ambient occlusion,
screen-space reflections, global illumination, subsurface scattering, godrays
and temporal antialiasing.

This is the single biggest capability gap between old and current three.js.

## Assembly

```js
import * as THREE from 'three/webgpu';
// mrt, output y normalView son nodos: viven en three/tsl, NO en three/webgpu.
// `THREE.mrt(...)` es undefined y muere con "THREE.mrt is not a function".
import { pass, mrt, output, normalView } from 'three/tsl';
import { bloom } from 'three/addons/tsl/display/BloomNode.js';
import { ao }    from 'three/addons/tsl/display/GTAONode.js';

const pipeline = new THREE.RenderPipeline(renderer);

const scenePass = pass(scene, camera);
scenePass.setMRT(mrt({ output, normal: normalView }));   // when an effect needs normals

const colour = scenePass.getTextureNode('output');
const depth  = scenePass.getTextureNode('depth');
const normal = scenePass.getTextureNode('normal');

// ao() returns a GTAONode, not a texture. Multiplying colour by the node itself
// does not give you occlusion — read its texture and take one channel.
const aoPass = ao(depth, normal, camera);
aoPass.radius.value = 9;        // METRES. See "GTAO is scale-dependent" below.
const occlusion = aoPass.getTextureNode().r;

pipeline.outputNode = colour.mul(occlusion).add(bloom(colour, 0.6, 0.4, 0.85));

renderer.setAnimationLoop((t) => {
  timer.update(t);
  pipeline.render();          // instead of renderer.render(scene, camera)
});
```

**The MRT key is `normal`, the node is `normalView`.** `mrt({ output, normal })`
with a bare `normal` is a reference to an undeclared variable — the key names
the buffer, the value is the node that fills it.

The output is a **node expression**, not an ordered list of passes. You compose
effects with maths — `.add()`, `.mul()`, `mix()` — which is why blending two
effects is trivial here and awkward in the legacy chain.

`RenderPipeline` was called `PostProcessing` until r183. Both exist; the old
name warns.

## `pass()` and what you can pull out of it

| Method | Gives you |
|---|---|
| `getTextureNode()` | The rendered colour |
| `getTextureNode('depth')` | Raw depth |
| `getTextureNode('normal')` | Normals (needs MRT configured) |
| `getLinearDepthNode()` | Linearised depth — what most effects want |
| `getViewZNode()` | View-space Z, for DOF focus maths |
| `getPreviousTextureNode()` | Last frame — for temporal effects |
| `setResolutionScale(0.5)` | Render the pass at half res (was `setResolution`) |
| `setMRT(mrt)` | Request extra buffers |

## GTAO is scale-dependent, and gets it wrong silently

`ao(depth, normal, camera)` is the single highest-value effect here, and its
defaults are authored for a tabletop: `radius = 0.25`, `thickness = 1`. **Both
are in view-space units** — metres, if you followed the 1 unit = 1 metre rule.

In a landscape-scale scene those defaults sample 25 cm from each point, where
the only signal left in the depth buffer is quantisation noise. The result is
**dark terrace bands following the depth isolines** across large surfaces.

Measured on a 1100 m terrain (r185, WebGPU, 1280×800): with the defaults, four
hard bands across the whole hillside. With `radius = 9`, `thickness = 45`, they
are gone and the AO finally reads as contact shadow — **at the same cost**
(32.4 vs 31.8 ms/frame). This is not a quality/perf trade-off, it is simply the
wrong number.

It reports nothing: zero console errors, zero audit findings, unchanged frame
rate. The screenshot is the only evidence, which is why you look at it.

### `radius` measures the scene, not the contact you want to see

The obvious way to scale it is the wrong one. On a 1.2 m desk with books,
a laptop and two plant pots — a genuine tabletop, where the defaults apply —
the tempting reasoning is "the contacts here are 1–3 cm, so drop the radius".
Measured, `radius = 0.03` produces a **bright silhouette halo** around every
object instead of a contact shadow: at 3 cm the border pixels find no occluders
while large flat surfaces still accumulate spurious occlusion from depth noise,
and the contrast between the two reads as a rim light.

Same root cause as the terrace bands — radius too small for the scene — with a
different symptom, because the geometry is different. And it is not the upsample:
at `resolutionScale = 1` the halo is still there, at 36.3 ms/frame instead of
21.1.

| Scene | Correct `radius` | What too small looks like |
|---|---|---|
| 1.2 m desk | 0.25 (the default) | bright halo around each object |
| 700 m mountain | 8 | horizontal bands across the whole frame |
| 1100 m terrain | 9 | dark terrace bands across slopes |

So: pick the radius from the size of the *scene*, then check the screenshot. Both
failures cost the same as the correct value, so frame time will never tell you.

Three scenes, three different symptoms, one cause. The mountain row is the one
that shows how to *find* it: the bands run horizontally across screen space and
cross terrain and sky alike, so they read like a post-processing artefact rather
than anything geometric. Measured against the same frame with `ao` disabled,
`radius = 3.5` on that 700 m scene changed **92 % of the pixels**; at
`radius = 8`, 6.5 %. An ambient-occlusion pass that is touching almost every
pixel in the frame is not occluding — it is banding.

## Bloom on a white background is a global veil

Bloom thresholds the image and blurs whatever passes. A product-shot background
is white — **exactly 1.0** — so it passes any threshold you can set, and since
the background is most of the frame, what gets blurred over your subject is not
the highlight you wanted but the backdrop.

Measured on the desk scene (`bloom(colour, 0.34, 0.45, 0.92)`, threshold already
high): oak went from mid-brown to pale salmon, the laptop lid from dark grey to
near-white, and the shadow under the desk disappeared. Zero console errors, zero
audit findings — the screenshot is the only evidence. It also cost 493 extra
draw calls for the mip pyramid.

Raising the threshold above 1.0 does not fix it: the colour reaching the bloom
node already has tone mapping applied, so nothing exceeds 1 and the effect
becomes a no-op. **On a white background bloom has no useful setting** — drop it
and light the highlight instead.

| Property | Default | Meaning |
|---|---|---|
| `radius` | 0.25 | Sampling radius in **view-space units**. Scale it to your scene: roughly the size of the features you want occluded. |
| `thickness` | 1 | Max depth difference, view-space units, before a sample stops counting as an occluder. Too small on big scenes → banding. |
| `scale` | 1 | Exponent on the final AO. >1 deepens. |
| `samples` | 16 | <30 uses 3 directions, ≥30 uses 5. |
| `distanceExponent` / `distanceFallOff` | 1 / 1 | Sample distribution and weighting along each ray. |
| `resolutionScale` | 1 | **Property, not a method.** See below. |

```js
aoPass.radius.value = 9;        // uniforms: assign to .value
aoPass.thickness.value = 45;
aoPass.resolutionScale = 0.5;   // plain number: assign directly
```

`aoPass.setResolutionScale(0.5)` throws — `GTAONode` has no such method. Only
`PassNode` (what `pass()` returns) has `setResolutionScale()` /
`getResolutionScale()`.

## The catalogue

Import each from `three/addons/tsl/display/<File>.js`. **The file name does not
always follow the `<Name>Node.js` convention** — the exceptions are listed
explicitly below, and guessing them wrong is a 404 that reads as a bad import.

**Antialiasing**

Keep `antialias: true` on the renderer **as well as** a post AA node. The
plausible-sounding assumption — "the canvas MSAA cannot reach the pipeline's
offscreen render, and that is what `fxaa` is for" — is false: the scene pass
inherits the renderer's sample count, and dropping MSAA visibly coarsens
silhouettes.

Measured on the desk scene (r185, WebGPU, 1280×800, `fxaa` on in both cases):
turning MSAA on changes **1.51 % of the frame's pixels** for +1.4 ms
(19.05 → 20.45 ms/frame). At 5× magnification it is the desk edge, the pot rims
and the leaves that clean up. Control: two runs of the identical URL differ by
**0 pixels**, so the difference is the MSAA and not run-to-run noise.

The two are not redundant, they do different jobs: MSAA supersamples *coverage*
at raster time, `fxaa` blurs edges in an image that has already been rasterised
and cannot recover coverage that was never sampled. Use both; drop MSAA only if
you need the 1.4 ms.

| Call | File | Cost | Note |
|---|---|---|---|
| `fxaa(node)` | `FXAANode` | very low | Cheapest, softens texture detail. Complements MSAA, does not replace it |
| `smaa(node)` | `SMAANode` | low | Better edges than FXAA |
| `traa(colour, depth, velocity, camera)` | `TRAANode` | medium | Temporal; needs velocity MRT. Best quality, can ghost |
| `ssaaPass(scene, camera)` | `SSAAPassNode` | high | Supersampling — for stills, not realtime |
| `taau(...)` / `fsr1(node)` | `TAAUNode` / `FSR1Node` | low | Render small, upscale. The mobile play |

**Ambient occlusion and global illumination**

| Call | File | Cost | Note |
|---|---|---|---|
| `ao(depth, normal, camera)` | `GTAONode` | medium | Ground-truth AO. The single biggest realism win per millisecond |
| `ssgi(...)` | `SSGINode` | high | Screen-space GI — bounced light |
| `ssr(colour, depth, normal, opts)` | `SSRNode` | high | Reflections. Only reflects what is on screen |
| `sss(...)` | `SSSNode` | medium | Subsurface scattering — skin, wax, leaves |
| `denoise(node, depth, normal, camera)` | `DenoiseNode` | medium | Clean up noisy AO/GI/SSR |
| `recurrentDenoise(...)` | `RecurrentDenoiseNode` | medium | Temporal denoise, better for animation |

**Light and lens**

| Call | File | Note |
|---|---|---|
| `bloom(node, strength, radius, threshold)` | `BloomNode` | Threshold high (0.85+) or everything glows. Useless on a white background — see above |
| `godrays(depth, camera, light)` | `GodraysNode` | Volumetric shafts from a light |
| `lensflare(node, params)` | `LensflareNode` | Screen-space flare |
| `dof(node, viewZ, focus, focalLength, bokehScale)` | `DepthOfFieldNode` | Needs `getViewZNode()` |
| `motionBlur(node, velocity, samples)` | `MotionBlur` | Needs velocity MRT |
| `chromaticAberration(node, strength, center, scale)` | `ChromaticAberrationNode` | Lens fringing. **Pass `center` explicitly** — see below |

`chromaticAberration`'s signature is
`(node, strength = 1.0, center = null, scale = 1.1)`, and its JSDoc says of
`center`: *"If null, uses screen center (0.5, 0.5)."* **It does not.** The
factory calls `nodeObject(center)`, which returns `null` for `null`, and the
node then calls `.build()` on it. Taking the documented default kills the page
with:

```
THREE.TSL: TypeError: Cannot read properties of null (reading 'build')
```

which names neither the effect nor the parameter. Always pass
`vec2(0.5, 0.5)` yourself. Worth remembering as a class of bug, not just this
one: in the TSL effects a `null` default that the docs promise to fill in is
usually a default that was never implemented, and the failure surfaces as a
`build` error far from the call site.

**Colour and grade**

`lut3D` (`Lut3DNode.js`) · `film` (`FilmNode.js`) · `sepia` (`Sepia.js`)
· `bleach` (**`BleachBypass.js`**) · `sharpen` (`SharpenNode.js`)
· `transition` (`TransitionNode.js`) · `outline` (`OutlineNode.js`)
· `sobel` (`SobelOperatorNode.js`)

**Blur** — three of these are lower-case files with no `Node` suffix:

`gaussianBlur` (`GaussianBlurNode.js`) · `boxBlur` (**`boxBlur.js`**)
· `bilateralBlur` (`BilateralBlurNode.js`, edge-preserving)
· `hashBlur` (**`hashBlur.js`**) · `radialBlur` (**`radialBlur.js`**)
· `depthAwareBlend` (**`depthAwareBlend.js`**)

**Stylised**

`pixelationPass` · `retroPass` · `dotScreen` · `rgbShift` · `afterImage`
· CRT kit — all four live in one file, **`CRT.js`**: `barrelUV`, `barrelMask`,
`scanlines`, `vignette`, `colorBleeding`

**Stereo** — `anaglyphPass` · `stereoPass` · `parallaxBarrierPass`
(`StereoCompositePassNode.js` is the shared base, not an effect)

**Also present, undocumented above** — `temporalReproject`
(`TemporalReprojectNode.js`, the reprojection primitive TRAA and the temporal
denoiser build on) and `circle` (`Shape.js`).

r185 ships **45 files** in `tsl/display/`, exporting 47 entry points.

## Ordering that works

Effects are not commutative. A chain that reads correctly:

1. `ao` — multiply into colour **before** anything emissive
2. `ssr` / `ssgi` — add reflected and bounced light
3. `denoise` — if AO/GI/SSR are noisy
4. `dof` — depth-based, so before anything that destroys depth correlation
5. `bloom` — **add**, never multiply
6. `motionBlur`
7. colour grade (`lut3D`, `film`)
8. antialiasing (`fxaa` / `smaa` / `traa`) — last, on the final image

Bloom before AO produces glow on surfaces that should be occluded. AO after
bloom darkens the glow. Both look wrong in ways that are hard to name.

## Budget

Post-processing is fragment work: cost scales with pixels, not scene
complexity. On an integrated or entry-level GPU at 1080p, a rough guide:

| Effects | Feel |
|---|---|
| bloom + fxaa | free |
| + ao | comfortable |
| + dof or ssr | tight — measure |
| ssgi + ssr + traa | desktop GPU territory |

Measured, so the "free" and "comfortable" above have a number attached.
Landscape scene, 131 k-triangle terrain + 5 k instances + 90 k compute
particles, **1280×800 on a GeForce MX450** (entry-level laptop dGPU), WebGPU
backend, mean ms/frame — the whole frame, not the pass in isolation:

| Configuration | ms/frame | Delta |
|---|---|---|
| bare scene (no shadows, no water, no post) | 21.4 | — |
| + shadows (PCFSoftShadowMap, 2048²) | 30.5 | +9.1 |
| + water (`WaterMesh`, `resolutionScale` 0.35) | 27.3→ | +3.2 |
| + bloom + fxaa | 29.7 | +2.4 |
| + ao (`resolutionScale` 0.5) | 32.7 | +3.0 |
| shadows as VSMShadowMap instead | 48.6 | **+18.1** |

Two things to take from that: the post-processing chain is genuinely cheap
(bloom + fxaa + ao ≈ 5.4 ms together, and `main-thread` never left 1.5 ms — it
is all GPU), and **VSM shadows cost eight times what PCF-soft costs** on this
class of hardware. Reach for shadow settings before reaching for the effect
chain; the intuition that post-processing is the expensive part is wrong here.

Halve the cost of an expensive pass rather than dropping it. Note the two
different spellings — the pass has a method, the effect nodes have a property:

```js
scenePass.setResolutionScale(0.5);   // PassNode: method
aoPass.resolutionScale = 0.5;        // GTAONode and friends: plain property
```

Always confirm with `scripts/verify_scene.mjs`. Post-processing shows up in
main-thread time and in GPU frame time; if `main-thread ms` stays flat but
frames get longer, the cost is on the GPU and resolution scale is the lever.
