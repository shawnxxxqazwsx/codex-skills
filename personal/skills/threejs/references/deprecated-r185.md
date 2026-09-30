# Blacklist — API that is dead or renamed in r185

Every entry below was extracted from `@deprecated` annotations in the r185
source, not from memory. `src/` contains 84 of them. Verify any doubtful symbol
yourself:

```bash
grep -rn "@deprecated" node_modules/three/src/ | grep -i "<symbol>"
```

Deprecated three.js API still runs — it warns to the console and quietly
degrades. That is why it survives review: the page works, so nobody looks. The
console is where the evidence is.

## Tier 1 — you will reach for these by default

| Dead | Use instead | Since | Consequence if ignored |
|---|---|---|---|
| `THREE.Clock` | `THREE.Timer` | r183 | Console warning. `Timer` needs `timer.update(timestamp)` in the loop; `Clock` self-computed. |
| `PostProcessing` | `RenderPipeline` | r183 | Renamed class, same job. Warns once. |
| `PCFSoftShadowMap` | nothing — see below | — | **Legacy `WebGLRenderer` only.** Valid on `WebGPURenderer`. |
| `renderer.renderAsync()` | `await renderer.init()` then `render()` | r181 | Whole `*Async` family is deprecated, see below. |
| `outputEncoding` | `outputColorSpace` | r152 | Removed outright. Washed-out or oversaturated output. |
| `sRGBEncoding` | `SRGBColorSpace` | r152 | Removed outright. |
| `physicallyCorrectLights` | on by default | r165 | Property ignored; light intensities read wrong. |
| `useLegacyLights` | removed | r165 | Property ignored. |

### `PCFSoftShadowMap` is not deprecated on the renderer this skill tells you to use

It is worth being precise, because the blanket claim sends you to VSM for no
reason and VSM costs 8× more (see `postfx-catalog.md`).

The downgrade warning exists in exactly one place — `src/renderers/webgl/
WebGLShadowMap.js`, which only the legacy `WebGLRenderer` uses:

```js
if ( this.type === PCFSoftShadowMap ) {   // WebGLShadowMap.js
  warn( 'WebGLShadowMap: PCFSoftShadowMap has been deprecated. Using PCFShadowMap instead.' );
```

The node path — `WebGPURenderer`, on **either** backend — resolves the type
through a lookup table, and index 2 is a real soft filter:

```js
// src/nodes/lighting/ShadowNode.js
const _shadowFilterLib = [ BasicShadowFilter, PCFShadowFilter, PCFSoftShadowFilter, VSMShadowFilter ];
getShadowFilterFn( type ) { return _shadowFilterLib[ type ]; }
// constants.js: BasicShadowMap = 0, PCFShadowMap = 1, PCFSoftShadowMap = 2, VSMShadowMap = 3
```

There is no `@deprecated` annotation on the constant anywhere in `src/`. So on
`WebGPURenderer`: `PCFSoftShadowMap` gives you `PCFSoftShadowFilter`, cheaply.
Choose `VSMShadowMap` for genuinely blurred, variance-based shadows when you have
measured that you can afford it — not as a workaround for a deprecation that does
not apply to you.

## Tier 2 — the `*Async` family (all r181)

The pattern is uniform: call `await renderer.init()` once at setup, then use
the plain synchronous method everywhere.

| Dead | Use instead |
|---|---|
| `renderer.renderAsync()` | `renderer.render()` |
| `renderer.clearAsync()` | `renderer.clear()` |
| `renderer.clearColorAsync()` | `renderer.clearColor()` |
| `renderer.clearDepthAsync()` | `renderer.clearDepth()` |
| `renderer.clearStencilAsync()` | `renderer.clearStencil()` |
| `renderer.hasFeatureAsync()` | `renderer.hasFeature()` |
| `renderer.initTextureAsync()` | `renderer.initTexture()` |
| `pipeline.renderAsync()` | `pipeline.render()` |
| `quadMesh.renderAsync()` | `quadMesh.render()` |
| `pmrem.fromSceneAsync()` | `pmrem.fromScene()` |
| `pmrem.fromEquirectangularAsync()` | `pmrem.fromEquirectangular()` |
| `pmrem.fromCubemapAsync()` | `pmrem.fromCubemap()` |

