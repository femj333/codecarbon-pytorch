"""
reference.py

Answer-key verify_evidence(): what the student's version should do.

INSTRUCTOR ONLY -- this is the solution. Do not give to students.

    last_counter = {}            # chip_id -> counter of last accepted record
    ok, reason = verify_evidence(record, registry, last_counter)
"""

from rot.verify import verify_signature


def verify_evidence(record, registry, last_counter):
    chip_id = record["measured"]["chip_id"]
    counter = record["measured"]["counter"]

    # 1. Endorsement: do we trust this chip at all?
    if chip_id not in registry:
        return False, "chip not in registry"

    # 2. Integrity: signed by THAT chip's registered key, unchanged since?
    if not verify_signature(record, registry[chip_id]["public_key"]):
        return False, "bad signature"

    # 3. Freshness: newer than the last report we accepted from this chip?
    if counter <= last_counter.get(chip_id, 0):
        return False, "stale counter (replay)"

    # only records that pass all three move the counter forward
    last_counter[chip_id] = counter
    return True, "ok"
