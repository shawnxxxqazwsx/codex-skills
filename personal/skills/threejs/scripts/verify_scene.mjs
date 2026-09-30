#!/usr/bin/env node
// Measure a three.js scene in a REAL, focused Chrome window over CDP.
//
// Why not headless / Playwright-headless: an unfocused or headless Chrome
// throttles requestAnimationFrame (often to ~1 fps) and `gl.finish()` does not
// synchronise, so every frame-rate number you get is fiction. This launches a
// visible window and reads the frame timings the page itself observed.
//
// No dependencies: uses node's built-in fetch and WebSocket (node >= 22).
//
// Usage:
//   node verify_scene.mjs --url http://127.0.0.1:8765/ [options]
//
// Options:
//   --url <url>          page to measure (required)
//   --seconds <n>        measurement window, default 6
//   --warmup <n>         seconds to ignore before measuring, default 3
//   --out <path>         screenshot path, default ./verify-<timestamp>.png
//   --json <path>        write the full report as JSON
//   --width/--height     window size, default 1280x800
//   --keep-open          leave the browser open when finished
//
// Exit code is 1 if the page logged errors or threw, 0 otherwise.

import { spawn } from 'node:child_process';
import { writeFile, mkdtemp, rm, access } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';

// ---------------------------------------------------------------- args

const argv = process.argv.slice(2);
const arg = (name, fallback) => {
  const i = argv.indexOf(`--${name}`);
  return i !== -1 && argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : fallback;
};
const flag = (name) => argv.includes(`--${name}`);

const URL_TO_TEST = arg('url');
const SECONDS = Number(arg('seconds', 6));
const WARMUP = Number(arg('warmup', 3));
const WIDTH = Number(arg('width', 1280));
const HEIGHT = Number(arg('height', 800));
const OUT_PNG = resolve(arg('out', `verify-${Date.now()}.png`));
const OUT_JSON = arg('json') ? resolve(arg('json')) : null;
const KEEP_OPEN = flag('keep-open');
const ORBIT = Number(arg('orbit', 1));

if (!URL_TO_TEST) {
  console.error('verify_scene: --url is required');
  process.exit(2);
}

// ---------------------------------------------------------------- chrome

const CHROME_CANDIDATES = [
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  process.env.LOCALAPPDATA && `${process.env.LOCALAPPDATA}/Google/Chrome/Application/chrome.exe`,
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
].filter(Boolean);

async function findChrome() {
  for (const p of CHROME_CANDIDATES) {
    try { await access(p); return p; } catch { /* keep looking */ }
  }
  throw new Error('No Chrome/Edge binary found. Pass one via CHROME_PATH.');
}

const DEBUG_PORT = 9222 + Math.floor(Math.random() * 700);

async function waitForDevtools(port, timeoutMs = 20000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const r = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (r.ok) return await r.json();
    } catch { /* not up yet */ }
    await new Promise((r) => setTimeout(r, 150));
  }
  throw new Error('Chrome DevTools endpoint did not come up');
}

async function findPageTarget(port, timeoutMs = 15000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const r = await fetch(`http://127.0.0.1:${port}/json/list`);
    const targets = await r.json();
    const page = targets.find((t) => t.type === 'page' && t.webSocketDebuggerUrl);
    if (page) return page;
    await new Promise((r) => setTimeout(r, 150));
  }
  throw new Error('No page target found');
}

// ---------------------------------------------------------------- cdp

