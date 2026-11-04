"""
manufacturer.py

The trusted manufacturer makes chips. Each chip's key is derived from one
secret seed + the chip ID, so the same seed always rebuilds the same chips.

A "rogue" chip (not in the registry) is just a chip made with a different seed.

INSTRUCTOR ONLY -- the seed can recreate every key. Never commit a real seed.
"""

import hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from rot.chip import Chip


def make_chip(seed, chip_id):
    key_bytes = hashlib.sha256(f"{seed}:{chip_id}".encode()).digest()  # 32 bytes
    return Chip(chip_id, Ed25519PrivateKey.from_private_bytes(key_bytes))
