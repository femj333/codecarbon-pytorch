"""Answer-key verify_evidence(). INSTRUCTOR ONLY -- this is the solution to the
student's verify_evidence() task. Never ship this file.

Order of checks matches the proposal: endorsement -> integrity -> freshness.
The counter state is only advanced for records that pass all three, so a
rejected record can never "use up" a counter value.
"""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping

from .registry import Registry
from .verify import verify_signature

OK = "ok"
NOT_ENDORSED = "not_endorsed"
BAD_SIGNATURE = "bad_signature"
STALE_COUNTER = "stale_counter"
MALFORMED = "malformed"


def verify_evidence(record: Mapping[str, Any], registry: Registry,
                    last_counter: MutableMapping[str, int]) -> tuple[bool, str]:
    try:
        measured = record["measured"]
        chip_id = measured["chip_id"]
        counter = measured["counter"]
    except (KeyError, TypeError):
        return False, MALFORMED

    # Endorsement: is this a chip the verifier knows about?
    if chip_id not in registry:
        return False, NOT_ENDORSED

    # Integrity: signed by THAT chip's registered key, unchanged since?
    if not verify_signature(record, registry.public_key(chip_id)):
        return False, BAD_SIGNATURE

    # Freshness: strictly newer than the last accepted report from this chip.
    if counter <= last_counter.get(chip_id, 0):
        return False, STALE_COUNTER

    last_counter[chip_id] = counter
    return True, OK