class CDP {
  constructor(ws) {
    this.ws = ws;
    this.id = 0;
    this.pending = new Map();
    this.listeners = [];
    ws.addEventListener('message', (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.id !== undefined) {
        const p = this.pending.get(msg.id);
        if (p) {
          this.pending.delete(msg.id);
          msg.error ? p.reject(new Error(msg.error.message)) : p.resolve(msg.result);
        }
      } else {
        for (const fn of this.listeners) fn(msg);
      }
    });
  }

  static connect(url) {
    return new Promise((res, rej) => {
      const ws = new WebSocket(url);
      ws.addEventListener('open', () => res(new CDP(ws)));
      ws.addEventListener('error', () => rej(new Error(`CDP connect failed: ${url}`)));
    });
  }

  send(method, params = {}) {
    const id = ++this.id;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      setTimeout(() => {
        if (this.pending.has(id)) {
          this.pending.delete(id);
          reject(new Error(`CDP timeout: ${method}`));
        }
      }, 60000);
    });
  }

  on(fn) { this.listeners.push(fn); }
  close() { try { this.ws.close(); } catch { /* already gone */ } }

  // Not JavaScript's eval(): this is CDP `Runtime.evaluate`, which runs the
  // expression inside the page under test, in its own renderer process. The
  // only expressions passed here are the two constant probes defined below
  // in this file -- no caller input is ever interpolated into them.
  async eval(expression) {
    const r = await this.send('Runtime.evaluate', {
      expression,
      returnByValue: true,
      awaitPromise: true,
    });
    if (r.exceptionDetails) {
      throw new Error(r.exceptionDetails.exception?.description || 'evaluate threw');
    }
    return r.result.value;
  }
}

// ---------------------------------------------------------------- probe

// Installed BEFORE any page script runs (Page.addScriptToEvaluateOnNewDocument).
//
// It wraps requestAnimationFrame so we time the page's own callback. This is
// the metric that matters: on a vsync-capped display every scene reports 60
// fps right up until it falls off a cliff, so frame rate alone cannot tell a
// cheap scene from one that is one feature away from stuttering. Main-thread
// milliseconds per frame can, and it degrades linearly.
const INSTALL_PROBE = `
(() => {
  if (window.__probe) return 'already';
  const p = { frameDeltas: [], jsMs: [], running: true };
  window.__probe = p;

  // --- Descubrimiento automatico de la escena ---
  // three.js anuncia cada Scene y cada Renderer a __THREE_DEVTOOLS__ en su
  // constructor, si esa global existe. Instalandola ANTES de que cargue la
  // pagina, el arnes encuentra la escena de cualquier proyecto three.js sin
  // que el proyecto coopere en nada.
  //
  // La camara no se anuncia, asi que se captura envolviendo render(): es la
  // unica forma de saber cual de las camaras que existan es la que se usa.
  const found = { scenes: [], renderers: [], camera: null, controls: null };
  window.__harness = found;

  const devtools = new EventTarget();
  devtools.addEventListener('observe', (e) => {
    const o = e.detail;
    if (!o) return;

    if (o.isScene && !found.scenes.includes(o)) found.scenes.push(o);

    if ((o.isWebGLRenderer || o.isWebGPURenderer) && !found.renderers.includes(o)) {
      found.renderers.push(o);
      if (typeof o.render === 'function') {
        const original = o.render.bind(o);
        o.render = function (scene, camera) {
          // Solo se acepta una camara si viene con una escena que three.js
          // anuncio: los pases internos de post-proceso tambien llaman a
          // render() y dejarian aqui su camara de quad.
          if (camera && camera.isCamera && scene && found.scenes.includes(scene)) {
            found.camera = camera;
            found.activeScene = scene;
          }
          return original(scene, camera);
        };
      }
    }
  });
  window.__THREE_DEVTOOLS__ = devtools;

  const rawRaf = window.requestAnimationFrame.bind(window);
  let last = -1;

  window.requestAnimationFrame = function (cb) {
    return rawRaf(function (t) {
      const s = performance.now();
      cb(t);
      const e = performance.now();
      if (p.running) {
        p.jsMs.push(e - s);
        if (last >= 0) p.frameDeltas.push(t - last);
        last = t;
      }
    });
  };
  return 'installed';
})()
`;

