# Production pitfalls

Failures that cost real hours. Every one of these looks like something else,
which is why they are expensive.

## Measurement lies

**`renderer.info` after a post-processing chain reports one quad.**
Every pass calls `render()`, and `render()` resets the counters. Read them
after `pipeline.render()` and you get the final fullscreen quad: 1 draw call,
2 triangles. It looks like a spectacularly optimised scene.

```js
renderer.info.autoReset = false;
// ... one full frame ...
read(renderer.info.render);
renderer.info.reset();
```

**`renderer.info.render.calls` is not comparable between `WebGLRenderer` and
`WebGPURenderer`.** Measured on the same scene: the legacy renderer reported 19
draw calls, the `RenderPipeline` path reported ~2000 — and the figure did *not*
scale with content (1 000 particles produced a higher count than 200 000, and
it varied between runs). `pipeline.render()` fans out into many internal
`render()` calls, so a per-frame sample taken over rAF ticks counts pipeline
internals, not scene objects. Forcing the WebGL backend does not change it, so
this is the renderer class, not the backend. Use it to spot changes within one
renderer; never to compare two.

**A monotonic three-point sweep is not a measurement without a repeated
control.** A parameter sweep produced 19 ms → 112 → 106 with main-thread flat
at 4 ms, which read cleanly as "cost tracks this parameter" and had a plausible
mechanism ready to hand. It was environment drift: re-running the *cheap*
setting at the end of a later batch gave 97 ms for the case that had just
measured 19 — with the suspected effect disabled, which could only be cheaper.
Order the runs so the cheap case repeats **last** as well as first; a control
only at the start proves the first run was clean and nothing else. **A
plausible explanation is exactly what makes a bad measurement dangerous**,
because it stops you re-running.

**Measuring a system with accumulation before it saturates measures the
transient.** A harness that samples 9 seconds from page load will catch a pool
that has not filled: a power dial that spawned one body every 0.06 s into a
340-body pool measured level 1 as *more* expensive than level 4, because no
level had reached steady state. Two different fast-forwards are needed and they
are not interchangeable — one that advances N steps and **keeps running** (to
measure in régime), and one that advances N steps and **freezes** (for
comparable screenshots).

**A metal with `metalness: 1` and very low roughness loses its own colour.**
A metal's albedo tints its reflection, so a near-mirror finish shows you the
environment, not the material: blued steel, brass and chrome all come out the
same pale grey. If a coloured metal reads as silver, drop metalness to ~0.9
and raise roughness to ~0.15 rather than saturating the colour, which just
makes it look like painted plastic.

**Studio environment plus strong lights plus high exposure blows out
everything.** `RoomEnvironment` already lights a scene on its own. Adding three
directional lights and exposure above 1 clips the highlights, and clipped
highlights erase surface finish — every material converges on white. If a scene
looks "bright but flat", cut exposure before touching anything else.

**Frame rate measured in a headless or unfocused browser is fiction.**
Chrome throttles `requestAnimationFrame` to about 1 fps without focus, and
`gl.finish()` does not synchronise. Measure in a real, focused window —
`scripts/verify_scene.mjs` launches one correctly.

**60 fps means nothing on a 60 Hz display.** Both a trivial scene and one that
is one feature from stuttering report 60. Read main-thread milliseconds per
frame: it degrades linearly and shows actual headroom.

**vsync caps mean `frame ms` too, not just fps.** A 60 Hz display pins mean
frame time at exactly 16.67 ms, so every configuration under budget measures
identical. Building up the desk scene — bare, then shadows, then instanced
foliage, then an instanced keyboard — reported 16.67 ms at every step, and only
the AO pass pushed it off the cap. Below the cap, an A/B is not a measurement:
either add load until something exceeds the budget, or compare a configuration
you already know is over it.

**A frame time in the hundreds of ms with ~1–3 fps is a focus problem, not a
performance problem.** Measured 307 ms/frame on a scene that had just measured
17; rerunning in a focused window gave 16.67. If a number is an order of
magnitude off the previous run, re-measure before you go looking for the cause.

**The WebGL2 fallback is not automatically the slow path.** Same desk scene,
same machine (GeForce MX450, 1280×800): WebGPU 21.1 ms/frame, forced WebGL2
20.3 ms. On a shader-bound, low-geometry scene the backends are within noise of
each other; WebGPU pays off with compute and with many draw calls, not
everywhere. Measure both rather than assuming.

**A second Chrome process silently ignores `--remote-debugging-port`.**
If Chrome is already running with the default profile, a new launch delegates
to the existing instance and your automation attaches to nothing. Always pass
a dedicated `--user-data-dir`.

## Things that fail silently

