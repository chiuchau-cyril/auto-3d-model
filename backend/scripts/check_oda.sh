#!/usr/bin/env bash
set -euo pipefail

DEFAULT_PATH="/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter"
ODA_PATH="${ODAFC_EXEC_PATH:-$DEFAULT_PATH}"

if [[ -z "${ODAFC_EXEC_PATH:-}" ]]; then
  echo "[warn] ODAFC_EXEC_PATH not set; falling back to $DEFAULT_PATH"
fi

if [[ ! -x "$ODA_PATH" ]]; then
  echo "[error] ODA File Converter not found or not executable at: $ODA_PATH" >&2
  echo "[error] Install from https://www.opendesign.com/guestfiles/oda_file_converter" >&2
  echo "[error] Then export ODAFC_EXEC_PATH to its absolute path." >&2
  exit 1
fi

echo "[ok] ODA File Converter found at: $ODA_PATH"