// three.js resets renderer.info every render() call, and EffectComposer calls
// render() once per pass -- so reading info after composer.render() reports
// only the final fullscreen quad (1 draw call, 2 triangles). Disabling
// autoReset and sampling across one full frame gives the real scene cost.
const MEASURE_DRAW_COST = `
(async () => {

// Resuelve {scene, camera, renderer, controls} de tres formas, en orden:
//  1. window.__scene, si el proyecto coopera (gana siempre: es explicito)
//  2. lo capturado por el shim de __THREE_DEVTOOLS__ (cualquier proyecto)
//  3. convenciones sueltas (window.escena, window.app)
const __resolve = () => {
  const out = { scene: null, camera: null, renderer: null, controls: null, via: 'none' };
  for (const [root, via] of [[window.__scene, 'window.__scene'], [window.escena, 'window.escena'], [window.app, 'window.app']]) {
    if (root && (root.renderer || root.scene)) {
      out.scene = root.scene || null;
      out.camera = root.camera || null;
      out.renderer = root.renderer || null;
      out.controls = root.controls || null;
      out.via = via;
      break;
    }
  }
  const h = window.__harness;
  if (h) {
    if (!out.renderer && h.renderers.length) { out.renderer = h.renderers[0]; out.via = out.via === 'none' ? 'devtools-hook' : out.via; }
    if (!out.scene) out.scene = h.activeScene || h.scenes[0] || null;
    if (!out.camera) out.camera = h.camera || null;
  }
  if (!out.renderer && (window.renderer?.isWebGLRenderer || window.renderer?.isWebGPURenderer)) {
    out.renderer = window.renderer; out.via = 'window.renderer';
  }
  return out;
};

  const renderer = __resolve().renderer;
  if (!renderer || !renderer.info) return null;

  const info = renderer.info;
  const prevAuto = info.autoReset;
  info.autoReset = false;
  info.reset();

  await new Promise((res) => requestAnimationFrame(() => requestAnimationFrame(res)));

  // Only WebGLRenderer renders exactly once per rAF tick, which is what makes
  // "counters over two ticks / 2" a true per-frame figure. On the newer
  // Renderer path (WebGPURenderer + RenderPipeline) each pipeline.render()
  // fans out into many internal render() calls and the total does not track
  // scene content -- measured: 1k particles gave a HIGHER count than 200k.
  // Report it, but never compare it across the two paths.
  const reliable = renderer.isWebGLRenderer === true;

  const snap = {
    reliable,
    drawCalls: info.render.calls,
    triangles: info.render.triangles,
    points: info.render.points,
    lines: info.render.lines,
    geometries: info.memory.geometries,
    textures: info.memory.textures,
    programs: info.programs ? info.programs.length : null,
  };

  info.autoReset = prevAuto;
  info.reset();

  // Two rAF ticks were sampled; report per-frame cost.
  snap.drawCalls = Math.round(snap.drawCalls / 2);
  snap.triangles = Math.round(snap.triangles / 2);
  snap.points = Math.round(snap.points / 2);
  snap.lines = Math.round(snap.lines / 2);
  return snap;
})()
`;

