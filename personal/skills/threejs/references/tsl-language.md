# TSL — Three.js Shading Language

TSL is how you write shaders in r185. You compose a graph of nodes in
JavaScript; three.js compiles it to **WGSL on WebGPU and GLSL on WebGL**. One
source, both backends.

This is not optional sugar. A GLSL string in `ShaderMaterial` is WebGL-only —
it fails on the WebGPU backend. If you want your shader to survive the
fallback, write it in TSL.

`three/tsl` exports 638 symbols. What follows is the working subset, verified
against the r185 build.

## Import

```js
import * as THREE from 'three/webgpu';
import { Fn, If, Loop, uniform, float, vec2, vec3, vec4, uv, texture,
         positionLocal, positionWorld, normalWorld, time, mix, smoothstep,
         instanceIndex, instancedArray, hash } from 'three/tsl';
```

## The mental model

A TSL expression is a **node**, not a value. Nothing executes in JavaScript;
you are building the shader's syntax tree.

```js
const brightness = uv().y.mul(2).sub(0.5).clamp(0, 1);
material.colorNode = mix(colorA, colorB, brightness);
```

Because nodes are objects, JavaScript control flow runs at *build* time and
TSL control flow (`If`, `Loop`) runs at *shader* time. A plain `if` picks which
shader to compile; `If()` branches per fragment.

Operators are methods, and they chain left to right:

| GLSL | TSL |
|---|---|
| `a + b` | `a.add(b)` |
| `a * b` | `a.mul(b)` |
| `a - b`, `a / b` | `a.sub(b)`, `a.div(b)` |
| `a += b` | `a.addAssign(b)` |
| `mix(a, b, t)` | `mix(a, b, t)` or `a.mix(b, t)` |
| `v.xy` | `v.xy` (swizzle works) |
| `v.x = 1.0` | `v.x = float(1)` (assignment works on storage/vars) |

## Vocabulary that covers most work

**Inputs**

| Node | Meaning |
|---|---|
| `uv()` | Texture coordinates |
| `positionLocal` / `positionWorld` / `positionView` | Vertex position per space |
| `normalLocal` / `normalWorld` / `normalView` | Normals per space |
| `cameraPosition` | World-space eye |
| `time` / `deltaTime` | Seconds; no uniform plumbing needed |
| `screenUV` / `viewportUV` | Screen-space coordinates |
| `instanceIndex` | Index in an instanced or compute dispatch |
| `attribute('name', 'vec3')` | Custom geometry attribute |
| `uniform(value)` | CPU-updatable value: `u.value = x` |
| `texture(map, uvNode)` | Sample a texture |

**Maths** — `mix` `smoothstep` `step` `clamp` `abs` `fract` `floor` `pow`
`sqrt` `exp` `log` `sin` `cos` `atan` `min` `max` `dot` `cross` `normalize`
`length` `distance` `remap` `select`

**Noise** — `hash(n)`, `mx_noise_float(p)`, `triNoise3D(p, speed, time)`,
`mx_fractal_noise_float(p, octaves, lacunarity, diminish)` (octaves is an `int`).
Use these before writing your own; they compile on both backends.

### Stripes that are not stripes: use the contour lines of a noise

For wood grain, marble, strata, contour maps — anything made of irregular
parallel lines — do not build it from a periodic function. `sin(y * k)` and
`fract(y * k)` give lines that are equidistant *by construction*, and the eye
reads equidistant lines as manufactured: laminate flooring, not oak. Adding a
per-line random offset and width does not fix it, because the spacing is still
one line per cell.

Take the **level sets** of a stretched fractal noise instead:

```js
// 20:1 anisotropy — the stretch IS the grain direction
const n = mx_fractal_noise_float(vec3(p.x.mul(0.25), p.y.mul(5.0), seed), int(4), float(2.0), float(0.55));
const line = smoothstep(0.15, 0.0, n.mul(5.2).fract().sub(0.5).abs());
```

The lines bunch where the noise gradient is steep and open out where it is
flat — which is what a growth ring does when the plank is cut at an angle. One
noise evaluation gives you spacing, width and figure at once, and `n` itself is
the broad tone variation, correlated with the grain the way it is in real timber.

