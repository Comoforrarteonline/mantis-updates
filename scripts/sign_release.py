#!/usr/bin/env python3
"""sign_release.py — utilitario local para firmar un entry de releases.json.

Uso:
    UPDATE_SIGNING_KEY=xxx python sign_release.py release.json

Donde release.json es un objeto sin 'signature'. Imprime el objeto con el campo
'signature' añadido. Útil para firmar manualmente fuera del workflow.
"""
import hashlib
import hmac
import json
import os
import sys
from pathlib import Path


def canonical_payload(entry: dict) -> bytes:
    filtered = {k: v for k, v in entry.items() if k != "signature"}
    return json.dumps(filtered, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign(entry: dict, key: str) -> dict:
    sig = hmac.new(key.encode(), canonical_payload(entry), hashlib.sha256).hexdigest()
    return {**entry, "signature": sig}


def main():
    if len(sys.argv) != 2:
        print("Usage: UPDATE_SIGNING_KEY=... python sign_release.py entry.json", file=sys.stderr)
        sys.exit(1)
    key = os.environ.get("UPDATE_SIGNING_KEY", "").strip()
    if not key:
        print("ERROR: UPDATE_SIGNING_KEY env var requerida", file=sys.stderr)
        sys.exit(2)

    entry = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    signed = sign(entry, key)
    print(json.dumps(signed, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
