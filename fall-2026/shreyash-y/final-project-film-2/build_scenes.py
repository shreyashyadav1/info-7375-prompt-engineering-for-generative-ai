#!/usr/bin/env python3
"""build_scenes.py: assemble scenes.py = iso_kit.py + iso_originals_25.py + scene_body.py, and copy logos.

Gate A copies only scenes.py into its sandbox, so the kit and the props must be pasted in, not imported.
Usage: python3 build_scenes.py /path/to/brutalist.art
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TK = Path(sys.argv[1] if len(sys.argv) > 1 else "../../brutalist.art-nov").resolve()
tpl = TK / "skills/make/show-tell/templates"
parts = [(tpl / "iso_kit.py").read_text(), (tpl / "iso_originals_25.py").read_text(), (HERE / "scene_body.py").read_text()]
(HERE / "scenes.py").write_text("\n\n".join(parts))
(HERE / "images").mkdir(exist_ok=True)
for name in ["claude-01", "anthropic-01", "python-01", "claude-code-01", "github-01"]:
    company = name.rsplit("-", 1)[0]
    shutil.copy(TK / "icons/logos" / company / f"{name}.svg", HERE / "images" / f"{name}.svg")
print("scenes.py:", sum(p.count("\n") for p in parts), "lines")
