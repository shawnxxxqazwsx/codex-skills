# Rigid-body physics

three.js ships **no physics engine**. What r185 ships is three *adapters* in
`examples/jsm/physics/`, and they are examples published as if they were
libraries. Read this before importing one — all four of their surprises are
silent.

| Adapter | Engine | Downloads at runtime |
|---|---|---|
| `RapierPhysics.js` | Rapier (Rust→WASM) | `cdn.skypack.dev/@dimforge/rapier3d-compat@0.17.3` |
| `JoltPhysics.js` | Jolt (C++→WASM) | `cdn.jsdelivr.net/npm/jolt-physics@1.0.0` |
| `AmmoPhysics.js` | Ammo (Bullet port) | `cdn.jsdelivr.net/gh/kripken/ammo.js@79190a1f…` |

## The four things the adapters do that you did not ask for

**1. They fetch the engine from a CDN, at a version hard-coded in three's own
source.** Not a peer dependency — a literal URL constant on line 1-3 of each
file. So: it does not work offline even after `npm install three`, and
`npm install @dimforge/rapier3d-compat` (0.19.3, Nov 2025) is *ignored* — the
adapter still pulls 0.17.3, two minors behind. The `/* @vite-ignore */` next to
each dynamic import is there because bundlers choke on it.

**2. They simulate in `setInterval`, not in your render loop.**

```js
setInterval( step, 1000 / frameRate );   // RapierPhysics:367, Jolt:288, Ammo:292
```

Wall-clock 60 Hz, unrelated to your frames. In a hidden tab browsers throttle
`setInterval` to ~1 Hz while `setAnimationLoop` stops entirely, so the two
drift apart and the scene jumps on return.

**3. They never expose `step()`.** Look at what `RapierPhysics()` returns:
`RAPIER, world, addScene, addMesh, removeMesh, setMeshPosition,
setMeshVelocity, addHeightfield, applyImpulse`. No `step`. You cannot pause,
substep, fix the timestep, or time it. And no `dispose()` either — the interval
runs forever, which is a leak the "dispose or leak" rule cannot help you with.

**4. `world.timestep = timer.getDelta()`** — variable timestep. Rapier is
deterministic only at a fixed step, so this trades away reproducibility, and a
long frame becomes a jump that tunnels through geometry.

### The measurement that matters

250 bodies, same scene, MX450:

| Engine | main-thread ms |
|---|---|
| Rapier via npm, stepped in the render loop | 2.89 |
| `RapierPhysics.js` adapter | **0.81** |

The adapter looks 3.5× cheaper. **It is not — the work moved out of the
measured window.** `setInterval` work is not attributed to the frame, so every
profiling number you collect understates the true cost. This is the most
expensive kind of wrong: it reads as a win.

### Two more traps in `RapierPhysics.js` specifically

**Instance scale is destroyed.** Syncing an `InstancedMesh` composes with a
module-level constant:

```js
const _scale = new Vector3( 1, 1, 1 );              // line 7
_matrix.compose( position, _quaternion, _scale );   // line 345
```

Every instance is redrawn at the source geometry's size, so per-instance scale
— the thing `InstancedMesh` is *for* — is silently flattened on the first step.

**Colliders come from `geometry.type`**, via `getShape()`: `BoxGeometry`,
`RoundedBoxGeometry`, `SphereGeometry`, `IcosahedronGeometry`,
`CylinderGeometry`, `CapsuleGeometry`, and `BufferGeometry` → trimesh.
Everything else hits `console.error('Unsupported geometry type')` and returns
`null` — **including `PlaneGeometry`**, the most obvious floor in the world.
Merged geometry from `BufferGeometryUtils` has no `.parameters`, so it becomes
a trimesh whether you wanted one or not.

## Rolling your own is about forty lines

Use the engine directly when any of the above matters. `rapier3d-compat` ships
the WASM inline as base64 (`rapier.mjs` is 2.2 MB), so an import map is enough
— no bundler, no CDN, no network:

```json
{ "imports": { "rapier": "./node_modules/@dimforge/rapier3d-compat/rapier.mjs" } }
```

```js
const RAPIER = (await import('rapier')).default;
await RAPIER.init();                       // decodes the embedded wasm
const world = new RAPIER.World({ x: 0, y: -9.81, z: 0 });
```

The loop, with the fixed-step accumulator the adapter does not give you:

```js
const FIXED_DT = 1 / 60, MAX_SUBSTEPS = 5;
let acc = 0;

function step(dt) {
  acc += Math.min(dt, 0.25);            // clamp, or a stall spirals
  let n = 0;
  while (acc >= FIXED_DT && n < MAX_SUBSTEPS) { world.step(); acc -= FIXED_DT; n++; }
  if (n === MAX_SUBSTEPS) acc = 0;      // drop the backlog, never carry it
  if (n > 0) syncMeshes();
}
```

`MAX_SUBSTEPS` is not optional. Without it, one long frame queues substeps that
make the next frame longer, which queues more: the simulation never catches up
and the tab locks.

## Cost: what "a lot of physics" actually means

Bodies dropped into a 40 m bowl, Rapier 0.19.3, `InstancedMesh`, MX450, 1280×800:

