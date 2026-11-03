import base64
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rot import attacks  # noqa: E402
from rot.canonical import EvidenceFormatError, evidence_bytes  # noqa: E402
from rot.manufacturer import Manufacturer, build_registry, make_rogue_chip  # noqa: E402
from rot.reference import (BAD_SIGNATURE, MALFORMED, NOT_ENDORSED, OK,  # noqa: E402
                           STALE_COUNTER, verify_evidence)
from rot.registry import Registry  # noqa: E402
from rot.verify import verify_endorsement, verify_signature  # noqa: E402

SEED = b"test-master-seed"


@pytest.fixture
def fleet():
    fab = Manufacturer(SEED)
    a1, a2, b1 = fab.fabricate("chip-a1"), fab.fabricate("chip-a2"), fab.fabricate("chip-b1")
    reg = build_registry(fab, [(a1, "Acme"), (a2, "Acme"), (b1, "Borealis")])
    return fab, reg, {"a1": a1, "a2": a2, "b1": b1}


# ---------------------------------------------------------------- keys / registry

def test_keys_are_deterministic_and_distinct():
    c1 = Manufacturer(SEED).fabricate("chip-x")
    c2 = Manufacturer(SEED).fabricate("chip-x")
    c3 = Manufacturer(SEED).fabricate("chip-y")
    c4 = Manufacturer(b"other-seed").fabricate("chip-x")
    assert c1.public_key == c2.public_key
    assert len({c1.public_key, c3.public_key, c4.public_key}) == 3


def test_registry_entries_are_endorsed(fleet):
    fab, reg, _ = fleet
    for cid in reg:
        e = reg.entry(cid)
        assert verify_endorsement(cid, e["public_key"], e["endorsement"], fab.public_key)
    # endorsement is bound to the chip_id
    e = reg.entry("chip-a1")
    assert not verify_endorsement("chip-a2", e["public_key"], e["endorsement"], fab.public_key)


def test_rogue_manufacturer_endorsement_rejected(fleet):
    fab, _, _ = fleet
    fake_fab = Manufacturer(b"evil-seed")
    chip = fake_fab.fabricate("chip-z")
    assert not verify_endorsement("chip-z", chip.public_key, fake_fab.endorse(chip), fab.public_key)


def test_registry_roundtrip(tmp_path, fleet):
    _, reg, _ = fleet
    p = tmp_path / "registry.json"
    reg.save(p)
    reg2 = Registry.load(p)
    assert reg2.to_dict() == reg.to_dict()
    assert reg2.owner("chip-b1") == "Borealis"
    with pytest.raises(ValueError):
        reg2._add("chip-a1", "x", "y", "z")


# ---------------------------------------------------------------- signing

def test_honest_record_verifies(fleet):
    _, reg, c = fleet
    rec = c["a1"].report("job-1", 10**9, 1.25, {"declared_workload": "inference"})
    assert rec["measured"]["counter"] == 1
    assert verify_signature(rec, reg.public_key("chip-a1"))
    assert not verify_signature(rec, reg.public_key("chip-a2"))  # wrong key


def test_counter_is_monotonic(fleet):
    _, _, c = fleet
    counters = [c["a1"].report(f"j{i}", 1, 0.1)["measured"]["counter"] for i in range(5)]
    assert counters == [1, 2, 3, 4, 5]


def test_json_roundtrip_preserves_signature(fleet):
    _, reg, c = fleet
    rec = c["a1"].report("job-1", 2_299_999_999_999, 4.5999999999, {})
    rec2 = json.loads(json.dumps(rec))
    assert verify_signature(rec2, reg.public_key("chip-a1"))


@pytest.mark.parametrize("field,value", [
    ("flops", 1),
    ("energy_j", 0.001),
    ("job_id", "job-other"),
    ("counter", 99),
    ("chip_id", "chip-a2"),
])
def test_any_measured_edit_breaks_signature(fleet, field, value):
    _, reg, c = fleet
    rec = c["a1"].report("job-1", 5 * 10**12, 9.0)
    bad = attacks.tamper(rec, **{field: value})
    assert not verify_signature(bad, reg.public_key("chip-a1"))
    assert verify_signature(rec, reg.public_key("chip-a1"))  # original untouched


def test_type_change_breaks_signature(fleet):
    _, reg, c = fleet
    rec = c["a1"].report("job-1", 5 * 10**12, 9.0)
    assert not verify_signature(attacks.tamper(rec, flops=5e12), reg.public_key("chip-a1"))
    assert not verify_signature(attacks.tamper(rec, flops=True), reg.public_key("chip-a1"))


