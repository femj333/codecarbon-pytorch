"""Helpers for producing adversarial records, for the level generator.

INSTRUCTOR ONLY. None of these need a private key except spoof_chip_id(), which
uses a rogue chip's own key -- exactly what a real attacker would have.

Each helper returns a NEW record and leaves its input untouched.
"""

from __future__ import annotations

import copy
from typing import Any

from .chip import SimulatedChip


def tamper(record: dict, **measured_changes: Any) -> dict:
    """Telemetry spoofing (edited evidence): change signed values after signing.

    e.g. tamper(rec, flops=rec["measured"]["flops"] // 10)
    -> fails integrity.
    """
    out = copy.deepcopy(record)
    for field, value in measured_changes.items():
        if field not in out["measured"]:
            raise KeyError(f"unknown measured field {field!r}")
        out["measured"][field] = value
    return out


def replay(record: dict) -> dict:
    """Replayed evidence: resubmit an old, validly signed record unchanged.

    -> passes endorsement and integrity, fails freshness (stale counter).
    """
    return copy.deepcopy(record)


def relabel(record: dict, **claim_changes: Any) -> dict:
    """Workload disguise: change UNSIGNED operator claims.

    -> still passes all three evidence checks; only the policy can catch it.
    """
    out = copy.deepcopy(record)
    out.setdefault("claims", {}).update(claim_changes)
    return out


def spoof_chip_id(rogue: SimulatedChip, victim_chip_id: str, job_id: str,
                  counter: int, flops: int, energy_j: float) -> dict:
    """Fabricated evidence: a rogue chip signs a record claiming a registered
    chip's identity. -> chip IS in the registry, but integrity fails because
    the signature doesn't match the registered public key.
    """
    return rogue.sign_as({
        "chip_id": victim_chip_id,
        "job_id": job_id,
        "counter": int(counter),
        "flops": int(flops),
        "energy_j": float(energy_j),
    })


def strip_signature(record: dict) -> dict:
    """Record with the signature removed or emptied. -> fails integrity."""
    out = copy.deepcopy(record)
    out["signature"] = ""
    return out
