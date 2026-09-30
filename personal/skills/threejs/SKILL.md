---
name: threejs
description: Build 3D scenes, environments, procedural geometry, physics, animation and shaders with three.js r185 (WebGPU/TSL first, WebGL fallback). Use when creating or debugging any three.js work - scenes, terrain, water, sky, particles, materials, shaders, GLTF loading, post-processing, camera work, instancing, rigid-body physics, or when a WebGL/WebGPU canvas is slow, black, or throwing errors. Trigger on three.js, threejs, THREE, WebGL, WebGPU, TSL, GLSL shader, 3D scene, 3D web, r3f, react-three-fiber, glTF, GLB, orbit controls, bloom, raycasting, Rapier, Jolt, Ammo, rigid body, collider.
---

# three.js r185

You already know how to write three.js. What you do not reliably know is
**which API is still alive in r185**. Your default output is three.js as of
roughly 2023: `THREE.Clock`, `EffectComposer`, `requestAnimationFrame`,
`WebGLRenderer`. All four are either deprecated or superseded.

This skill exists to correct that, and to make you verify what you built
instead of assuming it works.

## Non-negotiables

Apply these to every scene you write, without being asked.

1. **`WebGPURenderer`, not `WebGLRenderer`.** It falls back to WebGL2 on its
   own when WebGPU is unavailable — you lose nothing and gain compute shaders,
   node materials and the TSL post-processing catalogue.
2. **`renderer.setAnimationLoop(fn)`, not `requestAnimationFrame`.** Required
   for WebXR and for WebGPU's async submission. `rAF` silently breaks both.
3. **`Timer`, not `Clock`.** `Clock` is `@deprecated since r183` and prints a
   console warning. `Timer` needs an explicit `timer.update(timestamp)` call.
4. **Import from `three/webgpu` and `three/tsl`**, not bare `three`, whenever
   you use nodes, compute or the modern post-processing chain.
5. **Never claim a scene works until `scripts/verify_scene.mjs` says so.**
   Zero console errors is a measurement, not an opinion.

The canonical skeleton every scene starts from:

```js
import * as THREE from 'three/webgpu';   // Timer ships in core: THREE.Timer

const renderer = new THREE.WebGPURenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
await renderer.init();                 // WebGPU needs this before first render

const timer = new THREE.Timer();

renderer.setAnimationLoop((timestamp) => {
  timer.update(timestamp);
  const dt = timer.getDelta();
  // ...
  renderer.render(scene, camera);
});
```

Read `references/canon-r185.md` before writing the first line of any new scene.

## Router

Load only what the task needs. Do not read every reference.

| The task involves | Read |
|---|---|
| **Anything non-trivial, before writing a helper** | `references/capabilities.md` |
| Any new scene, renderer setup, colour, tone mapping, importmap | `references/canon-r185.md` |
| An API you are about to use that might be dead | `references/deprecated-r185.md` |
| Writing a shader, custom material, GPU compute, particles | `references/tsl-language.md` |
| Sky, water, terrain, fog, HDRI/IBL, scale, planetary distance | `references/environments.md` |
| Building geometry in code, instancing, CSG, extrusion, LOD | `references/geometry-procedural.md` |
| Animation, mixer, skinning, morph, cameras, timelines | `references/animation-motion.md` |
| Rigid bodies, collisions, gravity, ragdolls, vehicles | `references/physics.md` |
| Bloom, AO, SSR, DOF, godrays, antialiasing, colour grading | `references/postfx-catalog.md` |
| Putting a canvas in a real page: scroll, DOM, mobile, a11y | `references/web-integration.md` |
| It renders but is slow, black, flickering, or leaking memory | `references/pitfalls-production.md` |

**To start a scene, do not write boilerplate — generate it:**

```bash
node scripts/new_scene.mjs --dir path/to/scene --title "Name"
```

It walks up the tree to find the installed `three`, writes an importmap with
the correct relative path for that depth, and falls back to a CDN when there is
no install. A hand-written importmap at the wrong depth fails as a bare
specifier error that tells you nothing.

## Hard rules

**Scale is a decision, not a detail.** Fix `1 unit = 1 metre` and write it
down. Float32 precision visibly wobbles past ~100 km from the origin; scale the
world down rather than pushing coordinates up.

**Never trust `renderer.info` after a post-processing chain.** Each pass calls
`render()`, which resets the counters, so you read only the final fullscreen
quad. Set `info.autoReset = false`, reset once per frame yourself.

**Dispose or leak.** Geometries, materials, textures and render targets are not
garbage collected. Every `remove()` needs a matching `dispose()`.