Isotropic noise here gives stone, not wood. The anisotropy is the whole trick.

## Functions and control flow

```js
const ridged = Fn(([p, octaves]) => {
  const total = float(0).toVar();
  const amp = float(0.5).toVar();
  const freq = float(1).toVar();

  Loop(octaves, () => {
    total.addAssign(mx_noise_float(p.mul(freq)).abs().oneMinus().mul(amp));
    freq.mulAssign(2.03);
    amp.mulAssign(0.5);
  });

  return total;
});

// Call it like a function:
const h = ridged(positionWorld.xz.mul(0.02), 5);
```

`.toVar()` is essential and easy to forget: without it you are re-evaluating
an expression, not mutating a variable, and the loop accumulates nothing.

```js
If(h.greaterThan(0.5), () => {
  colour.assign(rock);
}).ElseIf(h.greaterThan(0.2), () => {
  colour.assign(grass);
}).Else(() => {
  colour.assign(sand);
});
```

`select(cond, a, b)` is the branchless ternary — prefer it for simple picks.

## Wiring nodes to a material

Use `*NodeMaterial` classes; the plain materials ignore node inputs.

```js
const material = new THREE.MeshStandardNodeMaterial();

material.colorNode      = texture(albedo, uv());
material.normalNode     = ...;
material.roughnessNode  = float(0.8);
material.metalnessNode  = float(0);
material.emissiveNode   = glow.mul(3);
material.positionNode   = positionLocal.add(normalLocal.mul(displacement));
material.opacityNode    = fade;
material.outputNode     = ...;   // last word on the final colour
```

Available: `MeshStandardNodeMaterial`, `MeshPhysicalNodeMaterial`,
`MeshBasicNodeMaterial`, `MeshLambertNodeMaterial`, `MeshMatcapNodeMaterial`,
`SpriteNodeMaterial`, `PointsNodeMaterial`, `LineBasicNodeMaterial`,
`Line2NodeMaterial`.

Displacing vertices via `positionNode` does **not** update normals. Either
recompute them analytically in TSL or accept flat lighting.

## Compute shaders

This is the reason to be on WebGPU. Work that would be a per-item JavaScript
loop runs on the GPU instead, and the buffer never leaves VRAM.

```js
import { instancedArray, instanceIndex, Fn, hash, vec3 } from 'three/tsl';

const COUNT = 200000;
const positions  = instancedArray(COUNT, 'vec3');
const velocities = instancedArray(COUNT, 'vec3');

// Runs once
const init = Fn(() => {
  const p = positions.element(instanceIndex);
  p.assign(vec3(hash(instanceIndex), hash(instanceIndex.add(1)), hash(instanceIndex.add(2))));
})().compute(COUNT).setName('init');

// Runs every frame
const update = Fn(() => {
  const p = positions.element(instanceIndex);
  const v = velocities.element(instanceIndex);
  v.addAssign(vec3(0, -0.0098, 0));
  p.addAssign(v);
})().compute(COUNT).setName('update');

renderer.compute(init);

renderer.setAnimationLoop(() => {
  renderer.compute(update);
  renderer.render(scene, camera);
});
```

Render the buffer without reading it back:

```js
const material = new THREE.SpriteNodeMaterial();
material.positionNode = positions.toAttribute();   // buffer stays on GPU
material.scaleNode    = uniform(0.12);
material.opacityNode  = shapeCircle();             // round sprite, no texture
material.transparent  = true;
material.alphaToCoverage = true;

const mesh = new THREE.Sprite(material);
mesh.count = COUNT;
```

`.setName()` (not the deprecated `.label()`) shows up in the inspector and in
compiled shader source — name your compute passes or debugging is guesswork.

For cross-invocation work: `workgroupArray`, `atomicAdd`, `storage`.

## Stateful compute: ping-pong, and what silently breaks

A simulation that reads its own previous state needs two buffers — you cannot
read and write the same storage texture in one pass. Three things bite here,
and none of them throws where the mistake is.

**A ping-pong is TWO computes, not two variables.** The shader is compiled with
the textures *hardcoded* into it. Swapping JavaScript references after the fact
changes nothing, and the simulation simply never advances — no error, no
warning, a picture that looks like frame one forever.

