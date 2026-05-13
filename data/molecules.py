from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


INPUT_PATH = Path(__file__).with_name("molecules.json")


@dataclass(frozen=True)
class Molecule:
    name: str
    molar_mass: float
    ghs_pictograms: list[str]


def load_molecules(path: Path = INPUT_PATH) -> dict[str, Molecule]:
    with open(path) as f:
        raw = json.load(f)

    molecules = {}

    for name, data in raw.items():
        molecules[name] = Molecule(
            name=name,
            molar_mass=data["molar_mass"],
            ghs_pictograms=data["ghs_pictograms"],
        )

    return molecules