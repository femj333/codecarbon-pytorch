# Compliance Bouncer: simulated hardware root of trust

This module simulates the chip side of hardware-rooted compute governance. Each simulated chip has a signing key that stands in for its PUF key, plus a monotonic report counter. A trusted manufacturer endorses each chip's public key, and the verifier keeps a registry of endorsed chips and their owners. Every meter reading becomes a signed **evidence record**.

```
pip install -r requirements.txt
python -m pytest -q                 # 27 tests
python scripts/demo_rot.py          # attack matrix demo, writes out/registry.json and out/records.json
python scripts/build_student_kit.py # copies only the public files to dist/student_kit/
```

## Files

| File | Ships to students? | Purpose |
|---|---|---|
| `rot/canonical.py` | yes | Exact bytes that get signed (one definition shared by the signer and the verifier) |
| `rot/verify.py` | yes | `verify_signature(record, public_key_b64) -> bool`, plus an optional `verify_endorsement()` |
| `rot/registry.py` | yes | `Registry.load()`, `chip_id in reg`, `reg.public_key(id)`, `reg.owner(id)` |
| `rot/chip.py` | **no** | `SimulatedChip`: holds the private key, increments the counter, signs reports |
| `rot/manufacturer.py` | **no** | `Manufacturer` (fabricates chips and endorses their keys), `build_registry()`, `make_rogue_chip()` |
| `rot/attacks.py` | **no** | Helpers that build adversarial records for the level generator |
| `rot/reference.py` | **no** | Answer-key `verify_evidence()` |

`build_student_kit.py` refuses to finish if any signing code ends up in the kit.

## Evidence record format

```json
{
  "measured": {
    "chip_id": "chip-01",
    "job_id": "job-001",
    "counter": 1,
    "flops": 410000000000,
    "energy_j": 0.82
  },
  "signature": "<base64 Ed25519 signature>",
  "claims": { "declared_workload": "training" }
}
```

- **`measured`** is signed. Types are strict: `flops` and `counter` are ints, and `energy_j` is a float in **joules**. Changing any value, or the type of any value, invalidates the signature.
- **`claims`** is not signed. It holds operator assertions such as the declared workload type. Editing it never affects `verify_signature()`, which is the point of Level 3.
- The record never carries a public key. The verifier must take the key from the registry, and that lookup is the endorsement check.

## Mapping to the proposal's attacks

| Attack | How to make it | Caught by |
|---|---|---|
| FLOPs edited after signing (L1) | `attacks.tamper(rec, flops=...)` | integrity |
| Chip not in registry (L1) | `make_rogue_chip(id).report(...)` | endorsement |
| Rogue chip claims a registered ID | `attacks.spoof_chip_id(rogue, "chip-04", ...)` | integrity |
| Replayed old low-FLOP record (L2) | `attacks.replay(rec)` | freshness (counter) |
| Disguised workload type (L3) | `attacks.relabel(rec, declared_workload=...)` | **nothing in this layer**: the policy has to catch it |
| Fragmented run (L2) | honest `report()` calls on chips with the same owner | policy (per-owner totals via `reg.owner()`) |

## Notes for the level generator

- **Use one `SimulatedChip` object per chip for the whole level.** `fabricate()` with the same ID gives the same key but resets the counter to 0. A second object for the same chip would therefore emit counters that look replayed.
- **Stream order matters.** Freshness means "counter greater than the last accepted counter," so if two records from one chip arrive out of order, the later-arriving older one is rejected. Emit each chip's records in counter order unless you are building a replay on purpose.
- **Rejected records don't advance the counter state** (in the reference verifier). A tampered copy of a fresh record won't block the genuine record that arrives after it.
- **Keys are deterministic** from `CB_MASTER_SEED` + chip ID, so the whole fleet can be regenerated from one secret. Keep the seed out of the student kit and out of git.

## Open decisions for the team

1. **Cumulative or per-interval FLOPs?** Checkpoint records could report the job total so far or only the work since the last checkpoint. This changes how students sum totals, so it needs to be agreed with the harness side.
2. **Should a job's records be tied to one chip?** At the moment, any chip can report any `job_id`.
3. **Energy units.** The schema uses joules, which suits the 4.6 kJ limit. CodeCarbon reports kWh (1 kWh = 3.6 × 10⁶ J), so the harness has to convert before signing.