```js
// Correct, once:
const renderer = new THREE.WebGPURenderer({ antialias: true });
await renderer.init();
// ...everything after this point is synchronous.
```

## Tier 3 — TSL renames

These are easy to get wrong because the old names are all over blog posts and
older examples.

| Dead | Use instead | Since |
|---|---|---|
| `.label()` | `.setName()` | r179 |
| `.cache()` | `.isolate()` | r181 |
| `append()` | `Stack` | r176 |
| `transformedNormalView` | `normalView` | r178 |
| `transformedNormalWorld` | `normalWorld` | r178 |
| `transformedClearcoatNormalView` | `clearcoatNormalView` | r178 |
| `viewportResolution` | `screenSize` | r169 |
| `directionToFaceDirection()` | `negateOnBackSide()` | r185 |
| `directionToColor()` | `packNormalToRGB()` | r185 |
| `colorToDirection()` | `unpackRGBToNormal()` | r185 |
| `PI2` | `Math.PI * 2` | r181 |
| `pass.setResolution()` | `pass.setResolutionScale()` | r181 |
| `pass.getResolution()` | `pass.getResolutionScale()` | r181 |
| `lineColorNode` (Line2) | `colorNode` | r185 |

## Tier 4 — math and misc

| Dead | Use instead | Since |
|---|---|---|
| `Matrix3.scale()` | `Matrix3.makeScale()` | r185 |
| `Matrix3.rotate()` | `Matrix3.makeRotation()` | r185 |
| `Matrix3.translate()` | `Matrix3.makeTranslation()` | r185 |
| `ColorManagement.fromWorkingColorSpace()` | `.workingToColorSpace()` | r177 |
| `ColorManagement.toWorkingColorSpace()` | `.colorSpaceToWorking()` | r177 |
| `reflector({ resolution })` | `{ resolutionScale }` | r180 |
| `controls.connect()` with no element | pass the element | r185 |
| `renderer.getColorBufferType()` | `.getOutputBufferType()` | r182 |

## Superseded rather than deprecated

These still work and warn about nothing. They are not errors — but choosing
them in new code means choosing the slower or weaker path.

| Legacy | Modern | Why it matters |
|---|---|---|
| `WebGLRenderer` | `WebGPURenderer` | Falls back to WebGL2 automatically. Without it: no compute shaders, no node materials, no TSL post-processing. |
| `requestAnimationFrame` | `renderer.setAnimationLoop` | rAF breaks WebXR entirely and does not await WebGPU submission. |
| `EffectComposer` + passes | `RenderPipeline` + TSL nodes | The legacy chain has bloom, DOF and a few filters. The TSL catalogue adds GTAO, SSGI, SSR, SSS, godrays, denoise, FSR1, SMAA. |
| `ShaderMaterial` + GLSL strings | `NodeMaterial` + TSL | GLSL strings are WebGL-only and fail on the WebGPU backend. TSL compiles to both WGSL and GLSL. |
| `Geometry` merging by hand | `BatchedMesh` | Per-object culling and separate transforms in one draw call. |
| `Points` updated in a JS loop | compute shader + `instancedArray` | The single biggest cause of missed frame budget. |

## Checking before you commit

The fastest audit of a scene you did not write:

```bash
grep -nE "Clock\(|PCFSoftShadowMap|outputEncoding|sRGBEncoding|renderAsync|\
physicallyCorrectLights|useLegacyLights|new PostProcessing|\.label\(|\.cache\(" src/**/*.js
```

And then the one that actually proves it — run the scene and read the console.
`scripts/verify_scene.mjs` collects warnings for you; deprecation notices show
up there verbatim.