// Scene-graph lint. These are the failures that produce a wrong image while
// reporting zero console errors and perfectly good frame times -- the ones a
// performance harness is blind to. Everything here is decided from the graph,
// so it is deterministic: no pixel comparison, no thresholds to tune.
const AUDIT_SCENE = `
(() => {

// Resuelve {scene, camera, renderer, controls} de tres formas, en orden:
//  1. window.__scene, si el proyecto coopera (gana siempre: es explicito)
//  2. lo capturado por el shim de __THREE_DEVTOOLS__ (cualquier proyecto)
//  3. convenciones sueltas (window.escena, window.app)
const __resolve = () => {
  const out = { scene: null, camera: null, renderer: null, controls: null, via: 'none' };
  for (const [root, via] of [[window.__scene, 'window.__scene'], [window.escena, 'window.escena'], [window.app, 'window.app']]) {
    if (root && (root.renderer || root.scene)) {
      out.scene = root.scene || null;
      out.camera = root.camera || null;
      out.renderer = root.renderer || null;
      out.controls = root.controls || null;
      out.via = via;
      break;
    }
  }
  const h = window.__harness;
  if (h) {
    if (!out.renderer && h.renderers.length) { out.renderer = h.renderers[0]; out.via = out.via === 'none' ? 'devtools-hook' : out.via; }
    if (!out.scene) out.scene = h.activeScene || h.scenes[0] || null;
    if (!out.camera) out.camera = h.camera || null;
  }
  if (!out.renderer && (window.renderer?.isWebGLRenderer || window.renderer?.isWebGPURenderer)) {
    out.renderer = window.renderer; out.via = 'window.renderer';
  }
  return out;
};

  const ctx = __resolve();
  if (!ctx.scene) return { available: false };

  const { scene, camera, renderer } = ctx;
  const findings = [];
  const add = (severity, rule, detail) => findings.push({ severity, rule, detail });

  const meshes = [];
  scene.traverse((o) => { if (o.isMesh || o.isSprite || o.isPoints || o.isLine) meshes.push(o); });
  const mats = (o) => Array.isArray(o.material) ? o.material : o.material ? [o.material] : [];

  // 1. Transparent draw-order ties. The exact failure the sea-over-ash bug was.
  const transparents = meshes.filter(o => mats(o).some(m => m.transparent));
  const noDepthWrite = transparents.filter(o => mats(o).some(m => m.transparent && m.depthWrite === false));
  if (noDepthWrite.length && transparents.length > 1) {
    const orders = new Set(transparents.map(o => o.renderOrder));
    if (orders.size === 1) {
      add('error', 'transparent-sort-tie',
        transparents.length + ' transparent objects share renderOrder ' + [...orders][0] +
        ' and ' + noDepthWrite.length + ' of them skip depthWrite (' +
        noDepthWrite.map(o => o.type + (o.name ? ':' + o.name : '')).join(', ') +
        '). Back-to-front sorting cannot resolve this: set renderOrder explicitly.');
    }
  }

  // 2. A huge dome inside exponential fog is a wall the colour of the fog.
  if (scene.fog) {
    for (const o of meshes) {
      const s = Math.max(o.scale.x, o.scale.y, o.scale.z);
      if (s > 1000 && mats(o).some(m => m.fog !== false)) {
        add('error', 'sky-inside-fog',
          (o.name || o.type) + ' is scaled to ' + Math.round(s) +
          ' with fog enabled. Set material.fog = false or it renders as solid fog.');
      }
    }
  }

  // 3. Colour-space tagging. Data maps must never be sRGB, colour maps must be.
  const DATA_MAPS = ['normalMap','roughnessMap','metalnessMap','aoMap','displacementMap','bumpMap','alphaMap'];
  const COLOUR_MAPS = ['map','emissiveMap','sheenColorMap','specularColorMap'];
  for (const o of meshes) {
    for (const m of mats(o)) {
      for (const k of DATA_MAPS) {
        if (m[k] && m[k].colorSpace === 'srgb') {
          add('error', 'data-map-tagged-srgb',
            (o.name || o.type) + '.' + k + ' is tagged sRGB. Data maps must be NoColorSpace.');
        }
      }
      for (const k of COLOUR_MAPS) {
        if (m[k] && m[k].colorSpace === '') {
          add('warn', 'colour-map-untagged',
            (o.name || o.type) + '.' + k + ' has no colorSpace. Colour maps need SRGBColorSpace.');
        }
      }
    }
  }

  // 4. Shadow frustum sanity.
  scene.traverse((o) => {
    if (!o.isDirectionalLight || !o.castShadow || !o.shadow) return;
    const c = o.shadow.camera;
    if (c.right !== undefined) {
      const w = c.right - c.left, h = c.top - c.bottom;
      if (w <= 0 || h <= 0) add('error', 'shadow-camera-degenerate', 'Directional light shadow camera has non-positive extent.');
      const texels = o.shadow.mapSize.x / Math.max(w, 1);
      if (texels < 2) add('warn', 'shadow-resolution-low',
        'Shadow map covers ' + Math.round(w) + ' units at ' + o.shadow.mapSize.x +
        'px (' + texels.toFixed(1) + ' texels/unit): shadows will look blocky.');
    }
  });

  // 5. Deprecated settings that degrade silently rather than failing.
  if (renderer) {
    // PCFSoftShadowMap (=2) solo degrada en el WebGLRenderer legacy: el warning
    // vive en WebGLShadowMap.js. En el camino de nodos (WebGPURenderer, en
    // cualquiera de sus dos backends) ShadowNode indexa _shadowFilterLib[type],
    // y el indice 2 es PCFSoftShadowFilter: es un tipo valido y suave de
    // verdad. Advertir aqui daba un falso positivo en toda escena WebGPU.
    if (renderer.shadowMap && renderer.shadowMap.enabled && renderer.shadowMap.type === 2
        && renderer.isWebGLRenderer === true && renderer.isWebGPURenderer !== true) {
      add('warn', 'deprecated-pcfsoft',
        'PCFSoftShadowMap silently downgrades to PCFShadowMap on the legacy WebGLRenderer. ' +
        'Use WebGPURenderer (where it is valid) or VSMShadowMap.');
    }
    if (renderer.getPixelRatio && renderer.getPixelRatio() > 2) {
      add('warn', 'pixel-ratio-high',
        'devicePixelRatio ' + renderer.getPixelRatio() + ' uncapped: fragment cost is quadratic. Cap at 2.');
    }
    if (renderer.isWebGLRenderer) {
      add('warn', 'legacy-renderer',
        'WebGLRenderer: WebGPURenderer falls back to WebGL2 on its own and unlocks compute and TSL post-processing.');
    }
  }

  // 6. Camera depth range.
  if (camera && camera.isPerspectiveCamera && camera.far / camera.near > 1e5) {
    add('warn', 'depth-range-wide',
      'far/near is ' + Math.round(camera.far / camera.near) + ' (>1e5): expect z-fighting. Raise near or shrink the world.');
  }

  // 7. Instanced/sprite batches culled by a bounding sphere that does not
  //    describe where the instances actually are.
  for (const o of meshes) {
    if ((o.isSprite && o.count > 1) || o.isInstancedMesh) {
      if (o.frustumCulled) {
        add('warn', 'batch-frustum-culled',
          (o.name || o.type) + ' has ' + (o.count || '?') + ' instances with frustumCulled on: ' +
          'the whole batch vanishes when its origin leaves view. Set frustumCulled = false.');
      }
    }
  }

  // 8. Broken transforms produce an empty frame with no error at all.
  scene.traverse((o) => {
    const p = o.position;
    if (!Number.isFinite(p.x + p.y + p.z)) add('error', 'non-finite-transform', (o.name || o.type) + ' has a NaN position.');
    if (o.scale.x === 0 || o.scale.y === 0 || o.scale.z === 0) add('warn', 'zero-scale', (o.name || o.type) + ' has a zero scale axis.');
  });

  return {
    available: true,
    via: ctx.via,
    objects: meshes.length,
    findings,
    errors: findings.filter(f => f.severity === 'error').length,
    warnings: findings.filter(f => f.severity === 'warn').length,
  };
})()
`;

