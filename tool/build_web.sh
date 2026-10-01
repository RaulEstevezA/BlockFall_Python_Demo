#!/usr/bin/env bash
# Compila el juego para el navegador con pygbag (pygame → WebAssembly).
#
# pygbag empaqueta todo el contenido de la carpeta que recibe, así que primero
# se copian solo los archivos del juego a build/blockfall/ y se compila desde ahí.
# Resultado: build/blockfall/build/web/ (index.html + blockfall.apk)
#
# Uso:  ./tool/build_web.sh           compila
#       ./tool/build_web.sh --serve   compila y sirve en http://127.0.0.1:8000
#
# En local hay que abrirlo con 127.0.0.1: en localhost pygbag busca sus paquetes
# en su propio servidor de desarrollo y el juego no arranca.

set -euo pipefail
cd "$(dirname "$0")/.."

STAGE=build/blockfall
rm -rf "$STAGE"
mkdir -p "$STAGE"
cp ./*.py "$STAGE/"
cp -R music "$STAGE/"

ARGS=(--app_name blockfall --title "BlockFall"
      --width 540 --height 960 --template web/template.tmpl)

python -m pygbag --build "${ARGS[@]}" "$STAGE"

# pygbag pone su propio icono: se sustituye por el del juego
cp web/favicon.png "$STAGE/build/web/favicon.png"

if [ "${1:-}" = "--serve" ]; then
  echo "Sirviendo en http://127.0.0.1:8000"
  python -m http.server 8000 --bind 127.0.0.1 --directory "$STAGE/build/web"
fi
