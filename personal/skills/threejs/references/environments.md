# Environments — sky, water, terrain, light, scale

## Sky

Three options, in order of preference.

**`SkyMesh`** (`three/addons/objects/SkyMesh.js`) is the TSL/node version of
the classic `Sky` — physically-based Preetham scattering, works on both
backends. Use `Sky.js` only in a WebGL-only project.

```js
import { SkyMesh } from 'three/addons/objects/SkyMesh.js';

const sky = new SkyMesh();
sky.scale.setScalar(10000);
sky.turbidity.value = 8;
sky.rayleigh.value = 2;
sky.mieCoefficient.value = 0.005;
sky.mieDirectionalG.value = 0.8;

const sun = new THREE.Vector3().setFromSphericalCoords(
  1,
  THREE.MathUtils.degToRad(90 - elevationDeg),
  THREE.MathUtils.degToRad(azimuthDeg)
);
sky.sunPosition.value.copy(sun);
scene.add(sky);
```

Node properties are uniforms — assign to `.value`, not to the property.

**`SkyMesh` in r185 also has procedural clouds and a sun disc**, which the
classic `Sky` never had. Nothing in the Preetham API hints at them, so they get
missed:

```js
sky.cloudCoverage.value = 0.45;   // 0 = clear sky
sky.cloudDensity.value  = 0.6;
sky.cloudScale.value    = 1.0;    // feature size
sky.cloudSpeed.value    = 0.02;   // animates on its own, no per-frame work
sky.cloudElevation.value = 2000;
sky.showSunDisc.value   = 1;      // 0 hides the disc, keeps the scattering
```

Full uniform list, verified against `SkyMesh.js`: `turbidity`, `rayleigh`,
`mieCoefficient`, `mieDirectionalG`, `sunPosition`, `cloudScale`, `cloudSpeed`,
`cloudCoverage`, `cloudDensity`, `cloudElevation`, `showSunDisc`.

One line that is easy to forget: `sky.material.fog = false`. With `FogExp2` in
the scene the fog is applied to the sky dome too, which flattens the whole
background to a single colour and reads as "my sky stopped working".

**Sun placement is a framing decision.** A sun at 3-5° elevation placed in
front of the camera fills the frame with a blown-out disc and the bloom
finishes the job. Put low suns behind or to the side (azimuth 240-290°), or
raise the elevation.

**HDRI** gives the most convincing light for anything reflective:

```js
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

const hdr = await new RGBELoader().loadAsync('env.hdr');
hdr.mapping = THREE.EquirectangularReflectionMapping;
scene.environment = hdr;
scene.background = hdr;
scene.environmentIntensity = 1.0;
scene.backgroundBlurriness = 0.3;   // background only, lighting stays sharp
```

**Procedural gradient** — cheapest, and enough when the sky is only a backdrop.
A `backgroundNode` on the scene costs no geometry at all:

```js
import { screenUV, mix, color } from 'three/tsl';
scene.backgroundNode = mix(color(0x1b3a5c), color(0xff9b54), screenUV.y.pow(2));
```

## Water

`WaterMesh` (`three/addons/objects/WaterMesh.js`) is TSL-based and does
reflection, refraction and normal-map distortion properly.

```js
import { WaterMesh } from 'three/addons/objects/WaterMesh.js';

const water = new WaterMesh(new THREE.PlaneGeometry(1000, 1000), {
  waterNormals,                 // tiling normal map, RepeatWrapping, NoColorSpace
  sunDirection: sun,
  sunColor: 0xffffff,
  waterColor: 0x0a2836,
  distortionScale: 3.7,
  size: 1.0,                    // normal-map tiling density
  alpha: 1.0,
  resolutionScale: 0.5,         // the reflector's render target, default 0.5
});
water.rotation.x = -Math.PI / 2;
```

Two things the option list does not tell you:

**`WaterMesh` renders the scene again.** It uses `reflector()` internally, so
every frame there is a second pass at `resolutionScale`. Measured on an
entry-level dGPU: +3.2 ms/frame for a 128 m radius lake at 0.35. It is the first
thing to turn down when a water scene misses budget, and dropping it out of the
scene graph is how you measure what it costs.

**The npm package does not ship `examples/textures/`.** Only `examples/jsm/`
is published — so every tutorial line like `load('textures/waternormals.jpg')`
404s in a local install, and `waterNormals` arrives `undefined`. Either vendor a
normal map yourself, or generate one once at load: sample 3D noise around a
torus so it tiles in both axes, take central differences for the gradient, and
pack it into a `DataTexture` with `colorSpace = NoColorSpace`. About 30 lines,
no assets, no network.

**Never animate water by rewriting vertex positions in JavaScript.** A
160×160 plane is 26 000 vertices; touching them per frame, plus
`computeVertexNormals()`, is milliseconds of main thread every frame for an
effect that belongs in a shader. Displace in `positionNode` instead:

