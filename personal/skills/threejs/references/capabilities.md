# What three.js already does for you

Read this before writing any non-trivial helper. The most expensive mistake in
a three.js project is not a bug — it is spending an afternoon implementing
something that ships in `three/addons/`.

Everything below is in r185, verified against the installed package. Import as
`three/addons/<folder>/<File>.js`.

## The ones people reimplement by hand

| You are about to write | Use instead |
|---|---|
| Scattering objects over a mesh surface | `math/MeshSurfaceSampler` |
| A physics engine, or gravity + collisions | `physics/RapierPhysics` (also Jolt, Ammo) — **all three download the engine from a CDN at runtime**, at a version hard-coded in three's source, and simulate in their own `setInterval`. Read `physics.md` first |
| Spatial partitioning for collision or raycast | `math/Octree`, `math/OBB`, `math/Capsule` |
| A mesh decimator for LODs | `modifiers/SimplifyModifier` |
| Merging geometries, computing tangents | `utils/BufferGeometryUtils` |
| Porting a GLSL or ShaderToy shader to TSL | `transpiler/` (`GLSLDecoder`, `ShaderToyDecoder`, `TSLEncoder`, `WGSLEncoder`) |
| Rounded-corner boxes | `geometries/RoundedBoxGeometry(w, h, d, segments, radius)` — `radius` must stay under half the smallest dimension |
| Lofting a surface through profiles | `geometries/LoftGeometry` |
| A surface from a `(u, v) → point` function | `geometries/ParametricGeometry` (+ `ParametricFunctions` for plane/sphere/torus/klein) |
| Projecting a decal onto a surface | `geometries/DecalGeometry` |
| A convex hull around points | `geometries/ConvexGeometry`, `math/ConvexHull` |
| Text as real 3D geometry | `geometries/TextGeometry` + `loaders/FontLoader` |
| Metaballs / isosurfaces | `objects/MarchingCubes` |
| A mirror or a water refraction plane | `objects/Reflector`, `objects/Refractor` |
| Breaking an object into pieces | `misc/ConvexObjectBreaker` |
| Inverse kinematics for a rig | `animation/CCDIKSolver` |
| GPGPU on the WebGL backend | `misc/GPUComputationRenderer` (on WebGPU use TSL compute) |
| Perlin/simplex noise in JS | `math/ImprovedNoise` (in a shader use TSL `mx_noise_float`) |
| A colour ramp / lookup table | `math/Lut` |
| Auto-optimising a loaded scene | `utils/SceneOptimizer` |

## Loaders (48 of them in r185)

Do not write a parser. The ones that matter:

**3D formats** — `GLTFLoader` (the default choice), `FBXLoader`, `OBJLoader`,
`ColladaLoader`, `STLLoader`, `PLYLoader`, `USDZLoader`, `3DMLoader`,
`3MFLoader`, `LDrawLoader`, `VRMLLoader`, `VOXLoader`, `MD2Loader`.

**Compression** — `DRACOLoader` (geometry), `KTX2Loader` (GPU textures, the
big VRAM win), `MeshoptDecoder`.

**Images and HDR** — `RGBELoader` (.hdr), `EXRLoader`, `HDRCubeTextureLoader`,
`TGALoader`, `DDSLoader`, `LogLuvLoader`, `UltraHDRLoader`.

**Other** — `FontLoader`, `SVGLoader`, `BVHLoader` (mocap), `TTFLoader`,
`LUT3dlLoader` / `LUTCubeLoader` (colour grading).

## Controls (9)

`OrbitControls` is the default. The others exist for a reason:

| Control | For |
|---|---|
| `MapControls` | Top-down pan-first navigation |
| `TrackballControls` | Free rotation with no up-vector constraint |
| `ArcballControls` | Precise inspection with a visible gizmo |
| `FlyControls` / `FirstPersonControls` | Free flight, walkthrough |
| `PointerLockControls` | FPS mouse capture |
| `TransformControls` | Editor gizmo: move, rotate, scale |
| `DragControls` | Dragging objects with the pointer |

