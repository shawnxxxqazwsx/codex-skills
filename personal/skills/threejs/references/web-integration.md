# Putting a canvas in a real page

A demo fills the window. A product does not. Most three.js advice assumes the
demo case and breaks the moment the canvas shares a page.

## Sizing to a container, not the window

```js
const container = document.querySelector('#viewer');

const resize = () => {
  const { clientWidth: w, clientHeight: h } = container;
  if (!w || !h) return;                    // hidden container: skip, do not divide by zero
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h, false);           // false: do not write inline CSS size
  pipeline?.setSize(w, h);
};

new ResizeObserver(resize).observe(container);
```

`ResizeObserver`, not `window.onresize` — a container can change size when the
window does not (sidebar, accordion, flex reflow).

The `false` third argument matters: with `true`, three.js sets inline `width`
and `height` styles on the canvas and fights your CSS. Let CSS own layout:

```css
#viewer { position: relative; aspect-ratio: 16 / 9; }
#viewer canvas { width: 100%; height: 100%; display: block; }
```

## Do not render what nobody sees

An offscreen canvas rendering at 60 Hz is pure battery drain.

```js
const io = new IntersectionObserver(([entry]) => {
  renderer.setAnimationLoop(entry.isIntersecting ? frame : null);
});
io.observe(container);

document.addEventListener('visibilitychange', () => {
  renderer.setAnimationLoop(document.hidden ? null : frame);
});
```

`setAnimationLoop(null)` stops cleanly. This is a real advantage over `rAF`,
where you have to track the handle and cancel it.

For a static scene, render on demand instead of continuously:

```js
controls.addEventListener('change', () => { needsRender = true; });
// in the loop: if (!needsRender) return; needsRender = false;
```

## Scroll-driven scenes

Read scroll once per frame; never do work inside the scroll event.

```js
let scrollProgress = 0;
addEventListener('scroll', () => {
  const r = container.getBoundingClientRect();
  scrollProgress = THREE.MathUtils.clamp(-r.top / (r.height - innerHeight), 0, 1);
}, { passive: true });
```

`{ passive: true }` keeps scrolling smooth. Apply `scrollProgress` in the
animation loop, smoothed — mapping it directly to a camera position makes the
scene stutter exactly as much as the scroll does.

## Loading

A blank canvas reads as broken. Always show progress:

```js
THREE.DefaultLoadingManager.onProgress = (url, loaded, total) => {
  bar.style.width = `${(loaded / total) * 100}%`;
};
THREE.DefaultLoadingManager.onLoad = () => overlay.remove();
```

Compress what you ship. A raw glTF is often 10× larger than it needs to be:

| Loader | For | Saving |
|---|---|---|
| `DRACOLoader` | mesh geometry | 5-10× |
| `KTX2Loader` | textures (GPU-compressed) | 4-6×, and less VRAM |
| `meshopt` | geometry + animation | fast decode |

KTX2 matters more than it looks: a JPEG must be decoded to raw RGBA in VRAM,
while KTX2 stays compressed on the GPU. Four 2K JPEGs are 64 MB of VRAM.

Set the decoder paths, and reuse one loader instance — each `DRACOLoader`
spawns its own worker pool.

## Mobile

- Cap `setPixelRatio` at 2. Phones report 3-4; the fragment cost is quadratic
  and the difference is invisible.
- Halve post-processing resolution: `pass.setResolutionScale(0.5)`.
- Touch needs `touch-action: none` on the canvas or the browser steals the
  gesture for scrolling.
- Handle context loss — mobile browsers drop WebGL contexts when backgrounded:

```js
renderer.domElement.addEventListener('webglcontextlost', (e) => {
  e.preventDefault();
  renderer.setAnimationLoop(null);
});
```

- Test the WebGL fallback path explicitly (`forceWebGL: true`). WebGPU coverage
  on mobile is still partial, so for many users the fallback *is* the product.

## Accessibility

A `<canvas>` is invisible to assistive technology. This is not optional
polish — a 3D-only interface with no alternative is unusable for some users.

```html
<div id="viewer" role="img" aria-label="Interactive 3D model of the product, rotatable">
  <canvas></canvas>
</div>
```

- Provide keyboard controls, or a non-3D path to the same information.
- Respect `prefers-reduced-motion`: stop auto-rotation and camera drift.

```js
const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
controls.autoRotate = !still;
```

- Never trap focus in the canvas. Tab must escape.

## Framework integration

In React, Vue or Svelte the mistakes are always the same two: recreating the
renderer on re-render, and not disposing on unmount.

```js
useEffect(() => {
  const renderer = new THREE.WebGPURenderer();
  // ...
  return () => {
    renderer.setAnimationLoop(null);
    renderer.dispose();
    disposeScene(scene);
    container.removeChild(renderer.domElement);
  };
}, []);   // empty deps: create once
```

Keep three.js objects out of reactive state. Wrapping a `Vector3` in a
framework's reactivity proxy makes every `.set()` trigger a re-render and
destroys performance in a way that is very hard to trace.

`react-three-fiber` handles all of this and is the right choice in a React
app — but it lags core three.js by a release or two, so check its peer
dependency before assuming an r185 API is available.

## Server-side rendering

There is no `window` or `document` at build time. Import three.js dynamically
inside the mount effect, or the build fails with `ReferenceError: window is
not defined`.