```js
const wave = Fn(() => {
  const p = positionLocal.xz;
  return p.x.mul(0.055).add(time.mul(1.1)).sin().mul(0.55)
    .add(p.y.mul(0.041).sub(time.mul(0.85)).sin().mul(0.45));
});
material.positionNode = positionLocal.add(vec3(0, wave(), 0));
```

Cheap fake that reads well at distance: a flat plane with a scrolling normal
map and high metalness. No vertex work at all.

## Terrain

**Build heights on the GPU when they are static in shape but large**, on the
CPU when you need to query them (placing objects, collision).

CPU generation is fine — once, at load:

```js
const geo = new THREE.PlaneGeometry(size, size, seg, seg);
geo.rotateX(-Math.PI / 2);
const pos = geo.attributes.position;
for (let i = 0; i < pos.count; i++) {
  pos.setY(i, heightAt(pos.getX(i), pos.getZ(i)));
}
geo.computeVertexNormals();
```

Segment count is a budget decision: `seg²  × 2` triangles. 256 segments is
131 000 triangles for one tile — reasonable. 1024 is 2.1 million — not.

**Vertex colours beat textures** for terrain that is mostly rock and sand: no
UV unwrap, no texture memory, and you can drive them from height and slope.

**Level of detail:** three concentric tiles at decreasing resolution, cross-
faded by opacity, cover far more ground than one dense mesh. Two rules:

- Planes that do not write depth are ordered by draw order — the **most
  detailed tile must be drawn last** or it is hidden by the coarse one.
- Blend with opacity over a band, never a hard swap, or the seam pops.

## Fog and aerial perspective

`FogExp2` is right for atmosphere; linear `Fog` for a bounded stage.

```js
scene.fog = new THREE.FogExp2(0x9a6650, 0.0055);
```

Match the fog colour to the horizon, not the sky zenith, or the ground meets
the sky in a visible band. If the camera climbs, fog density must fall — real
atmosphere thins with altitude, and constant density makes altitude
unreadable.

## Lighting

Default to three lights:

```js
const sun = new THREE.DirectionalLight(0xffd7b0, 3);
sun.position.copy(sunDir).multiplyScalar(300);
sun.castShadow = true;

const sky = new THREE.HemisphereLight(0xffa86a, 0x1a2138, 0.6);
scene.add(sun, sky);
```

Lighting is physically-based since r165 — `physicallyCorrectLights` no longer
exists, intensities are in real units, and point/spot lights fall off with the
inverse square. Old tutorials' intensity values are wrong by orders of
magnitude.

**Shadow camera is the whole game.** A `DirectionalLight` shadow covers the
frustum you configure and nothing else:

```js
sun.shadow.mapSize.set(2048, 2048);
const d = 150;
Object.assign(sun.shadow.camera, { left: -d, right: d, top: d, bottom: -d, near: 1, far: 600 });
sun.shadow.bias = -0.0005;
sun.shadow.normalBias = 0.02;
```

Too wide and shadows are blocky; too narrow and they vanish at the edges. Use
`CameraHelper(sun.shadow.camera)` to see it.

**Shadow type: `PCFSoftShadowMap` is fine on `WebGPURenderer`.** The
deprecation warning lives in `WebGLShadowMap.js` and only fires on the legacy
`WebGLRenderer`; the node path maps type 2 to a real `PCFSoftShadowFilter`. See
`deprecated-r185.md` for the source.

Cost matters more than type here. Measured on the same 1100 m scene at 1280×800
(MX450, WebGPU, 2048² shadow map, mean ms/frame):

| `renderer.shadowMap.type` | ms/frame | vs no shadows |
|---|---|---|
| shadows disabled | 30.5 | — |
| `PCFSoftShadowMap` | 32.7 | +2.2 |
| `VSMShadowMap` | 48.6 | **+18.1** |

VSM buys genuinely blurred contact-hardening shadows and costs eight times as
much. Start with `PCFSoftShadowMap`, and spend the budget on shadow camera
extent and map size — those dominate quality — before switching filter.

## Scale and distance

`1 unit = 1 metre`, always.

Objects that are genuinely huge do not need to be huge in the scene. A planet
at 1/25 scale, with its distance divided by 25 too, has **exactly the same
angular size and curvature** on screen — and keeps coordinates inside float32
precision. At true scale, 6 371 km expressed in metres makes nearby geometry
visibly shake.

For a camera whose distance to its subject varies by orders of magnitude, set
the near plane from that distance rather than fixing it:

```js
camera.near = Math.max(0.1, distanceToTarget * 0.001);
camera.far  = Math.max(2000, altitude * 8);
camera.updateProjectionMatrix();
```

`logarithmicDepthBuffer` also fixes z-fighting, but it breaks every
depth-based post effect (DOF, bokeh, SSAO). Prefer scaling the world.
