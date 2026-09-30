// Escena de la cabecera del repositorio.
//
// Se construye aplicando la propia skill, porque la imagen tiene que ser una
// demostracion y no una decoracion: instancing, materiales PBR con entorno,
// altura por ruido TSL, particulas en compute y post-proceso por nodos.
//
// Escala: 1 unidad = 1 metro.

import * as THREE from 'three/webgpu';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { bloom } from 'three/addons/tsl/display/BloomNode.js';
import {
  Fn, uniform, float, vec3, color, mix, pass, screenUV,
  instancedArray, instanceIndex, hash, positionLocal,
} from 'three/tsl';

const renderer = new THREE.WebGPURenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.92;
document.body.appendChild(renderer.domElement);

await renderer.init();

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x05070c, 0.021);

const camera = new THREE.PerspectiveCamera(34, innerWidth / innerHeight, 0.5, 400);
camera.position.set(15.5, 8.2, 25);
camera.lookAt(0, 1.2, 0);

// Un metal sin entorno se ve negro: esto no es adorno, es requisito.
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.03).texture;
scene.environmentIntensity = 0.62;

scene.backgroundNode = mix(color(0x04060b), color(0x111d33), screenUV.y.oneMinus().pow(1.6));

const key = new THREE.DirectionalLight(0xdfeaff, 2.4);
key.position.set(12, 18, 14);
scene.add(key);

const warm = new THREE.DirectionalLight(0xffb27a, 1.5);
warm.position.set(-18, 6, -10);
scene.add(warm);

scene.add(new THREE.HemisphereLight(0x9fc4ff, 0x0a0f18, 0.5));

// ---------------------------------------------------------------
// Reticula de pilares: una sola InstancedMesh, un solo draw call.
// La altura y el color salen de un nodo TSL, asi que la onda se calcula
// en la GPU y el hilo principal no toca nada por fotograma.
// ---------------------------------------------------------------
const COLS = 46, ROWS = 26, PITCH = 0.62;

const pillarGeo = new THREE.BoxGeometry(0.34, 1, 0.34);
pillarGeo.translate(0, 0.5, 0);            // pivote en la base: escalar crece hacia arriba

const pillarMat = new THREE.MeshStandardNodeMaterial({ metalness: 0.94, roughness: 0.24 });

// Color por altura: azul frio en los valles, ambar en las crestas.
// positionLocal.y va de 0 a 1 dentro del pilar, y la escala de la instancia
// hace el resto: un solo material sirve para las 1.196 columnas.
pillarMat.colorNode = mix(color(0x24405e), color(0xffc98a), positionLocal.y.mul(0.55).clamp(0, 1));
pillarMat.emissiveNode = color(0xff9a4a).mul(positionLocal.y.sub(0.72).max(0).mul(0.9));

const pillars = new THREE.InstancedMesh(pillarGeo, pillarMat, COLS * ROWS);
pillars.frustumCulled = false;             // el batch entero desaparece si se culea

const m4 = new THREE.Matrix4();
const pos = new THREE.Vector3();
const quat = new THREE.Quaternion();
const scl = new THREE.Vector3();
const heights = new Float32Array(COLS * ROWS);

let i = 0;
for (let x = 0; x < COLS; x++) {
  for (let z = 0; z < ROWS; z++) {
    const wx = (x - COLS / 2) * PITCH;
    const wz = (z - ROWS / 2) * PITCH;
    heights[i] = Math.hypot(wx, wz);
    pos.set(wx, 0, wz);
    scl.set(1, 0.2, 1);
    pillars.setMatrixAt(i, m4.compose(pos, quat, scl));
    i++;
  }
}
pillars.instanceMatrix.needsUpdate = true;
scene.add(pillars);

// Suelo especular que recoge el reflejo del entorno.
const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(120, 120),
  new THREE.MeshStandardNodeMaterial({ color: 0x080c14, metalness: 0.85, roughness: 0.28 })
);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -0.02;
scene.add(floor);

// ---------------------------------------------------------------
// Motas en suspension: compute puro, el bucle de JS no las toca.
// ---------------------------------------------------------------
const MOTES = 24000;
const mp = instancedArray(MOTES, 'vec3');
const uDelta = uniform(0);

const initMotes = Fn(() => {
  const p = mp.element(instanceIndex);
  p.assign(vec3(
    hash(instanceIndex).sub(0.5).mul(34),
    hash(instanceIndex.add(1)).mul(11).add(0.4),
    hash(instanceIndex.add(2)).sub(0.5).mul(22)
  ));
})().compute(MOTES).setName('motes-init');

const updateMotes = Fn(() => {
  const p = mp.element(instanceIndex);
  p.y.addAssign(uDelta.mul(hash(instanceIndex.add(7)).mul(0.32).add(0.06)));
  p.x.addAssign(uDelta.mul(0.14));
  // Reciclado por altura, sin condicionales caros.
  p.y.assign(p.y.mod(11.6).add(0.2));
})().compute(MOTES).setName('motes-update');

const moteMat = new THREE.SpriteNodeMaterial({ transparent: true, depthWrite: false });
moteMat.blending = THREE.AdditiveBlending;
moteMat.positionNode = mp.toAttribute();
moteMat.scaleNode = float(0.035);
moteMat.colorNode = color(0x9ecbff);
moteMat.opacityNode = float(0.5);

const motes = new THREE.Sprite(moteMat);
motes.count = MOTES;
motes.frustumCulled = false;
motes.renderOrder = 10;        // transparente: orden explicito frente al suelo
scene.add(motes);

renderer.compute(initMotes);

// ---------------------------------------------------------------
// Post-proceso por nodos (RenderPipeline, no el composer heredado)
// ---------------------------------------------------------------
const pipeline = new THREE.RenderPipeline(renderer);
const scenePass = pass(scene, camera);
const sceneColor = scenePass.getTextureNode();
// Umbral alto: por debajo de ~0.9 el lobulo especular del suelo se convierte
// en una mancha que se come la rotulacion.
pipeline.outputNode = sceneColor.add(bloom(sceneColor, 0.3, 0.5, 0.93));

// ---------------------------------------------------------------
// Bucle
// ---------------------------------------------------------------
const timer = new THREE.Timer();

renderer.setAnimationLoop((timestamp) => {
  timer.update(timestamp);
  const dt = Math.min(timer.getDelta(), 1 / 30);
  const t = timer.getElapsed();
  uDelta.value = dt;

  // La onda se aplica a la escala de cada instancia. Es trabajo de CPU, pero
  // son 1.196 matrices: cabe de sobra y mantiene el ejemplo legible.
  for (let k = 0; k < heights.length; k++) {
    const r = heights[k];
    const a = Math.sin(r * 0.42 - t * 1.15) * 0.5 + 0.5;
    const b = Math.sin((k % COLS) * 0.3 + t * 0.55) * 0.5 + 0.5;
    const hh = (a * 0.72 + b * 0.28) * 3.4 + 0.18;
    pillars.getMatrixAt(k, m4);
    m4.decompose(pos, quat, scl);
    scl.set(1, hh, 1);
    pillars.setMatrixAt(k, m4.compose(pos, quat, scl));
  }
  pillars.instanceMatrix.needsUpdate = true;

  renderer.compute(updateMotes);
  pipeline.render();
});

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  pipeline.setSize?.(innerWidth, innerHeight);
});

window.__scene = { scene, camera, renderer, pipeline };