const READ_RESULT = `
(() => {
  const p = window.__probe;
  p.running = false;


// Resuelve {scene, camera, renderer, controls} de tres formas, en orden:
//  1. window.__scene, si el proyecto coopera (gana siempre: es explicito)
//  2. lo capturado por el shim de __THREE_DEVTOOLS__ (cualquier proyecto)
//  3. convenciones sueltas (window.escena, window.app)
const __resolve = () => {
  const out = { scene: null, camera: null, renderer: null, controls: null, via: 'none' };
  for (const [root, via] of [[window.__scene, 'window.__scene'], [window.escena, 'window.escena'], [window.app, 'window.app']]) {
    if (root && (root.renderer || root.scene)) {
      out.scene = root.scene || null;
      out.camera = root.camera || null;
      out.renderer = root.renderer || null;
      out.controls = root.controls || null;
      out.via = via;
      break;
    }
  }
  const h = window.__harness;
  if (h) {
    if (!out.renderer && h.renderers.length) { out.renderer = h.renderers[0]; out.via = out.via === 'none' ? 'devtools-hook' : out.via; }
    if (!out.scene) out.scene = h.activeScene || h.scenes[0] || null;
    if (!out.camera) out.camera = h.camera || null;
  }
  if (!out.renderer && (window.renderer?.isWebGLRenderer || window.renderer?.isWebGPURenderer)) {
    out.renderer = window.renderer; out.via = 'window.renderer';
  }
  return out;
};

  const ctx = __resolve();
  const renderer = ctx.renderer;

  let backend = 'unknown';
  if (renderer) {
    if (renderer.isWebGPURenderer) {
      backend = renderer.backend && renderer.backend.isWebGPUBackend ? 'webgpu' : 'webgl2-fallback';
    } else if (renderer.isWebGLRenderer) {
      backend = 'webgl';
    }
  }

  const stats = (arr) => {
    const f = arr.filter(d => d > 0 && d < 2000).sort((a, b) => a - b);
    if (!f.length) return null;
    const pct = (q) => f[Math.min(f.length - 1, Math.floor(f.length * q))];
    return {
      n: f.length,
      mean: +(f.reduce((s, d) => s + d, 0) / f.length).toFixed(2),
      p50: +pct(0.5).toFixed(2),
      p95: +pct(0.95).toFixed(2),
      max: +f[f.length - 1].toFixed(2),
    };
  };

  // Drop the first 15%: shader compile and texture upload always spike there.
  const cut = (a) => a.slice(Math.floor(a.length * 0.15));
  const frame = stats(cut(p.frameDeltas));
  const js = stats(cut(p.jsMs));

  const canvas = document.querySelector('canvas');

  return {
    backend,
    rendererFound: !!renderer,
    discoveredVia: ctx.via,
    samples: frame ? frame.n : 0,
    fpsMean: frame ? +(1000 / frame.mean).toFixed(1) : null,
    fpsP50: frame ? +(1000 / frame.p50).toFixed(1) : null,
    frameMs: frame,
    // The number that actually discriminates once vsync caps frame rate.
    mainThreadMs: js,
    // How much of a 16.67 ms budget the page spends on its own JS.
    budgetUsedPct: js ? +((js.mean / 16.67) * 100).toFixed(1) : null,
    vsyncCapped: frame ? frame.mean < 17.5 && frame.mean > 15.8 : false,
    canvas: canvas ? { w: canvas.width, h: canvas.height } : null,
    jsHeapMB: performance.memory ? +(performance.memory.usedJSHeapSize / 1048576).toFixed(1) : null,
  };
})()
`;

