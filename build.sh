#!/usr/bin/env sh

SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)

if command -v poetry >/dev/null 2>&1; then
  echo "SCRIPT_DIR: $SCRIPT_DIR"
  if [ ! -d "$SCRIPT_DIR" ]; then
    echo "ERROR: 'SCRIPT_DIR=$SCRIPT_DIR' doesn't seem to exist!"
    exit 1
  fi
  cd $SCRIPT_DIR \
    && poetry install \
    && export FLASK_APP='awsmgr.app' \
    && poetry run flask digest compile \
    && touch ./awsmgr/__init__.py \
    && poetry build \
    && ls -lhtp ./dist/*.whl | head -n1 | awk '{print $9, $5}' \
    && echo "Done."
  #&&  
fi