**An effect whose parameters are in world units bands the image and reports
nothing.** `ao()`'s `radius` defaults to 0.25 view-space units — 25 cm. On a
1 km terrain that samples pure depth-quantisation noise and paints hard terrace
bands along the depth isolines. Zero console errors, zero audit findings,
unchanged frame rate, and fixing it costs nothing (`radius = 9` on that scene
was both correct and the same speed). Too *small* for the scene is equally wrong
in the other direction: on a 1.2 m desk, `radius = 0.03` puts a bright halo
around every object. Any post effect that reconstructs positions from depth —
`ao`, `dof`, `ssr`, `ssgi` — has to be told the scale it is working at. See
`postfx-catalog.md`.

**A child placed on the wrong local face of a rotated pivot looks like a
missing material.** A laptop lid hinges from the rear edge, so with the lid
closed the face that will point at the user is local **−Y**, not +Y — the axis
that "obviously" points up once the lid is open. Put the screen at +Y and it
lands on the back of the lid: from the front you see bare grey shell, from
behind a black rectangle. No error, no audit finding, and it reads as "the
screen material did not load". When you attach something to a pivot, reason
about the local axes **before** the rotation, and check a screenshot from both
sides — `verify_scene.mjs --orbit 3` exists for this.

**`PCFSoftShadowMap` downgrades without stopping — but only on the legacy
`WebGLRenderer`.** That warning comes from `WebGLShadowMap.js`. On
`WebGPURenderer` the node path maps the type to a real `PCFSoftShadowFilter`, so
the setting is valid and the blanket advice to switch to VSM costs 8× for
nothing. Details in `deprecated-r185.md`.

**Deprecated API keeps working.** `Clock`, `PostProcessing`, the `*Async`
family all run fine and warn once. The page works, so nobody looks at the
console. Read it anyway; see `deprecated-r185.md`.

**Chrome's `--print-to-pdf` writes nothing if the target file is open.**
Exit code 0, no error, no file written. Checking `exists()` then passes
against the *old* file. Delete the output first so the lock surfaces as a
`PermissionError`, and verify the content, not the file's existence.

**`three.module.js` alone is not enough.** Since r166 it imports
`three.core.js` as a sibling. Vendor both, or the page dies on a 404 naming a
file you never wrote.

**Mixing `three` and `three/webgpu` gives two class identities.**
`instanceof` starts returning false and the errors are nonsensical. Map both
specifiers to the same build in the importmap.

## Things that degrade quietly

**Multiplicative per-frame adjustment collapses to zero.**
`scale.y *= f` or `light.intensity *= f` compounds every frame. With `f < 1`
the value decays to nothing over a few seconds and the effect vanishes.
Always compute from a stored base: `value = base * f(t)`.

**Frame-rate-dependent lerp.** `pos.lerp(target, 0.1)` per frame moves 6×
faster at 144 Hz than at 24 Hz. Use `1 - Math.pow(k, dt)`.

**Unclamped `dt` teleports objects.** A backgrounded tab returns with a delta
of seconds. Clamp to `1/30`.

**Everything leaks unless disposed.** Geometries, materials, textures and
render targets are not garbage collected. If
`renderer.info.memory.geometries` climbs while the scene looks static, that is
your leak.

## Things that look like a different bug

**Detaching a child without updating world matrices** places it wherever the
parent was last frame — at 100 m/s, hundreds of metres off. Call
`updateMatrixWorld(true)` first, and use `scene.attach()` (preserves the world
transform) rather than `scene.add()`.

**Two transparent objects near the same centre sort arbitrarily, and anything
with `depthWrite: false` cannot defend itself.**

three.js sorts transparent objects back-to-front by the distance from their
*centre* to the camera. Two objects centred near the same point are a tie, and
the winner can differ between scenes, frames or backends. Whichever draws
second still runs its depth test — against a buffer that a `depthWrite: false`
object never wrote to. So it passes, and paints straight over it.

The classic pairing is a large transparent ground/water plane and a particle
system: the sea draws over the eruption column that is clearly in front of it.
Nothing errors, and it can look correct until the camera moves.

```js
water.renderOrder = 0;
particles.renderOrder = 10;    // explicit: the sort cannot resolve a tie
```

Any time a `depthWrite: false` object shares the frame with another
transparent object, set `renderOrder` on both. Do not rely on the sort.

The same rule decides cross-faded terrain tiles: the most detailed tile must
draw last, or the coarse one covers it.

**`logarithmicDepthBuffer` breaks depth-based post-processing.** Bokeh, DOF
and SSAO all read depth. It fixes z-fighting and ruins the effects. Scale the
world down instead.

**Float32 wobble past ~100 km.** Vertices jitter, shadows crawl. It reads as a
shader bug; it is precision. Scale the world, or keep the camera at the origin
and move the world around it.

