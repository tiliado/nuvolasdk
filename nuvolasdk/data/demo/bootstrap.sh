#!/bin/bash
set -eu

python3 -m nuvolasdk new-project \
  --no-git-repo \
  --id="nuvola_demo_player" \
  --name="Nuvola Player" \
  --url="nuvola://demo/main.html" \
  --maintainer-name="Jiří Janoušek" \
  --maintainer-mail="janousek.jiri@gmail.com" \
  --maintainer-github="fenryxo"

cd nuvola-app-nuvola-demo-player
rm integrate.js
ln -sv "$(python3 -m nuvolasdk data-dir)/demo/demo" .
ln -sv "$(python3 -m nuvolasdk data-dir)/demo/integrate.js" .
./configure
make all