## Environment and lighting

`environments/` ships three scenes for `PMREMGenerator.fromScene()`:

| Scene | Gives you |
|---|---|
| `RoomEnvironment` | Instant studio lighting, with softboxes. **A metal without an environment renders black**; this is the one-line fix. |
| `ColorEnvironment(hex)` | Uniform ambient of one colour. Cheaper and neutral, but a flat environment leaves metal flat — no gradient across the surface. |
| `DebugEnvironment` | Coloured walls, for checking that reflections point where you think. |

`lights/LightProbeGenerator`, `lights/RectAreaLightUniformsLib` (RectAreaLight
does nothing until you init this), `objects/Sky` / `SkyMesh` (node version),
`objects/GroundedSkybox`, `objects/Lensflare`.

## Post-processing

Two separate stacks — do not mix them:

- **`tsl/display/`** (45 files, 47 exports) — the modern one, works on both
  backends. See `postfx-catalog.md`.
- **`postprocessing/`** (30 passes) — the legacy `EffectComposer` chain.
  WebGL only. Use only when maintaining old code.

## Rendering to something other than a canvas

`renderers/CSS2DRenderer` — DOM labels tracking 3D positions. Backend-agnostic,
crisp at any zoom, accessible.
`renderers/CSS3DRenderer` — real DOM elements transformed in 3D space.
`renderers/SVGRenderer` — vector output.
`interactive/HTMLMesh` — a live DOM element as a texture in the scene.

## XR

`webxr/XRButton` (`VRButton`, `ARButton`), `XRControllerModelFactory`,
`XRHandModelFactory`, `OculusHandModel`, `XREstimatedLight`, `XRPlanes`.

Remember: WebXR **requires** `renderer.setAnimationLoop`. `requestAnimationFrame`
silently does nothing in an XR session.

## Exporters

`GLTFExporter` (the default), `USDZExporter` (AR Quick Look on iOS),
`OBJExporter`, `STLExporter`, `PLYExporter`, `DRACOExporter`, `KTX2Exporter`,
`EXRExporter`.

## Helpers worth knowing

`helpers/ViewHelper` (axis gizmo), `helpers/TextureHelper`,
`helpers/RectAreaLightHelper`, `helpers/OctreeHelper`,
`helpers/PositionalAudioHelper`, `helpers/VertexNormalsHelper`.

And in core: `CameraHelper`, `Box3Helper`, `GridHelper`, `AxesHelper`,
`SkeletonHelper`. `new THREE.CameraHelper(light.shadow.camera)` is the fastest
way to see why shadows are missing.

## Inspector

```js
import { Inspector } from 'three/addons/inspector/Inspector.js';
renderer.inspector = new Inspector();
```

Official runtime inspector for the WebGPU renderer: scene graph, compiled
shader source, per-pass timings. Faster than guessing why a node material is
black.

## What the package does NOT ship

`examples/` contains **only** `jsm/`. There is no `examples/textures/`, no
`examples/models/`, no `examples/screenshots/` in the npm package — those live in
the GitHub repo. Every tutorial and official-example snippet that loads
`textures/waternormals.jpg`, `textures/matcaps/…` or a `.glb` from `models/`
therefore 404s against a plain `npm install three`, and the loader hands your
material an `undefined` map.

Generate the small ones procedurally (noise → `DataTexture` for normal maps,
`FlakesTexture` ships in `jsm/textures/`), or vendor the asset deliberately.
`examples/fonts/` *is* published, so `FontLoader` + `TextGeometry` work offline.

## How to check before building

```bash
ls node_modules/three/examples/jsm/            # the folders above
ls node_modules/three/examples/jsm/<folder>/   # what is in one
```

If a capability sounds generic — noise, sampling, simplification, physics,
IK, decals, hulls, text, mirrors — assume it exists and look before writing it.
