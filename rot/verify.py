"""
verify.py

verify_signature() -- the one crypto helper students get.

It only answers: "was record["measured"] signed by this public key, unchanged?"
Students still have to check the chip is in the registry and the counter is fresh.
It says nothing about unsigned fields like declared_type.

Ships to students.
"""

import base64
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from rot.canonical import to_bytes


def verify_signature(record, public_key):
    """True if the signature is valid for record["measured"] under public_key (base64)."""
    try:
        key = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key))
        key.verify(base64.b64decode(record["signature"]), to_bytes(record["measured"]))
        return True
    except (InvalidSignature, KeyError, ValueError, TypeError):
        return False