// ---------------------------------------------------------------- run

let chromeProc = null;
let userDataDir = null;

async function main() {
  const chromePath = process.env.CHROME_PATH || (await findChrome());
  // A dedicated profile dir is mandatory: if Chrome is already running with
  // the default profile, a second process just delegates to it and our
  // --remote-debugging-port is silently ignored.
  userDataDir = await mkdtemp(join(tmpdir(), 'verify-scene-'));

  chromeProc = spawn(chromePath, [
    `--remote-debugging-port=${DEBUG_PORT}`,
    `--user-data-dir=${userDataDir}`,
    `--window-size=${WIDTH},${HEIGHT}`,
    '--new-window',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',
    '--disable-background-timer-throttling',
    '--enable-unsafe-webgpu',
    '--autoplay-policy=no-user-gesture-required',
    URL_TO_TEST,
  ], { detached: false, stdio: 'ignore' });

  await waitForDevtools(DEBUG_PORT);
  const target = await findPageTarget(DEBUG_PORT);
  const cdp = await CDP.connect(target.webSocketDebuggerUrl);

  const consoleErrors = [];
  const consoleWarnings = [];
  const exceptions = [];
  const failedRequests = [];

  cdp.on((msg) => {
    if (msg.method === 'Runtime.consoleAPICalled') {
      const text = (msg.params.args || [])
        .map((a) => a.value ?? a.description ?? a.unserializableValue ?? '')
        .join(' ').trim();
      if (!text) return;
      if (msg.params.type === 'error') consoleErrors.push(text);
      else if (msg.params.type === 'warning') consoleWarnings.push(text);
    } else if (msg.method === 'Runtime.exceptionThrown') {
      const d = msg.params.exceptionDetails;
      exceptions.push(d.exception?.description || d.text || 'unknown exception');
    } else if (msg.method === 'Log.entryAdded') {
      const e = msg.params.entry;
      if (e.level === 'error') consoleErrors.push(`[${e.source}] ${e.text}`);
    } else if (msg.method === 'Network.loadingFailed') {
      failedRequests.push(msg.params.errorText);
    }
  });

  await cdp.send('Runtime.enable');
  await cdp.send('Log.enable');
  await cdp.send('Page.enable');
  await cdp.send('Network.enable');

  // --width/--height describen el VIEWPORT, no la ventana. Sin esto, la barra
  // del navegador se come ~160 px de alto y las capturas no son reproducibles
  // entre equipos ni entre ejecuciones.
  await cdp.send('Emulation.setDeviceMetricsOverride', {
    width: WIDTH,
    height: HEIGHT,
    deviceScaleFactor: 1,
    mobile: false,
  });

  // The rAF wrapper must exist before the page's own script installs its loop,
  // otherwise we only time frames it schedules after we attach.
  await cdp.send('Page.addScriptToEvaluateOnNewDocument', { source: INSTALL_PROBE });

  // The page may already be loaded by the time we attach; reload so we
  // capture every console message from the very first frame.
  await cdp.send('Page.reload', { ignoreCache: true });
  await new Promise((r) => setTimeout(r, 1200));

  console.log(`warming up ${WARMUP}s...`);
  await new Promise((r) => setTimeout(r, WARMUP * 1000));

  // Restart sampling now that warmup is over.
  await cdp.eval(`(() => { const p = window.__probe; if (p) { p.frameDeltas.length = 0; p.jsMs.length = 0; p.running = true; } return !!p; })()`);

  console.log(`measuring ${SECONDS}s...`);
  await new Promise((r) => setTimeout(r, SECONDS * 1000));

  const metrics = await cdp.eval(READ_RESULT);
  const drawCost = await cdp.eval(MEASURE_DRAW_COST);

  // --eval "<expression>" runs an inspection expression in the live page and
  // prints the result. This is a local development harness driving a page you
  // control; the expression comes from the developer's own command line.
  let inspected;
  const probeExpr = arg('eval');
  if (probeExpr) {
    try {
      // Promise.resolve(...) para que una expresion async funcione: sin esto
      // JSON.stringify recibe la promesa sin resolver y devuelve "{}".
      inspected = await cdp.eval(
        `Promise.resolve((() => (${probeExpr}))()).then(v => JSON.stringify(v))`
      );
      console.log('\n  eval →', inspected);
    } catch (e) {
      console.log('\n  eval failed:', e.message);
    }
  }

  const audit = await cdp.eval(AUDIT_SCENE);

  const shot = await cdp.send('Page.captureScreenshot', { format: 'png' });
  await writeFile(OUT_PNG, Buffer.from(shot.data, 'base64'));

  // Draw-order and culling faults are angle-dependent: a single head-on frame
  // is exactly the view most likely to look fine. Orbit and capture again.
  const extraShots = [];
  if (ORBIT > 1) {
    for (let i = 1; i < ORBIT; i++) {
      const az = (i / ORBIT) * Math.PI * 2;
      const moved = await cdp.eval(`
        (() => {
          const c = (window.__scene || window.escena || window.app);
          if (!c || !c.camera) return false;
          const cam = c.camera, t = (c.controls && c.controls.target) || { x: 0, y: 0, z: 0 };
          const dx = cam.position.x - t.x, dz = cam.position.z - t.z;
          const r = Math.hypot(dx, dz), a = Math.atan2(dz, dx) + ${az};
          cam.position.x = t.x + Math.cos(a) * r;
          cam.position.z = t.z + Math.sin(a) * r;
          cam.lookAt(t.x, t.y, t.z);
          if (c.controls && c.controls.update) c.controls.update();
          return true;
        })()
      `);
      if (!moved) break;
      await new Promise((r) => setTimeout(r, 700));
      const s = await cdp.send('Page.captureScreenshot', { format: 'png' });
      const p = OUT_PNG.replace(/\.png$/, `-a${i}.png`);
      await writeFile(p, Buffer.from(s.data, 'base64'));
      extraShots.push(p);
    }
  }

  // A missing favicon is not a scene defect and would fail every run.
  const realErrors = consoleErrors.filter((e) => !/favicon/i.test(e));

  const report = {
    url: URL_TO_TEST,
    measuredFor: SECONDS,
    ...metrics,
    draw: drawCost,
    audit,
    consoleErrors: realErrors,
    consoleWarnings: consoleWarnings.slice(0, 20),
    exceptions,
    failedRequests: failedRequests.filter((e) => !/favicon/i.test(e)),
    screenshot: OUT_PNG,
    screenshotsExtra: extraShots,
    // A scene-graph error means a wrong image, even when nothing threw.
    ok: realErrors.length === 0 && exceptions.length === 0 && (audit?.errors ?? 0) === 0,
  };

  if (OUT_JSON) await writeFile(OUT_JSON, JSON.stringify(report, null, 2), 'utf-8');

  const f = report.frameMs, j = report.mainThreadMs, d = report.draw;
  console.log('');
  console.log(`  backend      ${report.backend}${report.rendererFound ? '' : '  (renderer not exposed on window)'}`);
  console.log(`  fps          mean ${report.fpsMean}  p50 ${report.fpsP50}${report.vsyncCapped ? '   [vsync-capped: read main-thread instead]' : ''}`);
  console.log(`  frame ms     mean ${f?.mean}  p95 ${f?.p95}  max ${f?.max}`);
  console.log(`  main-thread  mean ${j?.mean} ms  p95 ${j?.p95} ms  max ${j?.max} ms   (${report.budgetUsedPct}% of a 60 Hz budget)`);
  if (d) {
    const caveat = d.reliable ? '' : '   [approximate: RenderPipeline fans out internally, do not compare across renderers]';
    console.log(`  draw calls   ${d.drawCalls}   triangles ${d.triangles}   points ${d.points}${caveat}`);
    console.log(`  geometries   ${d.geometries}   textures ${d.textures}   programs ${d.programs}`);
  } else {
    console.log(`  draw calls   unavailable (expose the renderer as window.__scene = { renderer })`);
  }
  console.log(`  js heap      ${report.jsHeapMB} MB`);
  console.log(`  errors       ${realErrors.length}   exceptions ${exceptions.length}`);
  for (const e of [...exceptions, ...realErrors].slice(0, 8)) console.log(`     ! ${e.slice(0, 160)}`);

  if (audit?.available) {
    console.log(`  scene audit  ${audit.objects} drawables · ${audit.errors} errors · ${audit.warnings} warnings`);
    for (const f of audit.findings) {
      console.log(`     ${f.severity === 'error' ? '!' : '·'} [${f.rule}] ${f.detail}`);
    }
  } else {
    console.log(`  scene audit  unavailable (expose window.__scene = { scene, camera, renderer, controls })`);
  }

  console.log(`  screenshot   ${OUT_PNG}`);
  for (const p of extraShots) console.log(`               ${p}`);
  console.log('');

  cdp.close();
  return report.ok ? 0 : 1;
}

async function cleanup() {
  if (!KEEP_OPEN && chromeProc && !chromeProc.killed) {
    try { chromeProc.kill(); } catch { /* already exited */ }
  }
  if (!KEEP_OPEN && userDataDir) {
    await new Promise((r) => setTimeout(r, 500));
    try { await rm(userDataDir, { recursive: true, force: true }); } catch { /* locked, leave it */ }
  }
}

main()
  .then(async (code) => { await cleanup(); process.exit(code); })
  .catch(async (err) => {
    console.error(`verify_scene failed: ${err.message}`);
    await cleanup();
    process.exit(2);
  });