**Radial `ExtrudeGeometry` rotation is `rotation.y = -a`.** If you find
yourself adding 90° to make it line up, the profile is authored in the wrong
plane.

**A static camera loses a fast-moving subject in about two seconds.** Mount
the camera on the moving object for separation or flyby shots.

**Aerial imagery does not cover water.** Ortho sources return black over sea.
Composite over a global basemap and colour-match, or the coastline appears
cut out.

## Performance, in the order that pays

1. **Draw calls before triangles.** A thousand `Mesh` objects at 60 Hz is not
   happening; the same thousand as one `InstancedMesh` is trivial. Modern GPUs
   eat triangles and choke on state changes.
2. **Move per-item JS loops to the GPU.** The most common cause of a blown
   frame budget is a JavaScript loop over particles or vertices. Compute
   shaders exist.
3. **Cap pixel ratio at 2.** Fragment cost is quadratic in resolution.
4. **Scale post-processing resolution** before dropping an effect —
   `pass.setResolutionScale(0.5)` is usually invisible.
5. **Shadow map size and camera extent**, not shadow type, dominate shadow
   cost.
6. **Texture memory is usually the real ceiling on mobile.** KTX2 stays
   compressed in VRAM; JPEG does not.
7. **Count the noise calls in a procedural material that covers the screen.**
   A `MeshStandardNodeMaterial` whose `colorNode` and `roughnessNode` came to 7
   `mx_*noise*` evaluations per fragment cost **12 ms/frame** on a GeForce MX450
   at 1280×800 — on a desk made of six boxes. Dropping to 5 (reusing one fractal
   for both the grain and the broad tone instead of sampling twice) took the
   frame from 30.9 to 19.1 ms. Two rules follow: sample once and reuse the
   result across `*Node` outputs (call an `Fn` twice and it is evaluated twice),
   and if the surface fills the frame, bake the pattern to a texture instead of
   evaluating it per pixel per frame.

8. **Physics is the one workload you cannot move to the GPU.** Rules 1 and 2
   both say "push it down"; a rigid-body solver is where that advice runs out.
   It is WASM on the main thread, and its cost tracks **contacts, not bodies**,
   so it is superlinear in density: 100→1 000 bodies dropped in the same bowl
   scaled linearly (1.2→7.8 ms), 2 000→4 000 went ×4.2 for ×2 bodies
   (18.4→76.9 ms). The 60 Hz budget broke between 1 000 and 2 000 while `fps`
   still read 60. Instance the bodies (500 of them: 4.9 ms instanced vs 11.5 ms
   as separate meshes), cap the count, and if you need more, a Web Worker is the
   only remaining direction. See `references/physics.md`.

9. **A particle system costs what it COVERS, not how many particles it has.**
   Fragments, not vertices, and overdraw multiplies them. A 28 000-sprite
   eruption column ran at **90 ms/frame** while a 90 000-particle ash plume in
   another scene ran at 31 — the difference was sprite scale 38 vs 11, and area
   goes as the square. Dropping to 28 000 sprites at scale 14 took the frame
   from 90 to 27 ms. The A/B pointed at the particles (without them, 19 ms;
   without bloom, 88), but only the cross-scene comparison explained it.
   **Fewer and smaller beats more and bigger**, and it also happens to be how
   the phenomenon works: smoke is a few large blobs, sparks are many small ones.

## Making emissive things look right

**`AdditiveBlending` over thousands of stacked sprites saturates to white no
matter what colour you feed it.** Colours multiplied ×9 summed to pure white,
and bloom then spread that flash across the entire frame — the same veil as
bloom over a white background, this time generated from inside the scene.
`NormalBlending` at ×3.4 reads as fire. Additive is for isolated sparks; smoke
**occludes**, it does not add.

**`shapeCircle()` cuts a solid disc**, and thousands of solid discs read as
balls, not as a column. A radial falloff over `uv()` melts them together:

```js
material.opacityNode = uv().sub(0.5).length().oneMinus().smoothstep(0.1, 0.5);
```

**Glowing material wants a near-black albedo with all the brightness in
emission.** Using one bright colour for both `colorNode` and `emissiveNode`
means the sun lights the pale albedo and the result reads as sand, not as lava.
Splitting them — albedo `0x140805`→`0x4a1206`, emission `0x5e1403`→`0xffb347` —
is what produces dark crust floating on an incandescent flow. If it looks like
painted plastic, the albedo is too light, not the emission too weak.

## Development hygiene

**Serve with caching disabled.** A default static server lets the browser
cache ES modules, so after an edit you are debugging the previous version.
This failure is indistinguishable from "my fix did not work" and reliably
costs an afternoon. Use `scripts/serve.mjs`.

**Verify before claiming.** Run `scripts/verify_scene.mjs`, read the console
errors, look at the screenshot. "It should work" is not a result.