```js
// WRONG: the compute was built with texA baked in. This does nothing.
let src = texA, dst = texB;
const step = Fn(() => { /* reads src, writes dst */ })().compute(N);
function tick() { renderer.compute(step); [src, dst] = [dst, src]; }

// RIGHT: build both directions, alternate which one you dispatch.
const makeStep = (src, dst) => Fn(() => { /* ... */ })().compute(N);
const stepAB = makeStep(texA, texB).setName('step-ab');
const stepBA = makeStep(texB, texA).setName('step-ba');
function tick() { renderer.compute(parity ? stepBA : stepAB); parity ^= 1; }
```

**`modInt` does not exist in r185 — it is `mod`.** And it does not fail where
you wrote it: it fails while *building* the compute, with
`i.modInt is not a function` thrown from inside the node builder, far from the
offending line. Index-to-cell arithmetic is where this shows up:

```js
const ix = (i) => i.mod(int(N));   // not i.modInt(...)
const iz = (i) => i.div(int(N));
```

**Advect everything that travels with the mass, not just the mass.** In a
transport automaton — lava, fluid, heat, erosion — it is easy to move the
quantity and forget the properties riding on it. If one of those properties
also *gates* movement, the system deadlocks itself: material arrives in a cell
carrying a default value, the gate rejects it, and the front stops exactly one
cell past the source. Measured case: a lava automaton transported thickness but
not temperature, and its mobility test required temperature. It looked like
"transport is broken" and transport was fine from the start.

```js
// Each inflow carries its source value; mix by mass, not by count.
const mixed = kept.mul(current).add(inHeat).div(total.max(float(1e-5)));
temp.assign(total.greaterThan(float(1e-5)).select(mixed, temp));
```

The `max()` in the denominator is not defensive dressing: empty cells are most
of the grid, and dividing by zero there produces NaN that the gather then
spreads across the whole domain in a handful of steps.

## Debugging a compute: dump what it READS

A compute has no `console.log`. Inferring its state from the final render is
how you end up falsifying two hypotheses in a row, because the render is
several transformations away from the buffer.

Write a probe pass that dumps the values the compute *reads* into a texture you
can put on screen, and give each channel a different question:

```js
const probe = Fn(() => {
  const cx = int(ix(instanceIndex)), cz = int(iz(instanceIndex));
  textureStore(texA, vec2(cx, cz), vec4(
    textureLoad(heightTex, vec2(cx, cz)).r.div(float(MAX_H)),  // R: does this read?
    textureLoad(texB, vec2(cx, cz)).g,                          // G: storage round-trip?
    float(0.15),                                                // B: CONTROL
    1,
  ));
})().compute(CELLS).setName('probe');
```

**The constant channel is the part people skip and the part that makes it a
measurement.** Without it, two black channels do not distinguish "the compute
cannot read" from "your visualisation is not painting". Bind it through
`emissiveNode`, not `colorNode`, so lighting is not between you and the value.

Real result of exactly this probe: all three channels came back, which killed
the standing hypothesis (`textureLoad` on a `RedFormat`/`FloatType` DataTexture
returning 0) in one screenshot and sent the search somewhere else entirely.

## Sanity checks

Read the generated shader rather than guessing why something is black:

```js
const wgsl = await material.getNodeBuilderAsync?.(renderer);
console.log(await renderer.debug.getShaderAsync(scene, camera, mesh));
```

Or attach the official inspector:

```js
import { Inspector } from 'three/addons/inspector/Inspector.js';
renderer.inspector = new Inspector();
```

**Always test both backends.** A node that compiles to WGSL can still fail on
GLSL — integer handling, texture sampling and loop bounds differ. Force it:

```js
new THREE.WebGPURenderer({ forceWebGL: true })
```

## Renamed API

Old TSL names are everywhere in blog posts. See `deprecated-r185.md`; the ones
that bite most often:

| Dead | Use |
|---|---|
| `.label()` | `.setName()` |
| `.cache()` | `.isolate()` |
| `transformedNormalView/World` | `normalView` / `normalWorld` |
| `viewportResolution` | `screenSize` |
| `directionToColor()` | `packNormalToRGB()` |
| `PI2` | `Math.PI * 2` |
