"""Signature-checking helpers given to students.

SHIPS TO STUDENTS (public keys only; nothing here can create a signature).

verify_signature() answers exactly one question: "was this record's measured
block signed by the holder of this public key, and is it unchanged since?"

It deliberately does NOT:
  * decide which public key to use  -> the student looks the chip up in the
    registry (that lookup IS the endorsement check),
  * check freshness                 -> the student tracks each chip's counter,
  * say anything about record["claims"] -> those fields are unsigned operator
    claims; editing them never changes the result of this function.
"""

from __future__ import annotations

import base64
import binascii
from typing import Any, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .canonical import EvidenceFormatError, endorsement_bytes, evidence_bytes


def _load_public_key(public_key_b64: str) -> Ed25519PublicKey:
    raw = base64.b64decode(public_key_b64, validate=True)
    return Ed25519PublicKey.from_public_bytes(raw)


def verify_signature(record: Mapping[str, Any], public_key_b64: str) -> bool:
    """Return True iff record["signature"] is a valid signature over
    record["measured"] under public_key_b64. Never raises on bad input."""
    try:
        measured = record["measured"]
        signature = base64.b64decode(record["signature"], validate=True)
        key = _load_public_key(public_key_b64)
        key.verify(signature, evidence_bytes(measured))
        return True
    except (KeyError, TypeError, ValueError, binascii.Error,
            EvidenceFormatError, InvalidSignature):
        return False


def verify_endorsement(chip_id: str, public_key_b64: str, endorsement_b64: str,
                       manufacturer_public_key_b64: str) -> bool:
    """Return True iff the manufacturer endorsed this (chip_id, public key) pair.

    Optional for students: the registry is only built from endorsed keys, so
    "chip is in the registry" already implies this. Provided for anyone who
    wants to audit the registry itself.
    """
    try:
        signature = base64.b64decode(endorsement_b64, validate=True)
        key = _load_public_key(manufacturer_public_key_b64)
        key.verify(signature, endorsement_bytes(chip_id, public_key_b64))
        return True
    except (TypeError, ValueError, binascii.Error,
            EvidenceFormatError, InvalidSignature):
        return False
