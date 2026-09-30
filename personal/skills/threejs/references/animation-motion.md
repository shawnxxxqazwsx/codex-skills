# Animation and motion

## Timing

`Clock` is deprecated since r183. `Timer` replaces it, with one behavioural
difference that will bite you: **`Timer` does not compute time by itself** —
you must feed it the timestamp.

```js
const timer = new THREE.Timer();

renderer.setAnimationLoop((timestamp) => {
  timer.update(timestamp);          // forgetting this makes dt zero forever
  const dt = timer.getDelta();      // seconds since previous frame
  const t  = timer.getElapsed();
  ...
});
```

`timer.setTimescale(0.5)` for slow motion. `timer.connect(document)` pauses it
when the tab is hidden, which stops the huge `dt` spike on return that
teleports everything.

**Always multiply motion by `dt`.** `x += 0.01` moves at a speed that depends
on the user's refresh rate; at 144 Hz it is 2.4× faster than you designed.

Clamp `dt` for physics-like integration: a background tab or a slow load can
deliver a delta of several seconds, which sends objects through walls.

```js
const dt = Math.min(timer.getDelta(), 1 / 30);
```

## Skeletal and keyframe animation

```js
const mixer = new THREE.AnimationMixer(model);
const action = mixer.clipAction(gltf.animations[0]);
action.play();

// in the loop:
mixer.update(dt);
```

Crossfade rather than cut:

```js
next.reset().setEffectiveWeight(1).play();
current.crossFadeTo(next, 0.35, false);
```

Useful controls: `action.setLoop(THREE.LoopOnce)` with `clampWhenFinished`,
`action.timeScale`, `action.setEffectiveTimeScale()`. The mixer emits
`'finished'`.

**One mixer per model.** Sharing a mixer across models silently applies the
wrong tracks.

For many copies of the same animated model, `InstancedMesh` does not help —
skinning is per-instance. Bake the animation into a texture (VAT) and read it
in TSL, or accept the draw calls.

## Morph targets

```js
mesh.morphTargetInfluences[mesh.morphTargetDictionary['smile']] = 0.7;
```

Morph targets are GPU-cheap and CPU-free. Good for facial animation and shape
blending; wasteful for anything a skeleton could do.

## Camera work

Interpolate the camera's *target*, not its position, when following something.
Position-following produces motion sickness; target-following reads as intent.

```js
desired.copy(subject.position).add(offset);
camera.position.lerp(desired, 1 - Math.pow(0.001, dt));   // frame-rate safe
camera.lookAt(subject.position);
```

`1 - Math.pow(k, dt)` is the frame-rate-independent form of exponential
smoothing. A raw `lerp(a, b, 0.1)` per frame is 6× faster at 144 Hz than at
24 Hz.

**A camera watching a fast separation must be mounted on the moving object.**
A static camera loses anything travelling at 100 m/s within two seconds.

For scripted sequences, drive a plain array of keyframes and interpolate with
Catmull-Rom rather than linearly. Linear interpolation leaves visible slope
discontinuities at every knot — in a flight profile, the discarded stage
appears to overtake the vehicle.

```js
const curve = new THREE.CatmullRomCurve3(points);
camera.position.copy(curve.getPointAt(u));
```

## Physics-adjacent motion without a physics engine

Objects released from a moving parent should inherit **the near-future
velocity**, not the instantaneous one, when the parent follows an authored
path whose slope is changing. Averaging the next few seconds of the path
avoids the separated piece drifting the wrong way.

Before detaching anything, update world matrices:

```js
vehicle.updateMatrixWorld(true);
piece.getWorldPosition(p);
piece.getWorldQuaternion(q);
scene.attach(piece);          // attach() preserves world transform; add() does not
```

Skipping `updateMatrixWorld(true)` places the detached piece at wherever the
parent was last frame — at speed, hundreds of metres away.

## Animating in the shader

Anything that is a pure function of time and position belongs in TSL, where it
costs no main-thread milliseconds at all:

```js
material.positionNode = positionLocal.add(
  vec3(positionLocal.y.mul(0.3).add(time.mul(2)).sin().mul(sway), 0, 0)
);
```

Grass, foliage, flags, water, pulsing and orbiting all qualify. The rule of
thumb: if a JavaScript loop touches more than a few hundred objects per frame,
it belongs on the GPU.

For simulations with state that carries between frames — particles with
velocity, flocking, cloth — use compute shaders and `instancedArray`. See
`tsl-language.md`.

## Flicker, done right

```js
light.intensity = base * (1 + Math.sin(t * 11) * 0.15);
```

Never `light.intensity *= f` or `scale.y *= f`. Multiplicative per-frame
adjustment compounds: with `f < 1` the value decays to zero over a few seconds
and the effect quietly disappears. Always compute from a stored base value.
