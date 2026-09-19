#!/usr/bin/env bash
# Gera os tamanhos web da logo a partir dos PNGs originais (1254×1254, fundo sólido).
# Requer ImageMagick 7 (`magick`). Uso: bash scripts/gerar-logos.sh [pasta-destino-do-app]
# Os originais ficam intactos: assets/marca/logo-estudada-escuro.png e logo-estudata-claro.png.
set -euo pipefail
cd "$(dirname "$0")/../assets/marca"
DARK=logo-estudada-escuro.png
LIGHT=logo-estudata-claro.png

# recorte quadrado centrado no desenho, com margem: square SRC FATOR SAIDA TAMANHO
square() {
  local src=$1 factor=$2 out=$3 size=$4
  read -r w h x y < <(magick "$src" -fuzz 3% -trim -format '%w %h %X %Y\n' info: | tr -d '+')
  local side cx cy x0 y0
  side=$(python3 -c "print(round(max($w,$h)*$factor))")
  cx=$((x + w / 2)); cy=$((y + h / 2))
  x0=$((cx - side / 2)); y0=$((cy - side / 2))
  magick "$src" -crop "${side}x${side}+${x0}+${y0}" +repage -resize "${size}x${size}" -strip \
    -define png:compression-level=9 "$out"
}

# site e app: logo para interface (exibida a 24–40 px; 2× e 3× para telas densas)
square "$DARK"  1.10 logo-escuro-128.png 128
square "$LIGHT" 1.10 logo-claro-128.png 128
square "$DARK"  1.10 logo-escuro-512.png 512
# favicons: recorte justo para ficar legível em 16–32 px
square "$DARK" 1.04 favicon-32.png 32
square "$DARK" 1.04 favicon-16.png 16
# ícones de instalação (fundo sólido, margem confortável)
square "$DARK" 1.25 apple-touch-icon-180.png 180
square "$DARK" 1.25 icon-192.png 192

# ícones usados só pelo app (PWA): gerados direto na pasta do app, se informada
if [ "${1:-}" != "" ]; then
  mkdir -p "$1"
  square "$DARK" 1.25 "$1/icon-512.png" 512
  # maskable: desenho dentro da zona segura de 80%
  square "$DARK" 1.50 "$1/icon-maskable-192.png" 192
  square "$DARK" 1.50 "$1/icon-maskable-512.png" 512
  cp favicon-16.png favicon-32.png apple-touch-icon-180.png icon-192.png "$1"/
  cp logo-escuro-128.png logo-claro-128.png "$1"/
  echo "ícones do app gerados em $1"
fi
ls -la logo-*-128.png logo-escuro-512.png favicon-*.png apple-touch-icon-180.png icon-192.png
