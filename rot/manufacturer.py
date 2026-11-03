"""Trusted chip manufacturer: fabricates chips and endorses their public keys.

INSTRUCTOR ONLY. Holds private keys. Never ship this file.
"""

from __future__ import annotations

import base64
from typing import Iterable, Tuple

from .canonical import endorsement_bytes
from .chip import SimulatedChip, derive_private_key, public_key_b64
from .registry import Registry


class Manufacturer:
    def __init__(self, master_seed: bytes, name: str = "TrustedFab"):
        self.name = name
        self._seed = master_seed
        self._key = derive_private_key(master_seed, f"manufacturer:{name}")

    @property
    def public_key(self) -> str:
        return public_key_b64(self._key)

    def fabricate(self, chip_id: str) -> SimulatedChip:
        """Make a chip whose key is derived from this manufacturer's seed.

        Calling this twice with the same chip_id yields the same key (useful
        for regenerating data) but a fresh counter, so keep one SimulatedChip
        object per chip while generating a level.
        """
        return SimulatedChip(chip_id, derive_private_key(self._seed, f"chip:{chip_id}"))

    def endorse(self, chip: SimulatedChip) -> str:
        sig = self._key.sign(endorsement_bytes(chip.chip_id, chip.public_key))
        return base64.b64encode(sig).decode("ascii")


def build_registry(manufacturer: Manufacturer,
                   chips_and_owners: Iterable[Tuple[SimulatedChip, str]]) -> Registry:
    """Registry containing only chips this manufacturer endorses."""
    reg = Registry(manufacturer.public_key)
    for chip, owner in chips_and_owners:
        reg._add(chip.chip_id, chip.public_key, owner, manufacturer.endorse(chip))
    return reg


def make_rogue_chip(chip_id: str, rogue_seed: bytes = b"not-the-trusted-fab") -> SimulatedChip:
    """A chip with a working key that no trusted manufacturer endorsed."""
    return SimulatedChip(chip_id, derive_private_key(rogue_seed, f"rogue:{chip_id}"))
