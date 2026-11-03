"""The verifier's registry of endorsed chips and their registered owners.

SHIPS TO STUDENTS (read side). Building a registry needs the manufacturer, see
manufacturer.build_registry().

registry.json layout:
{
  "manufacturer_public_key": "<b64>",
  "chips": {
    "chip-01": {"public_key": "<b64>", "owner": "Acme AI", "endorsement": "<b64>"},
    ...
  }
}
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator


class Registry:
    def __init__(self, manufacturer_public_key: str, chips: dict[str, dict] | None = None):
        self.manufacturer_public_key = manufacturer_public_key
        self._chips: dict[str, dict] = dict(chips or {})

    # ---- lookups students use -------------------------------------------
    def __contains__(self, chip_id: object) -> bool:
        return chip_id in self._chips

    def __iter__(self) -> Iterator[str]:
        return iter(self._chips)

    def __len__(self) -> int:
        return len(self._chips)

    def public_key(self, chip_id: str) -> str:
        """Raises KeyError if the chip is not registered."""
        return self._chips[chip_id]["public_key"]

    def owner(self, chip_id: str) -> str:
        """Raises KeyError if the chip is not registered."""
        return self._chips[chip_id]["owner"]

    def entry(self, chip_id: str) -> dict:
        return dict(self._chips[chip_id])

    # ---- persistence ----------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "manufacturer_public_key": self.manufacturer_public_key,
            "chips": {cid: dict(e) for cid, e in sorted(self._chips.items())},
        }

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n")

    @classmethod
    def from_dict(cls, data: dict) -> "Registry":
        return cls(data["manufacturer_public_key"], data["chips"])

    @classmethod
    def load(cls, path: str | Path) -> "Registry":
        return cls.from_dict(json.loads(Path(path).read_text()))

    # ---- used only while building ---------------------------------------
    def _add(self, chip_id: str, public_key: str, owner: str, endorsement: str) -> None:
        if chip_id in self._chips:
            raise ValueError(f"chip {chip_id!r} already registered")
        self._chips[chip_id] = {
            "public_key": public_key,
            "owner": owner,
            "endorsement": endorsement,
        }
