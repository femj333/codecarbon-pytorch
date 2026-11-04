"""
chip.py

A simulated AI chip: a secret signing key (stands in for the PUF key)
and a counter that goes up by one on every report.

INSTRUCTOR ONLY -- holds a private key. Do not give to students.
"""

import base64
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from rot.canonical import to_bytes


class Chip:
    def __init__(self, chip_id, private_key):
        self.chip_id = chip_id
        self._key = private_key   # never leaves the chip
        self.counter = 0          # 0 = no reports yet

    def public_key(self):
        raw = self._key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        return base64.b64encode(raw).decode()

    def report(self, job_id, flops, energy_kj):
        """Sign one meter reading. Returns {"measured": ..., "signature": ...}."""
        self.counter += 1
        measured = {
            "chip_id": self.chip_id,
            "job_id": job_id,
            "counter": self.counter,
            "flops": flops,
            "energy_kj": energy_kj,
        }
        signature = self._key.sign(to_bytes(measured))
        return {"measured": measured, "signature": base64.b64encode(signature).decode()}
