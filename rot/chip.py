"""Simulated AI chip with a PUF-style signing key and a monotonic counter.

INSTRUCTOR ONLY. Holds private keys. Never ship this file.

Stand-ins for real hardware:
  * PUF-derived key  -> Ed25519 key derived from (master seed, chip_id), so the
                        whole fleet is reproducible from one secret seed.
  * on-chip meter     -> the flops / energy_j values passed to report(); in the
                        game these come from torch.profiler and CodeCarbon.
  * monotonic counter -> incremented inside report() and never settable from
                        outside, so the only way to present an old counter
                        value is to replay an old record.
"""

from __future__ import annotations

import base64
import copy
import hashlib
from typing import Any, Mapping

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from .canonical import evidence_bytes

_PUF_TAG = b"ECE576-simulated-PUF/v1"


def derive_private_key(master_seed: bytes, label: str) -> Ed25519PrivateKey:
    """Deterministic Ed25519 key for a chip (or the manufacturer)."""
    if not master_seed:
        raise ValueError("master_seed must be non-empty")
    seed = hashlib.sha256(_PUF_TAG + b"|" + master_seed + b"|" + label.encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def public_key_b64(private_key: Ed25519PrivateKey) -> str:
    raw = private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return base64.b64encode(raw).decode("ascii")


class SimulatedChip:
    def __init__(self, chip_id: str, private_key: Ed25519PrivateKey):
        if not chip_id:
            raise ValueError("chip_id must be non-empty")
        self.chip_id = chip_id
        self._key = private_key  # the "PUF" secret; nothing reads it out
        self._counter = 0

    @property
    def public_key(self) -> str:
        return public_key_b64(self._key)

    @property
    def counter(self) -> int:
        """Counter value of the most recent report (0 = no reports yet)."""
        return self._counter

    def report(self, job_id: str, flops: int, energy_j: float,
               claims: Mapping[str, Any] | None = None) -> dict:
        """Sign one meter reading and return an evidence record.

        `claims` are operator-supplied and are copied into the record
        unsigned (e.g. {"declared_workload": "inference"}).
        """
        self._counter += 1
        measured = {
            "chip_id": self.chip_id,
            "job_id": job_id,
            "counter": self._counter,
            "flops": int(flops),
            "energy_j": float(energy_j),
        }
        signature = self._key.sign(evidence_bytes(measured))
        return {
            "measured": measured,
            "signature": base64.b64encode(signature).decode("ascii"),
            "claims": copy.deepcopy(dict(claims or {})),
        }

    def sign_as(self, measured: Mapping[str, Any]) -> dict:
        """Sign an arbitrary measured block WITHOUT touching the counter.

        Only for building adversarial records, e.g. a rogue chip that claims
        another chip's chip_id. Honest data must go through report().
        """
        signature = self._key.sign(evidence_bytes(measured))
        return {
            "measured": dict(measured),
            "signature": base64.b64encode(signature).decode("ascii"),
            "claims": {},
        }

    def __repr__(self) -> str:
        return f"SimulatedChip({self.chip_id!r}, counter={self._counter})"
