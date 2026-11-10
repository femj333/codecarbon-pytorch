"""
student.py

The student writes two functions:
    1. `verify_evidence()` a helper function to determine if evidence can be trusted. It should return True or False.
    2. `policy_checker()` called once per record, in order. It should return "allow" or "block"

A record looks like this:
    {"record_id": "L1-001",
    "measured": {"chip_id": "chip-04", "job_id": "job_008", "counter": 1,
                 "flops": 349827463012, "energy_kj": 0.6564},
    "signature": "...",
    "declared_type": "training"}

Only "measured" is signed. Students can reference `game_data.json` for more examples.

context gives you:
    context["config"]  {"flop_limit": ..., "energy_limit_kj": ...}
    context["ranges"]  reference ranges per declared type ("training", "inference")
    context["registry"]  chip_id -> {"public_key": ..., "owner": ...}
    context["state"]     a dict that persists between calls, resets every level
"""

from verify import verify_signature

# Energy readings are noisy (~ +/-5%), so a job can read just under the energy limit while being over it. Treat anything
# within one noise-width of the limit as over. The cost is some honest jobs just under the limit get blocked.
ENERGY_MARGIN = 0.05

# FLOPs per kJ identifies the kind of work, but it varies from run to run, so allow 10% beyond the reference band.
RATIO_MARGIN = 0.1

"""
Return True if the record can be trusted. Return False if it cannot. Does not change any state.
"""
def verify_evidence(record, context) -> bool:
    measured = record["measured"]
    chip = measured["chip_id"]
    registry = context["registry"]

    # TODO -> student implements this
    return True

"""
Return 'allow' if a record is legitimate. Return 'block' if it is not.
"""
def policy_checker(record, context) -> str:
    state = context["state"]
    config = context["config"]
    measured = record["measured"]

    # TODO -> student implements this
    return "allow"