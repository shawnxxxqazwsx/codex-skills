# Procedural geometry

## Choosing how to draw many things

This decision costs more performance than any other in three.js.

| Situation | Use | Draw calls |
|---|---|---|
| Same geometry, same material, thousands of copies | `InstancedMesh` | 1 |
| Different geometries, same material, per-object culling | `BatchedMesh` | 1 |
| Points/sprites driven by a simulation | compute + `SpriteNodeMaterial` | 1 |
| A handful of distinct objects | plain `Mesh` | 1 each |
| Static scenery that never moves separately | merge into one geometry | 1 |

A thousand `Mesh` objects is a thousand draw calls and will not hold 60 Hz.
The same thousand as one `InstancedMesh` is one.

### InstancedMesh

```js
const mesh = new THREE.InstancedMesh(geometry, material, COUNT);
const m = new THREE.Matrix4();
for (let i = 0; i < COUNT; i++) {
  m.compose(position, quaternion, scale);
  mesh.setMatrixAt(i, m);
  mesh.setColorAt(i, colour);
}
mesh.instanceMatrix.needsUpdate = true;
```

Set `mesh.frustumCulled = false` if instances are spread wider than the source
geometry's bounding box, or the whole batch disappears when the origin leaves
view. This is almost always the case: the bounding box comes from the source
geometry — one 15 mm key, one 6 mm leaf — not from where you put the instances.

**Different shapes do not always mean `BatchedMesh`.** If the difference is an
anisotropic scale, `InstancedMesh` already covers it: `compose()` takes a
per-instance scale, so one rounded-box geometry plus a scale on X gives a full
keyboard — 93 keys with real 1u / 1.5u / 2.25u / 6.25u widths, one draw call, one
geometry:

```js
// geometry is 0.88 u wide; a k-unit key must span k u minus the 0.12 u gap
scale.set((k.w - 0.12) / 0.88, 1, 1);
m.compose(pos, quat, scale);
mesh.setMatrixAt(i, m);
```

Reach for `BatchedMesh` when the *topology* differs (rocks, props, LOD swaps),
not when a stretch would do. Watch out for what stretching does to a bevel or
rounded corner: it stretches too. At key sizes nobody sees it; on a 6× stretch
they will.

### BatchedMesh

`BatchedMesh` (r166+) is what you want when the shapes differ. One draw call,
but each instance keeps its own geometry, transform and culling:

```js
const batch = new THREE.BatchedMesh(maxInstances, maxVertices, maxIndices, material);
const rockId = batch.addGeometry(rockGeo);
const id = batch.addInstance(rockId);
batch.setMatrixAt(id, matrix);
```

Unlike `InstancedMesh` it culls per instance and supports per-instance
visibility — better for scattered scenery.

## Building geometry by hand

```js
const geo = new THREE.BufferGeometry();
geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
geo.setAttribute('normal',   new THREE.BufferAttribute(normals, 3));
geo.setAttribute('uv',       new THREE.BufferAttribute(uvs, 2));
geo.setIndex(new THREE.BufferAttribute(indices, 1));
geo.computeVertexNormals();      // only if you did not author normals
geo.computeBoundingSphere();     // needed for correct culling
```

Index your geometry. An indexed cube is 8 vertices; unindexed it is 36. The
saving compounds with every attribute.

`computeVertexNormals()` averages across shared vertices, which is what you
want for smooth surfaces and wrong for hard edges — split vertices at the
edges you want faceted, or use `flatShading`.

## Displacing on the GPU

If a shape is a mathematical function of position, do not bake it into
vertices — compute it in `positionNode`. The geometry stays a plain plane and
the CPU does nothing per frame:

```js
material.positionNode = positionLocal.add(vec3(0, heightFn(positionLocal.xz), 0));
```

The catch: displacement in the shader does **not** update normals, so lighting
stays flat. Either derive normals analytically (sample the height function at
two nearby offsets and cross the tangents) or keep displacement subtle.

## Extrusion, lathe, CSG

`ExtrudeGeometry` handles profiles, bevels and holes:

```js
const shape = new THREE.Shape();
shape.moveTo(0, 0); shape.lineTo(2, 0); shape.lineTo(2, 1);
shape.holes.push(hole);
const geo = new THREE.ExtrudeGeometry(shape, { depth: 0.4, bevelEnabled: true, bevelSize: 0.05 });
```

For radial arrangements of extruded pieces the rotation is `rotation.y = -a`
where `a` is the angle. Adding 90° "to make it line up" is a sign the profile
is authored in the wrong plane; fix the profile.

`LatheGeometry` for anything turned on an axis — bottles, nozzles, columns.
Cheaper and cleaner than extrusion for those.

Boolean operations are not in core. `three-bvh-csg` is the current option;
budget for it being slow enough that it belongs at build time, not runtime.

## Level of detail

```js
const lod = new THREE.LOD();
lod.addLevel(highMesh, 0);
lod.addLevel(medMesh, 50);
lod.addLevel(lowMesh, 200);
```

`LOD` swaps by distance automatically during render. The swap is a hard cut —
if it pops, the levels differ too much; add an intermediate one.

For terrain and large surfaces, cross-fade tiles by opacity instead. Remember
that transparent tiles that skip depth writes are drawn in insertion order:
**add the most detailed one last**.

## Attributes for shaders

Custom per-vertex or per-instance data reaches TSL through `attribute()`:

```js
geo.setAttribute('aWind', new THREE.BufferAttribute(windStrength, 1));
// in TSL:
const wind = attribute('aWind', 'float');
material.positionNode = positionLocal.add(vec3(wind.mul(sway), 0, 0));
```

`InstancedBufferAttribute` does the same per instance. This is how you vary
thousands of instances without thousands of uniforms.

## Memory

Geometry is not freed automatically:

```js
geometry.dispose();
material.dispose();
texture.dispose();
```

Rebuilding a geometry every frame — even a small one — allocates a new GPU
buffer every frame. If a shape animates, animate it in the shader or mutate
the existing attribute with `needsUpdate = true`; never allocate a replacement.

Watch `renderer.info.memory.geometries`. Static scene, climbing number, means
a leak.
