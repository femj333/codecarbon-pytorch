# Simulated Hardware Root of Trust

Each simulated chip signs its own FLOP and energy readings, so a verifier can tell which chip
a record came from and that nobody edited it. This stands in for a chip's PUF-derived key.

## Setup

```bash
pip install -r rot/requirements.txt
```

## See it work

From the repo root:

```bash
python -m rot.demo
```

```
honest             PASS  ok
honest             PASS  ok
edited FLOPs       FAIL  bad signature
unregistered chip  FAIL  chip not in registry
replay             FAIL  stale counter (replay)
```

## Files

| File | Gives students? | What it does |
|---|---|---|
| `canonical.py` | yes | `to_bytes()`: the exact bytes that get signed |
| `verify.py` | yes | `verify_signature(record, public_key)` -> True/False |
| `registry.py` | yes | `load_registry()`; chip_id -> public key + owner |
| `chip.py` | **no** | `Chip`: private key + counter, `report()` signs a reading |
| `manufacturer.py` | **no** | `make_chip(seed, chip_id)` |
| `reference.py` | **no** | Answer-key `verify_evidence()` |
| `demo.py` | no | The demo above |

## A signed record

```json
{
  "measured": {"chip_id": "chip-01", "job_id": "job_008", "counter": 1,
                "flops": 349897090620, "energy_kj": 0.6564},
  "signature": "<base64>"
}
```

`measured` is signed. Anything added next to it (`record_id`, `declared_type`, `actor`) is an
unsigned operator claim: editing it does not break the signature. That is the Level 3 lesson.

## Making records (instructor)

```python
from rot.manufacturer import make_chip
from rot.registry import build_registry, save_registry

chip = make_chip(SECRET_SEED, "chip-01")         # make each chip ONCE per level
save_registry(build_registry([(chip, "lab_01")]), "registry.json")

record = chip.report("job_008", 349897090620, 0.6564)   # counter goes 1, 2, 3...
record.update(record_id="L1-001", declared_type="training")
```

Attacks, by hand:

- **Edited:** change `record["measured"]["flops"]` after signing -> bad signature
- **Unregistered chip:** `make_chip("other-seed", "chip-99")`, left out of the registry
- **Replay:** submit an old record again -> stale counter
- **Disguise:** change `declared_type` -> signature still valid, the policy must catch it

## Rules to keep

- Never commit a real seed. Anyone with it can rebuild every chip key.
- Calling `make_chip()` twice for the same chip resets its counter to 0, which makes later
  records look like replays. Make each chip once and reuse it.
- Emit each chip's records in counter order. An older record arriving late is rejected.
