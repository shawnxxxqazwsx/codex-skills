# Canonical scene setup — r185

Read this before writing the first line of a new scene. Everything here is
verified against `three@0.185.1`.

## Entry points

`package.json` (0.185.1) declares exactly these:

```json
"exports": {
  ".":                { "import": "./build/three.module.js", "require": "./build/three.cjs" },
  "./webgpu":         "./build/three.webgpu.js",
  "./tsl":            "./build/three.tsl.js",
  "./addons":         "./examples/jsm/Addons.js",
  "./addons/*":       "./examples/jsm/*",
  "./examples/jsm/*": "./examples/jsm/*",
  "./examples/fonts/*": "./examples/fonts/*",
  "./src/*":          "./src/*"
}
```

| Import from | When |
|---|---|
| `three/webgpu` | Default for new work. 629 exports: everything in `three` **except `WebGLRenderer`**, plus node materials, `WebGPURenderer`, `RenderPipeline`. |
| `three/tsl` | Shader authoring **and every node function**. 638 exports. |
| `three` | Only for WebGL-only projects with no node materials. |
| `three/addons/*` | Loaders, controls, `SkyMesh`, `WaterMesh`, TSL display nodes. |

**`three/webgpu` does not re-export the TSL vocabulary.** This is the single
most common import mistake in r185. `pass`, `mrt`, `output`, `normalView`,
`vertexColor`, `shapeCircle`, `uv`, `positionWorld` — all of them are `undefined`
on the `THREE` namespace. Verified against the build:

```js
import * as THREE from 'three/webgpu';
THREE.mrt          // undefined  →  "THREE.mrt is not a function"
THREE.TSL.mrt      // function   ←  the namespace is nested under THREE.TSL
```

So either import from `three/tsl`, or reach through `THREE.TSL.*`. Note also
that `WebGLRenderer` genuinely is not there: if you need the legacy renderer you
must import it from `three`, and then you are back to two class identities.

Odd corner worth knowing: `isolate` (the replacement for the deprecated
`cache()`) is **not** an export of `three/tsl` — only `THREE.TSL.isolate` and the
chained method `node.isolate()` exist. `import { isolate } from 'three/tsl'`
fails while `import { cache } from 'three/tsl'` (the deprecated one) succeeds.

**`three/webgpu` and `three` cannot be mixed.** Two copies of the library means
two class identities: `mesh instanceof THREE.Mesh` starts returning false and
the errors make no sense. Pick one specifier per project and map addons to it.

## Importmap, no build step

```html
<script type="importmap">
{
  "imports": {
    "three":          "./node_modules/three/build/three.webgpu.js",
    "three/webgpu":   "./node_modules/three/build/three.webgpu.js",
    "three/tsl":      "./node_modules/three/build/three.tsl.js",
    "three/addons/":  "./node_modules/three/examples/jsm/"
  }
}
</script>
```

Mapping bare `three` to the webgpu build matters: addons import from `'three'`
internally, and if that resolves to `three.module.js` while your code uses
`three/webgpu`, you get the two-copies problem above.

**Vendoring:** `three.module.js` alone is not enough — it imports
`three.core.js` as a sibling. Copy both, or the page dies on a 404 that names
a file you never referenced.

## The skeleton

```js
import * as THREE from 'three/webgpu';

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 2000);
camera.position.set(0, 40, 130);

const renderer = new THREE.WebGPURenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
document.body.appendChild(renderer.domElement);

// setAnimationLoop initialises the backend on its own, so this is not always
// required. It IS required before calling render(), clear(), hasFeature() or
// initTexture() directly, and it is what makes the whole *Async() family
// unnecessary. Cheap and unconditional is the safe habit.
await renderer.init();

const timer = new THREE.Timer();

renderer.setAnimationLoop((timestamp) => {
  timer.update(timestamp);
  const dt = timer.getDelta();
  const t = timer.getElapsed();

  controls.update();
  renderer.render(scene, camera);
});

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

// Required by scripts/verify_scene.mjs.
window.__scene = { scene, camera, renderer };
```

### Which backend am I actually on?

The fallback is silent by design, so check rather than assume:

```js
const usingWebGPU = renderer.backend?.isWebGPUBackend === true;
```

`WebGPURenderer` prints `WebGPU is not available, running under WebGL2 backend`
when it falls back. Both paths must be tested — a TSL node that works on WGSL
can still fail to compile to GLSL.

Force the fallback to test it: `new THREE.WebGPURenderer({ forceWebGL: true })`.

## Renderer options worth knowing

| Option | Default | Note |
|---|---|---|
| `antialias` | `false` | Not `true` like `WebGLRenderer`. Set it explicitly. |
| `samples` | 4 when `antialias` | Override for a different MSAA count. |
| `outputBufferType` | `HalfFloatType` | Recommended. `UnsignedByteType` saves bandwidth, costs quality. |
| `forceWebGL` | `false` | Skip WebGPU entirely. Use to test the fallback path. |
| `multiview` | `false` | WebXR performance win where supported. |
| `reversedDepthBuffer` | `false` | Better precision for large depth ranges. |
| `logarithmicDepthBuffer` | `false` | Fixes z-fighting at planetary scale. **Breaks depth-based post-processing** (bokeh, DOF, SSAO) — prefer scaling the world down. |

