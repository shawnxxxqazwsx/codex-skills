#!/usr/bin/env node
// Create a runnable r185 scene in any project, with no build step.
//
// The point is the importmap: it must resolve `three` to a real file from
// wherever the new scene lives. Hardcoding "../../node_modules" only works at
// one depth, and a wrong importmap fails as a bare-specifier error that says
// nothing useful. This walks up to find the package and writes the correct
// relative path -- or falls back to a CDN when there is no install.
//
// Usage:
//   node new_scene.mjs --dir scenes/my-scene [--title "My scene"] [--cdn]
//
// Then:
//   node serve.mjs --root . --port 8765
//   node verify_scene.mjs --url http://127.0.0.1:8765/scenes/my-scene/ --orbit 3

import { mkdir, writeFile, access, readFile } from 'node:fs/promises';
import { join, resolve, relative, dirname, sep } from 'node:path';

const argv = process.argv.slice(2);
const arg = (n, d) => {
  const i = argv.indexOf(`--${n}`);
  return i !== -1 && argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : d;
};
const flag = (n) => argv.includes(`--${n}`);

const DIR = resolve(arg('dir', 'scene'));
const TITLE = arg('title', 'three.js r185 scene');
const FORCE_CDN = flag('cdn');
const CDN = 'https://unpkg.com/three@0.185.1';

const exists = async (p) => { try { await access(p); return true; } catch { return false; } };

/** Walk up from `from` looking for an installed three. */
async function findThree(from) {
  let dir = from;
  for (let i = 0; i < 8; i++) {
    const candidate = join(dir, 'node_modules', 'three');
    if (await exists(join(candidate, 'build', 'three.webgpu.js'))) {
      let version = 'unknown';
      try {
        version = JSON.parse(await readFile(join(candidate, 'package.json'), 'utf-8')).version;
      } catch { /* keep unknown */ }
      return { path: candidate, version };
    }
    const up = dirname(dir);
    if (up === dir) break;
    dir = up;
  }
  return null;
}

/** Web-safe relative path from the scene folder to the package. */
function webRelative(fromDir, toPath) {
  const r = relative(fromDir, toPath).split(sep).join('/');
  return r.startsWith('.') ? r : `./${r}`;
}

const html = (title, imports) => `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title>
<link rel="icon" href="data:,">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { height: 100%; overflow: hidden; }
  body { background: #0b0d10; font-family: ui-sans-serif, system-ui, sans-serif; color: #e8eaee; }
  canvas { display: block; touch-action: none; }
  #hud {
    position: fixed; top: 16px; left: 18px; font-size: 12px; line-height: 1.6;
    color: #9aa4b4; pointer-events: none; text-shadow: 0 1px 3px #000;
  }
</style>
</head>
<body>
<div id="hud">…</div>

<!-- Bare "three" points at the webgpu build on purpose: addons import from
     'three' internally, and two different builds mean two class identities,
     with instanceof returning false and errors that make no sense. -->
<script type="importmap">
{
  "imports": {
    "three":         "${imports.three}",
    "three/webgpu":  "${imports.three}",
    "three/tsl":     "${imports.tsl}",
    "three/addons/": "${imports.addons}"
  }
}
</script>

<script type="module" src="./main.js"></script>
</body>
</html>
`;

const mainJs = `// ${TITLE}
// three.js r185 · WebGPU with automatic WebGL2 fallback.
// Scale: decide it now and write it here. 1 unit = 1 metre unless stated.

import * as THREE from 'three/webgpu';           // Timer ships in core
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { mix, color, screenUV } from 'three/tsl';

const renderer = new THREE.WebGPURenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));   // cap: cost is quadratic
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
document.body.appendChild(renderer.domElement);

// Not always required (setAnimationLoop initialises too), but it is what makes
// the whole *Async() family unnecessary.
await renderer.init();

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 500);
camera.position.set(0, 2.5, 7);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// A metal with no environment reflects nothing and renders black.
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

// Background as a node: no geometry, no texture.
scene.backgroundNode = mix(color(0x0a1220), color(0x243b55), screenUV.y);

scene.add(new THREE.HemisphereLight(0xbcd8ff, 0x101820, 1.0));
const key = new THREE.DirectionalLight(0xffffff, 2.2);
key.position.set(4, 6, 3);
scene.add(key);

// --- your scene ---------------------------------------------------------
const material = new THREE.MeshStandardNodeMaterial({ roughness: 0.3, metalness: 0.5 });
const mesh = new THREE.Mesh(new THREE.TorusKnotGeometry(1.2, 0.36, 200, 32), material);
scene.add(mesh);
// ------------------------------------------------------------------------

const timer = new THREE.Timer();     // Clock is deprecated since r183

renderer.setAnimationLoop((timestamp) => {
  timer.update(timestamp);                       // Timer needs this; Clock did not
  const dt = Math.min(timer.getDelta(), 1 / 30); // a hidden tab returns a huge delta

  mesh.rotation.y += dt * 0.4;                   // dt-scaled, never per-frame constant

  controls.update();
  renderer.render(scene, camera);
});

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();               // forgetting this stretches the image
  renderer.setSize(innerWidth, innerHeight);
});

document.getElementById('hud').textContent =
  \`three.js r185 · \${renderer.backend?.isWebGPUBackend ? 'WebGPU' : 'WebGL2 (fallback)'}\`;

// Optional: verify_scene.mjs discovers the scene on its own via the devtools
// hook, but exposing it explicitly is more reliable and costs one line.
window.__scene = { scene, camera, renderer, controls };
`;

const found = FORCE_CDN ? null : await findThree(DIR);

const imports = found
  ? {
      three: webRelative(DIR, join(found.path, 'build/three.webgpu.js')),
      tsl: webRelative(DIR, join(found.path, 'build/three.tsl.js')),
      addons: webRelative(DIR, join(found.path, 'examples/jsm')) + '/',
    }
  : {
      three: `${CDN}/build/three.webgpu.js`,
      tsl: `${CDN}/build/three.tsl.js`,
      addons: `${CDN}/examples/jsm/`,
    };

await mkdir(DIR, { recursive: true });
await writeFile(join(DIR, 'index.html'), html(TITLE, imports), 'utf-8');
await writeFile(join(DIR, 'main.js'), mainJs, 'utf-8');

console.log(`scene created at ${DIR}`);
if (found) {
  console.log(`three ${found.version} found at ${found.path}`);
  if (!found.version.startsWith('0.185')) {
    console.log(`  NOTE: this skill documents r185; installed is ${found.version}.`);
    console.log(`  Verify any API you are unsure about against node_modules/three/src/.`);
  }
} else {
  console.log(`no local three found -> importmap points at the CDN (${CDN})`);
  console.log(`  for offline work: npm install three@0.185.1, then re-run this script`);
}
console.log('');
console.log('  node serve.mjs --root . --port 8765');
console.log(`  node verify_scene.mjs --url http://127.0.0.1:8765/... --orbit 3`);
