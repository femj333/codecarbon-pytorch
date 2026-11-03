"""Copy ONLY the public, secret-free modules into dist/student_kit/.

    python scripts/build_student_kit.py

Then fails loudly if anything that can sign ended up in the kit.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHIPPED = ["__init__.py", "canonical.py", "verify.py", "registry.py"]
FORBIDDEN = re.compile(r"Ed25519PrivateKey|\.sign\(|derive_private_key|master_seed")

dest = ROOT / "dist" / "student_kit" / "rot"
if dest.parent.exists():
    shutil.rmtree(dest.parent)
dest.mkdir(parents=True)

for name in SHIPPED:
    shutil.copy2(ROOT / "rot" / name, dest / name)

bad = [p.name for p in dest.glob("*.py") if FORBIDDEN.search(p.read_text())]
if bad:
    sys.exit(f"ERROR: signing code found in student kit: {bad}")

print(f"student kit written to {dest.parent}")
for p in sorted(dest.iterdir()):
    print("  rot/" + p.name)