## Colour management

`ColorManagement.enabled` is `true` by default since r152. The rules:

- Colours you type are sRGB: `new THREE.Color(0xff8844)` is handled correctly.
- **A `Color` built from hex already holds linear components.** `setHex` calls
  `toWorkingColorSpace`, and the working space is Linear-sRGB:
  `new THREE.Color(0xd6a068).r` is `0.672`, not `0.839`. So calling
  `.convertSRGBToLinear()` on it converts twice and everything comes out too
  dark, with no warning. In TSL, write `color(0xd6a068)` and let the node handle
  it — never `vec3(r, g, b)` with hand-converted numbers, and never a hex
  written straight into a `vec3`.
- **`vertexColors: true` *multiplies*; it does not replace.** `NodeMaterial.js:838`
  reads:

  ```js
  let colorNode = this.colorNode ? vec4( this.colorNode ) : materialColor;
  if ( this.vertexColors === true && geometry.hasAttribute( 'color' ) )
      colorNode = colorNode.mul( vertexColor() );
  ```

  The flag alone is correct and sufficient. Setting it *and* writing
  `colorNode = vertexColor()` applies the attribute twice — `vertexColor()²` —
  so the mesh renders darker with no error and a perfectly plausible image.
  Measured on a terrain that had shipped that way for two sessions: 64.6 % of
  pixels changed when it was fixed, ground colour `89,64,42` → `112,87,56`.
  Same double-application shape as the `convertSRGBToLinear()` trap above. Use
  the flag, or an explicit `colorNode`, never both.
- Colour textures (albedo, emissive) need `texture.colorSpace = THREE.SRGBColorSpace`.
- Data textures (normal, roughness, AO, displacement) must stay
  `THREE.NoColorSpace`. Tagging a normal map as sRGB is the classic cause of
  lighting that looks subtly wrong everywhere and obviously wrong nowhere.
- Loaders set this for you for glTF. They do not for a bare `TextureLoader`.

Tone mapping is separate and always needed for HDR-ish content:
`ACESFilmicToneMapping` is the safe default; `AgXToneMapping` is more neutral
in the highlights and better for photographic looks; `NeutralToneMapping`
follows the Khronos PBR neutral spec.

**On a white background, the choice is not cosmetic.** All three compress the
top end, so a backdrop you set to `0xffffff` does not come out white. Measured
on the same frame, same exposure 1.0, sampling the backdrop (r185, WebGPU):

| `toneMapping` | pure white renders as |
|---|---|
| `NeutralToneMapping` | 249 / 255 (97.6 %) |
| `ACESFilmicToneMapping` | 236 / 255 (92.5 %) |
| `AgXToneMapping` | 214 / 255 (83.9 %) |

For product shots, e-commerce and anything on a white page, `AgX` puts your
"white" background at 84 % — a visible grey — and ACES desaturates the subject
along with it. `Neutral` is the one that keeps white white. For a lit scene with
real highlights the ranking reverses: ACES and AgX roll off gracefully where
Neutral clips sooner.

## Scale and precision

Fix `1 unit = 1 metre` and write it in the project's notes.

Float32 has ~7 significant digits. Past roughly 100 km from the origin,
vertices visibly jitter and shadows crawl. The fix is not a bigger depth
buffer — it is a smaller world:

- Scale a planet down (a factor of 25 keeps angular size and curvature exact
  while keeping coordinates inside the safe range).
- Or keep the camera at the origin and move the world.

`near` and `far` are a ratio problem, not absolute numbers. Keep `far / near`
under ~10⁵. A `near` of 0.1 with a `far` of 100 000 is already z-fighting.

## Resize, correctly

```js
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();   // forgetting this stretches the image
  renderer.setSize(innerWidth, innerHeight);
  pipeline?.setSize?.(innerWidth, innerHeight);
});
```

Cap `setPixelRatio` at 2. Retina and high-DPI phones report 3 or 4, which
quadruples fragment cost for a difference nobody can see.

## Disposal

Nothing in three.js is garbage collected. A scene that grows and shrinks leaks
until the tab dies.

```js
function disposeObject(obj) {
  obj.traverse((o) => {
    o.geometry?.dispose();
    const mats = Array.isArray(o.material) ? o.material : o.material ? [o.material] : [];
    for (const m of mats) {
      for (const v of Object.values(m)) v?.isTexture && v.dispose();
      m.dispose();
    }
  });
  obj.removeFromParent();
}
```

Render targets and `RenderPipeline` need explicit `.dispose()` too. Verify with
`renderer.info.memory` — if `geometries` or `textures` climbs while the scene
looks static, something is leaking.