**Move work to the GPU before optimising it on the CPU.** A per-particle JS
loop is the single most common reason a three.js page misses frame budget.
Compute shaders exist; see `references/tsl-language.md`.

**Do not add glow to hide weak geometry.** Build the form, then the material,
then the light, then the effect. Bloom applied to primitives just makes bright
primitives.

**An effect's default parameters belong to the scene it was authored for.**
Anything in world or view-space units — `ao().radius`, `dof` focus distance,
`ssr` thickness, fog density, shadow bias — is wrong by orders of magnitude the
moment your scene is not a tabletop. The failure is silent: correct code, plausible
image, no error. When you set `1 unit = 1 metre`, go back through the effect
parameters and ask what each one means in metres.

## Red flags

Each of these means stop and check the relevant reference.

| You are about to write | Problem |
|---|---|
| `new THREE.WebGLRenderer(` | Use `WebGPURenderer`; it falls back by itself |
| `requestAnimationFrame(animate)` | Use `renderer.setAnimationLoop` |
| `new THREE.Clock()` | Deprecated since r183 — use `Timer` |
| `THREE.mrt(`, `THREE.pass(`, `THREE.uv(` | Node functions are **not** on the `three/webgpu` namespace. Import from `three/tsl`, or `THREE.TSL.*` |
| `ao(depth, normal, camera)` and nothing else | `radius`/`thickness` are view-space **metres**; 0.25 bands anything bigger than a room, and a radius below the scene's scale haloes every silhouette |
| `bloom(…)` on a white or near-white background | The backdrop is 1.0, so it passes any threshold: the "glow" is a veil over the subject. No threshold setting fixes it |
| `new THREE.Color(hex).convertSRGBToLinear()` | A `Color` from hex is **already** linear. Converting twice darkens everything, silently. In TSL write `color(hex)` |
| `aoPass.setResolutionScale(` | Effect nodes expose `resolutionScale` as a *property*; only `PassNode` has the method |
| `THREE.VSMShadowMap` "because PCF-soft is deprecated" | It is not, on `WebGPURenderer` — and VSM measured 8× the cost |
| `new EffectComposer(` | Legacy chain — use `RenderPipeline` + TSL nodes |
| `new PostProcessing(` | Renamed to `RenderPipeline` in r183 |
| `renderer.renderAsync()` | Whole `*Async` family dead — `await renderer.init()` once |
| `for (…) positions[i] += …` per frame | Move it to a compute shader |
| `outputEncoding` / `sRGBEncoding` | Removed — `outputColorSpace` / `SRGBColorSpace` |
| `transparent: true` + `depthWrite: false` | Set `renderOrder` on every transparent object sharing the frame |
| `await RapierPhysics()` and nothing else | It fetches the engine **from a CDN** at a version pinned in three's source, simulates in its own `setInterval`, exposes no `step()` and no `dispose()`. See `references/physics.md` before you rely on it |
| `physics.addMesh(instancedMesh, …)` via the adapter | It re-composes every instance with a constant `_scale` of (1,1,1) and flattens per-instance scale on the first step |
| `vertexColors: true` **and** `colorNode = vertexColor()` | `NodeMaterial` *multiplies* by the attribute when the flag is set, so the colour lands twice and the mesh darkens silently. Pick one |
| A ping-pong compute that swaps `src`/`dst` in JavaScript | The textures are baked into the compiled shader. Build **both** directions and alternate which you dispatch, or the simulation silently never advances |
| `i.modInt(` in a compute | Not in r185 — it is `mod`. And it throws from inside the node builder, nowhere near your line |
| A transport automaton that moves one quantity | Advect **everything** riding on the mass. If a property also gates movement, unadvected material arrives inert and the front stops one cell out |
| `AdditiveBlending` on thousands of stacked sprites | Saturates to white regardless of colour, and bloom then spreads it over the frame. Smoke occludes; additive is for isolated sparks |
| A bright colour in both `colorNode` and `emissiveNode` | The sun lights the pale albedo and it reads as sand, not as lava. Near-black albedo, brightness in emission |
| A helper for noise/sampling/physics/IK/decals/simplify | Check `references/capabilities.md` — it probably ships |
| A metal that renders black | No `scene.environment`. `RoomEnvironment` is one line |
| "it looks fine" with no screenshot | Run `scripts/verify_scene.mjs --orbit 3` |

## Verification loop

Never finish a scene without this. It is the difference between "should work"
and "works".

