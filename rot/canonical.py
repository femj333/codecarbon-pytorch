"""Canonical byte encoding for everything that gets signed.

SHIPS TO STUDENTS (no secrets here).

A signature is over bytes, not over a Python dict, so the signer and the
verifier must turn the same values into exactly the same bytes. This module is
the single definition of that encoding; both the instructor's signer and the
student's verify_signature() import it.

Rules:
  * A fixed domain-separation prefix, so a signature made for one purpose
    (an evidence record) can never be reused as another (an endorsement).
  * Exactly the fields in SIGNED_FIELDS, no more, no less.
  * Strict types: flops and counter are ints, energy_j is a float. A value of
    the wrong type is rejected rather than coerced, so "editing" a record by
    changing 2300000000000 to 2300000000000.4 cannot slip through a cast.
  * JSON with sorted keys and no whitespace. Python's float repr round-trips
    exactly, so a record loaded from JSON re-encodes to identical bytes.
"""

from __future__ import annotations

import json
import math
from typing import Any, Mapping

EVIDENCE_DOMAIN = b"ECE576-compliance-bouncer/evidence/v1\n"
ENDORSEMENT_DOMAIN = b"ECE576-compliance-bouncer/endorsement/v1\n"

# Values the chip itself measured. These are signed.
# Anything else in a record (e.g. declared workload type) is an operator claim
# and is NOT covered by the signature.
SIGNED_FIELDS: dict[str, type] = {
    "chip_id": str,
    "job_id": str,
    "counter": int,
    "flops": int,
    "energy_j": float,
}


class EvidenceFormatError(ValueError):
    """Raised when a payload cannot be canonically encoded."""


def _check_measured(measured: Mapping[str, Any]) -> None:
    if not isinstance(measured, Mapping):
        raise EvidenceFormatError("measured payload must be a mapping")
    keys = set(measured)
    expected = set(SIGNED_FIELDS)
    if keys != expected:
        missing = sorted(expected - keys)
        extra = sorted(keys - expected)
        raise EvidenceFormatError(f"field mismatch: missing={missing} extra={extra}")
    for name, typ in SIGNED_FIELDS.items():
        value = measured[name]
        # bool is a subclass of int in Python; never accept it as a number.
        if isinstance(value, bool) or type(value) is not typ:
            raise EvidenceFormatError(
                f"{name} must be {typ.__name__}, got {type(value).__name__}"
            )
    if not measured["chip_id"] or not measured["job_id"]:
        raise EvidenceFormatError("chip_id and job_id must be non-empty")
    if measured["counter"] < 0 or measured["flops"] < 0:
        raise EvidenceFormatError("counter and flops must be non-negative")
    energy = measured["energy_j"]
    if not math.isfinite(energy) or energy < 0:
        raise EvidenceFormatError("energy_j must be finite and non-negative")


def _json(obj: Mapping[str, Any]) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("ascii")


def evidence_bytes(measured: Mapping[str, Any]) -> bytes:
    """Bytes a chip signs for one meter reading."""
    _check_measured(measured)
    return EVIDENCE_DOMAIN + _json(measured)


def endorsement_bytes(chip_id: str, public_key_b64: str) -> bytes:
    """Bytes the manufacturer signs to endorse a chip's public key."""
    if not isinstance(chip_id, str) or not chip_id:
        raise EvidenceFormatError("chip_id must be a non-empty string")
    if not isinstance(public_key_b64, str) or not public_key_b64:
        raise EvidenceFormatError("public_key must be a non-empty string")
    return ENDORSEMENT_DOMAIN + _json({"chip_id": chip_id, "public_key": public_key_b64})
