# Escena de la cabecera

La imagen `../header.png` no es una ilustración: la genera esta escena, y las
cifras de su pie son las que midió `verify_scene.mjs` en esa misma ejecución.

Está construida aplicando la skill que documenta: `WebGPURenderer` con respaldo
WebGL2, `Timer`, `setAnimationLoop`, una sola `InstancedMesh` para las 1.196
columnas, motas en compute TSL, `RenderPipeline` con bloom por nodos, y
`renderOrder` explícito en lo transparente.

## Regenerarla

```bash
S=../../scripts
node $S/serve.mjs --root ../../.. --port 8801

# 1) medir
node $S/verify_scene.mjs --url http://127.0.0.1:8801/skill/assets/header-scene/ \
     --width 1280 --height 400 --json /tmp/h.json --out /tmp/h1.png

# 2) rotular con lo medido y capturar
node $S/verify_scene.mjs --url http://127.0.0.1:8801/skill/assets/header-scene/ \
     --width 1280 --height 400 --out ../header.png \
     --eval "(() => { /* volcar /tmp/h.json en los #m-* */ })()"
```

`--width` y `--height` describen el viewport, no la ventana, así que la captura
es reproducible.

## Imagen para redes

`../social-preview.png` es la misma escena capturada a **1280x640**, que es el
formato que consumen las tarjetas Open Graph. La cabecera de 1280x400 no sirve
para eso: LinkedIn y X encajan a ~1.91:1 y recortarian el pie de metricas.

Se sube a mano en el repo: Settings -> General -> Social preview. GitHub no
expone endpoint de API para esa imagen, asi que no se puede automatizar.

```bash
node tools/skill.mjs verify_scene --url "http://127.0.0.1:8766/assets/header-scene/"   --width 1280 --height 640 --orbit 0 --out assets/social-preview.png   --json verify/social.json --eval "(() => { /* rotular los #m-* */ })()"
```
