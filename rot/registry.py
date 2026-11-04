"""
registry.py

The verifier's list of trusted chips:
    {"chip-01": {"public_key": "<base64>", "owner": "lab_01"}, ...}

A chip is "endorsed" if and only if it is in this registry.

Ships to students (they only need load_registry).
"""

import json


def build_registry(chips_and_owners):
    """[(chip, owner), ...] -> registry dict. Instructor side."""
    return {chip.chip_id: {"public_key": chip.public_key(), "owner": owner}
            for chip, owner in chips_and_owners}


def save_registry(registry, path):
    with open(path, "w") as f:
        json.dump(registry, f, indent=2)


def load_registry(path):
    with open(path) as f:
        return json.load(f)