```bash
node scripts/serve.mjs --port 8765 --root .          # no-store, always
node scripts/verify_scene.mjs --url http://127.0.0.1:8765/ \
     --json report.json --out shot.png --orbit 3
```

**It works on any three.js page, including ones you did not write.** three.js
announces every `Scene` and `Renderer` to `__THREE_DEVTOOLS__` in their
constructors; the harness installs that global before the page loads and picks
them up, then wraps `render()` to catch the active camera. Nothing to add to
the project.

Exposing the scene explicitly is still slightly more reliable, and costs a line:

```js
window.__scene = { scene, camera, renderer, controls };
```

It checks three independent things, because they fail independently:

1. **Did it crash?** — console errors and exceptions.
2. **Is it fast?** — main-thread milliseconds per frame.
3. **Is it correct?** — the scene-graph audit.

The third exists because **a wrong image throws nothing and costs nothing**.
Draw-order faults, a sky dome inside fog, a normal map tagged sRGB, a shadow
frustum that misses the scene: all of them report zero errors and full frame
rate. Performance numbers cannot see them. Treat an `audit` error as a
failure exactly like an exception — the harness already does, via `ok`.

`--orbit N` captures from N angles. Do this by default: draw-order and culling
faults are angle-dependent, and the head-on frame is the one most likely to
look fine. **Look at the screenshots.** The audit catches known structural
faults; it cannot tell you the composition is ugly or the water reads as rock.

### Four lines of scene code that make the screenshots worth comparing

The harness captures whatever the page renders. These make two captures
*comparable*, which is what turns a screenshot into a measurement:

1. **Seed your randomness.** `Math.random()` in scene construction means every
   run builds a different scene and no two captures can be diffed. A four-line
   LCG is enough. Payoff: two runs of the same URL came out **pixel-identical**,
   so a 1.5 % pixel difference between two settings was provably the setting and
   not noise. Without it that experiment is not possible.
2. **Expose your named views through the query string,** not only through
   keyboard shortcuts. `verify_scene.mjs` orbits, but it cannot press keys, so a
   detail view reachable only with `6` cannot be captured. `?view=6` can.
3. **If you are recreating a reference image, put it in the page** — a fixed
   `<figure>` in a corner at ~1/6 width, with a flag to hide it. Every capture
   then arrives as a side-by-side, and framing and colour errors that look fine
   in isolation stop looking fine. Judging a likeness from memory always flatters
   the copy.
4. **If the scene simulates anything, freeze the step *count*, not the step
   size.** Seeding is not enough once physics, cloth or a solver is running: a
   fixed timestep makes the sequence deterministic, but each run still reaches
   the screenshot with a different number of steps behind it, because the
   accumulator consumes real time. Measured on one URL captured twice, seeded
   and fixed-step: **5.83 % of pixels differed**. With a `?steps=N` flag that
   advances exactly N steps and stops: **0.00 %**. See `references/physics.md`.
5. **If the scene accumulates, you need a second fast-forward that keeps
   running.** `?steps=N` freezes, which is right for screenshots and wrong for
   timing: the harness samples ~9 s from load, so a system still filling its
   pool is measured in its transient — a power dial once measured level 1 as
   *more* expensive than level 4 for exactly this reason. Add `?warm=N`, which
   advances N steps and **continues**. Freezing and warming are two different
   needs; one flag cannot serve both.

Read the output as follows:

- **`errors` / `exceptions` must be 0.** Nothing else matters until they are.
- **`fps` is meaningless when `vsyncCapped` is true.** A 60 Hz display reports
  60 fps for both a trivial scene and one that is one feature from stuttering.
- **`main-thread ms` is the number that discriminates.** It degrades linearly
  and shows real headroom. Under ~8 ms mean on a 60 Hz budget is comfortable;
  over ~12 ms you are one dropped frame from visible stutter.
- **`draw calls` and `triangles`** come from a dedicated single-frame sample
  with `autoReset` disabled, so they are the true per-frame cost.

Measure in a real, focused window — never headless. An unfocused Chrome
throttles `requestAnimationFrame` to about 1 fps and every timing you collect
is fiction. `verify_scene.mjs` already launches Chrome correctly; do not
replace it with a headless Playwright run.

## Checking a fact

When unsure whether an API still exists, check the installed package rather
than guessing — the answer is on disk:

```bash
grep -rn "@deprecated" node_modules/three/src/ | grep -i "<symbol>"
node -e "const t=require('three'); console.log(typeof t.<Symbol>)"
```

Three.js is the fastest-moving major library in the browser 3D space. A
confident answer from memory about r150-era API is the failure mode this skill
prevents.
