#!/usr/bin/env node
// Static dev server with caching disabled.
//
// Why not `python -m http.server` or any default static server: they send
// cache headers (or none, which lets the browser heuristically cache), so
// after you edit an ES module the browser keeps serving the old one. That
// failure mode looks exactly like "my fix did not work" and costs hours.
//
// Usage: node serve.mjs [--port 8765] [--root .]

import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { join, extname, resolve, normalize, sep } from 'node:path';

const args = process.argv.slice(2);
const getArg = (name, fallback) => {
  const i = args.indexOf(`--${name}`);
  return i !== -1 && args[i + 1] ? args[i + 1] : fallback;
};

const PORT = Number(getArg('port', 8765));
const ROOT = resolve(getArg('root', process.cwd()));

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.wasm': 'application/wasm',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml',
  '.ktx2': 'image/ktx2',
  '.basis': 'application/octet-stream',
  '.glb': 'model/gltf-binary',
  '.gltf': 'model/gltf+json',
  '.bin': 'application/octet-stream',
  '.hdr': 'image/vnd.radiance',
  '.exr': 'image/x-exr',
  '.mp3': 'audio/mpeg',
  '.ogg': 'audio/ogg',
  '.ttf': 'font/ttf',
  '.woff2': 'font/woff2',
};

const server = createServer(async (req, res) => {
  try {
    const url = new URL(req.url, `http://${req.headers.host}`);
    let pathname = decodeURIComponent(url.pathname);
    if (pathname.endsWith('/')) pathname += 'index.html';

    // Block path traversal: resolve, then confirm the result is under ROOT.
    const target = resolve(join(ROOT, normalize(pathname)));
    if (target !== ROOT && !target.startsWith(ROOT + sep)) {
      res.writeHead(403).end('Forbidden');
      return;
    }

    const info = await stat(target);
    if (info.isDirectory()) {
      res.writeHead(302, { Location: pathname + '/' }).end();
      return;
    }

    const body = await readFile(target);
    res.writeHead(200, {
      'Content-Type': MIME[extname(target).toLowerCase()] || 'application/octet-stream',
      // The whole point of this server:
      'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
      'Pragma': 'no-cache',
      'Expires': '0',
      // Required for SharedArrayBuffer / multithreaded WASM decoders.
      'Cross-Origin-Opener-Policy': 'same-origin',
      'Cross-Origin-Embedder-Policy': 'require-corp',
      'Cross-Origin-Resource-Policy': 'cross-origin',
    });
    res.end(body);
  } catch (err) {
    const code = err.code === 'ENOENT' ? 404 : 500;
    res.writeHead(code, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end(code === 404 ? 'Not found' : `Server error: ${err.message}`);
  }
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`serving ${ROOT}`);
  console.log(`http://127.0.0.1:${PORT}/  (no-store)`);
});
