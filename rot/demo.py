"""
demo.py

Shows every evidence check catching its attack.

python -m rot.demo        (run from the repo root)
"""

import copy
from rot.manufacturer import make_chip
from rot.registry import build_registry
from rot.reference import verify_evidence

SEED = "demo-seed"   # real data: use a secret seed, never committed

chip1 = make_chip(SEED, "chip-01")
chip2 = make_chip(SEED, "chip-02")
registry = build_registry([(chip1, "lab_01"), (chip2, "lab_02")])
rogue = make_chip("some-other-seed", "chip-99")   # not in the registry

honest = chip1.report("job_001", 349897090620, 0.6564)
small = chip2.report("job_002", 58556789011, 1.0765)
tampered = copy.deepcopy(chip1.report("job_003", 5438713243560, 4.8234))
tampered["measured"]["flops"] = 1000                # edited after signing
unregistered = rogue.report("job_004", 1000, 0.01)
replayed = copy.deepcopy(small)                     # resubmitted old record

last_counter = {}
for name, record in [("honest", honest), ("honest", small), ("edited FLOPs", tampered),
                     ("unregistered chip", unregistered), ("replay", replayed)]:
    ok, reason = verify_evidence(record, registry, last_counter)
    print(f"{name:18} {'PASS' if ok else 'FAIL':5} {reason}")