def test_claims_are_not_covered_by_signature(fleet):
    """Teaching point: a valid signature says nothing about the declared type."""
    _, reg, c = fleet
    rec = c["a1"].report("job-1", 5 * 10**12, 9.0, {"declared_workload": "training"})
    disguised = attacks.relabel(rec, declared_workload="inference")
    assert verify_signature(disguised, reg.public_key("chip-a1"))


@pytest.mark.parametrize("mutate", [
    lambda r: r.pop("signature"),
    lambda r: r.pop("measured"),
    lambda r: r.__setitem__("signature", "not base64!!"),
    lambda r: r.__setitem__("signature", ""),
    lambda r: r["measured"].__setitem__("extra", 1),
    lambda r: r["measured"].pop("energy_j"),
    lambda r: r.__setitem__("measured", "nope"),
])
def test_malformed_records_return_false_not_raise(fleet, mutate):
    _, reg, c = fleet
    rec = c["a1"].report("job-1", 1, 0.5)
    mutate(rec)
    assert verify_signature(rec, reg.public_key("chip-a1")) is False


def test_bad_public_key_returns_false(fleet):
    _, _, c = fleet
    rec = c["a1"].report("job-1", 1, 0.5)
    assert verify_signature(rec, "garbage") is False
    assert verify_signature(rec, base64.b64encode(b"short").decode()) is False


def test_canonical_rejects_bad_values():
    good = {"chip_id": "c", "job_id": "j", "counter": 1, "flops": 1, "energy_j": 1.0}
    evidence_bytes(good)
    for change in [{"flops": -1}, {"energy_j": float("nan")}, {"energy_j": float("inf")},
                   {"chip_id": ""}, {"energy_j": 1}]:
        with pytest.raises(EvidenceFormatError):
            evidence_bytes({**good, **change})


def test_evidence_signature_cannot_be_reused_as_endorsement(fleet):
    """Domain separation: a chip signature is never a valid endorsement."""
    fab, reg, c = fleet
    rec = c["a1"].report("job-1", 1, 0.5)
    assert not verify_endorsement("chip-a1", reg.public_key("chip-a1"),
                                  rec["signature"], c["a1"].public_key)


# ---------------------------------------------------------------- reference verify_evidence

def test_reference_verifier_attack_matrix(fleet):
    fab, reg, c = fleet
    rogue = make_rogue_chip("chip-rogue")
    state = {}

    honest1 = c["a1"].report("job-1", 10**11, 0.3)
    honest2 = c["a1"].report("job-2", 10**11, 0.3)
    other_chip = c["b1"].report("job-3", 10**11, 0.3)

    cases = [
        (honest1, True, OK),
        (attacks.tamper(honest2, flops=1), False, BAD_SIGNATURE),     # edited
        (honest2, True, OK),                                           # unaffected by the failed copy
        (attacks.replay(honest1), False, STALE_COUNTER),               # replayed
        (other_chip, True, OK),                                        # independent counter
        (rogue.report("job-4", 1, 0.1), False, NOT_ENDORSED),          # unregistered chip
        (attacks.spoof_chip_id(rogue, "chip-a2", "job-5", 1, 1, 0.1),
         False, BAD_SIGNATURE),                                        # registered id, wrong key
        (attacks.strip_signature(c["a2"].report("job-6", 1, 0.1)),
         False, BAD_SIGNATURE),
        ({"garbage": True}, False, MALFORMED),
    ]
    for rec, ok, reason in cases:
        assert verify_evidence(rec, reg, state) == (ok, reason)

    assert state == {"chip-a1": 2, "chip-b1": 1}  # rejected records never advance state


def test_failed_record_does_not_burn_counter(fleet):
    """A tampered copy of a fresh record is rejected without blocking the real one."""
    _, reg, c = fleet
    state = {}
    rec = c["a1"].report("job-1", 1, 0.1)
    assert verify_evidence(attacks.tamper(rec, flops=0), reg, state)[0] is False
    assert verify_evidence(rec, reg, state) == (True, OK)


def test_out_of_order_delivery_rejects_older(fleet):
    """Freshness is 'higher than last accepted', so an older record arriving late
    is rejected. Stream order is a generator design decision."""
    _, reg, c = fleet
    state = {}
    r1 = c["a1"].report("job-1", 1, 0.1)
    r2 = c["a1"].report("job-2", 1, 0.1)
    assert verify_evidence(r2, reg, state) == (True, OK)
    assert verify_evidence(r1, reg, state) == (False, STALE_COUNTER)
