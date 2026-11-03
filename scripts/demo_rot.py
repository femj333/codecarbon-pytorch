"""Demo: build a fleet, emit honest + adversarial records, run the answer-key
verifier, and write registry.json / records.json to out/.

    python scripts/demo_rot.py

The FLOP and energy numbers here are placeholders. Real values come from the
torch.profiler / CodeCarbon harness.

Master seed: set CB_MASTER_SEED for real data. The default is for demos only.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rot import attacks  # noqa: E402
from rot.manufacturer import Manufacturer, build_registry, make_rogue_chip  # noqa: E402
from rot.reference import verify_evidence  # noqa: E402

seed = os.environ.get("CB_MASTER_SEED", "demo-seed-do-not-use-for-real-data").encode()
fab = Manufacturer(seed)

chips = {cid: fab.fabricate(cid) for cid in ["chip-01", "chip-02", "chip-03", "chip-04"]}
owners = {"chip-01": "Acme AI", "chip-02": "Acme AI",
          "chip-03": "Borealis Labs", "chip-04": "Cobalt Research"}
registry = build_registry(fab, [(chips[c], owners[c]) for c in chips])
rogue = make_rogue_chip("chip-99")

honest_small = chips["chip-01"].report("job-001", 4.1e11, 0.82, {"declared_workload": "training"})
honest_big = chips["chip-03"].report("job-002", 3.9e12, 7.4, {"declared_workload": "training"})
low_flop = chips["chip-02"].report("job-003", 2.0e10, 0.05, {"declared_workload": "inference"})
honest_next = chips["chip-01"].report("job-004", 3.0e11, 0.61, {"declared_workload": "training"})

stream = [
    ("honest, under limit", honest_small),
    ("honest, over limit (policy's job)", honest_big),
    ("honest, low FLOP", low_flop),
    ("FLOPs edited after signing", attacks.tamper(honest_next, flops=3_000_000)),
    ("unregistered chip", rogue.report("job-005", 1.0e11, 0.2, {"declared_workload": "inference"})),
    ("rogue chip using chip-04's ID", attacks.spoof_chip_id(rogue, "chip-04", "job-006", 1, 1.0e11, 0.2)),
    ("replay of low-FLOP report", attacks.replay(low_flop)),
    ("relabelled claim (signature still valid)", attacks.relabel(honest_next, declared_workload="inference")),
]

state: dict[str, int] = {}
print(f"{'case':45} {'chip':9} {'ctr':>3}  verdict")
print("-" * 80)
for label, rec in stream:
    ok, reason = verify_evidence(rec, registry, state)
    m = rec["measured"]
    print(f"{label:45} {m['chip_id']:9} {m['counter']:>3}  {'PASS' if ok else 'FAIL'} ({reason})")

out = ROOT / "out"
out.mkdir(exist_ok=True)
registry.save(out / "registry.json")
(out / "records.json").write_text(json.dumps([r for _, r in stream], indent=2) + "\n")
print(f"\nwrote {out/'registry.json'} and {out/'records.json'}")
