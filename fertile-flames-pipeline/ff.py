#!/usr/bin/env python3
"""ff — Fertile Flames pipeline CLI. The whole vertical slice runs through here.

Usage:
  ./ff.py status [VAULT]                 derived state of every canon node + scene
  ./ff.py pack "Scene 01-01" [VAULT]     assemble + freeze a context pack for a scene
"""
import sys
from pathlib import Path

from pipeline.vault import Vault
from pipeline.contextpack import build_pack
from pipeline.project import project

DEFAULT_VAULT = Path(__file__).parent / "vault"


def cmd_status(vault_path):
    v = Vault.load(vault_path)
    rows = project(v)
    w = max((len(n) for _, n, _ in rows), default=10)
    print(f"{'type':<12} {'name':<{w}} status")
    print("-" * (14 + w + 8))
    for t, n, s in rows:
        print(f"{t:<12} {n:<{w}} {s}")


def cmd_pack(scene, vault_path):
    v = Vault.load(vault_path)
    pack = build_pack(v, scene)
    out = Path(vault_path) / "control" / "context-packs" / f"{scene.replace(' ', '-')}-context.md"
    out.write_text(pack.markdown, encoding="utf-8")
    print(f"wrote {out}  (sha {pack.sha}, {len(pack.markdown)} bytes)")


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 1
    cmd = argv[1]
    if cmd == "status":
        cmd_status(argv[2] if len(argv) > 2 else DEFAULT_VAULT)
    elif cmd == "pack":
        if len(argv) < 3:
            print("pack needs a scene name"); return 1
        cmd_pack(argv[2], argv[3] if len(argv) > 3 else DEFAULT_VAULT)
    else:
        print(__doc__); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
