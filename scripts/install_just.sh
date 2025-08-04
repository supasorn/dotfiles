#!/bin/bash
set -e

curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to DEST && sudo cp DEST/just /usr/bin && rm -rf DEST