| Bodies | main-thread ms | 60 Hz budget |
|---|---|---|
| 100 | 1.22 | 7 % |
| 250 | 2.24 | 13 % |
| 500 | 4.01 | 24 % |
| 1 000 | 7.79 | 47 % |
| 2 000 | **18.37** | **110 %** |
| 4 000 | 76.93 | 462 % |

Two things to take from it. **The curve is linear to ~1 000 and superlinear
after** (2 000→4 000 is ×4.2 for ×2 bodies) — because the cost tracks
*contacts*, not bodies, and contacts grow with density in a fixed volume. So a
body count from someone else's demo tells you nothing about your scene.

And **the budget breaks between 1 000 and 2 000**, where `fps` is still 60 and
tells you nothing. This is the case `pitfalls-production.md` describes in the
abstract: physics is the workload that finally makes `main-thread ms` the
number that discriminates, because unlike almost everything else in three.js
you cannot move it to the GPU.

**Instance your bodies.** 500 bodies, same simulation:

| | main-thread ms | drawables |
|---|---|---|
| `InstancedMesh` | 4.86 | 3 |
| one `Mesh` each | 11.50 | 501 |

**But the table above is the worst case, and the reason is sleeping.** Rapier
puts settled bodies to sleep, so cost tracks the **awake** count, not the total.
Same engine, volcanic bombs landing on a hillside over time: 24 vs 340 live
bodies moved main-thread by **9 %** (1.54 → 1.68 ms), because everything already
at rest on the slope costs nothing. The bowl measurements are expensive because
all the bodies land together and stay in mutual contact — a pile is the shape
that defeats sleeping.

So "how many bodies can I afford" has no answer without knowing how many are
moving at once. Budget for the peak of simultaneous motion, and be aware that a
scene which never settles (anything continuously re-emitting) never gets the
discount.

## Reproducible captures need a fixed step *count*, not a fixed step

`SKILL.md` says to seed your randomness so two captures can be diffed. With a
simulation that is not enough, and the shortfall is easy to miss.

Measured on the same URL twice, seeded, fixed timestep: **5.83 % of pixels
differ.** The step *size* is constant, but each run reaches the screenshot with
a different number of steps behind it, because the accumulator consumes real
time. Freeze the count instead — advance exactly N steps, then stop:

```js
function stepExactly(n) { for (let i = 0; i < n; i++) world.step(); syncMeshes(); }
```

Same two runs: **0.00 % of pixels.** Now an A/B measures the change instead of
the moment the shutter fired. Note this is impossible with the official
adapter, which owns its own interval and exposes no `step()`.

## Gyroscopic stability: what the engines actually do

A wheel thrown downhill stays upright because angular momentum resists tipping —
the same reason a moving bicycle does not fall. Whether your engine reproduces
that is **not documented anywhere**: Rapier's and Jolt's guides never mention
gyroscopic effects, and although Bullet implements them, the `ammo.js` build
three pulls **does not expose `setFlags` or the `GYROSCOPIC_FORCE` constants**
(only `setDamping` and `setAngularFactor`). So it has to be measured.

Measured, on a 200 m slope, same launch impulse, spin as the only variable:

| Spin | Distance before tipping |
|---|---|
| 4 rad/s | 225 m |
| 8 | 235 m (upright) |
| 22 | 340 m (upright) |
| 32 | **412 m (upright)** |

**Rapier reproduces it.** Not because it integrates `ω × Iω` — because
conserving angular momentum through the inertia tensor is already enough for
directional stability. Two practical consequences: give the body the *right*
tensor (a tyre has its mass at the rim, `I = m·r²`, twice a solid cylinder's
`½m·r²` — via `setAdditionalMassProperties`), and expect stability to scale with
spin without doing anything special.

### Do not add the explicit term by hand

The missing term in Euler's equation is `τ = −ω × (I·ω)`, and adding it with
`applyTorqueImpulse` looks like free rigour. Measured, same scene, at 60 Hz:

| Spin | Rapier alone | With the explicit term |
|---|---|---|
| 8 rad/s | 235 m upright | 99 m, tipped |
| 32 | 412 m upright | 40 m, tipped |
| 48 | 216 m | 22 m, tipped after **81 steps** (1.35 s) |

It makes things *worse*, and worse the faster it spins — the torque goes with
`ω²`, so an explicit impulse at `dt = 1/60` diverges. **This is exactly why
engines omit it.** At `dt = 1/240` it stops blowing up (48 rad/s survives 1011
steps instead of 81), so the term is not wrong, it is stiff. Unless you are
modelling precession specifically, leave it out and spend the budget on the
inertia tensor instead.

## Terrain

`RAPIER.ColliderDesc.heightfield(nrows, ncols, heights, scale)` takes a
`Float32Array` in **column-major** order and spans `-scale/2 … +scale/2`.
Feeding it row-major does not error — it gives you a transposed collider, which
is worse, because bodies still land on *something*. Build the visual mesh and
the collider from the same array, and test on an asymmetric patch: a symmetric
bowl hides a transposition completely.

## Checking a fact

```bash
ls node_modules/three/examples/jsm/physics/
grep -n "_PATH =\|setInterval\|_scale =" node_modules/three/examples/jsm/physics/*.js
npm view @dimforge/rapier3d-compat version
```
