"""
canonical.py

Turns a chip's measurements into the exact bytes that get signed.
The chip (signing) and the student (verifying) must build identical bytes,
so both call to_bytes().

Ships to students.
"""

import json

# The values the chip measures and signs. Anything else in a record
# (record_id, declared_type, actor) is an unsigned operator claim.
SIGNED_FIELDS = ["chip_id", "job_id", "counter", "flops", "energy_kj"]


def to_bytes(measured):
    if sorted(measured) != sorted(SIGNED_FIELDS):
        raise ValueError(f"measured must have exactly these fields: {SIGNED_FIELDS}")
    # sorted keys + no spaces -> the same dict always gives the same bytes
    return json.dumps(measured, sort_keys=True, separators=(",", ":")).encode()
