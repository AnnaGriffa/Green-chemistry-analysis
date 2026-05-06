from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List
from pathlib import Path


INPUT_PATH = Path(__file__).with_name("reactions.json")


@dataclass(frozen=True)
class Species:
    name: str
    coeff: int = 1


@dataclass(frozen=True)
class Reaction:
    name: str
    reactants: List[Species]
    products: List[Species]
    solvent: List[Species]


def load_reactions(path: Path = INPUT_PATH) -> dict[str, Reaction]:
    with open(path) as f:
        raw = json.load(f)

    reactions = {}

    for name, r in raw.items():
        reactions[name] = Reaction(
            name=name,
            reactants=[Species(**sp) for sp in r["reactants"]],
            products=[Species(**sp) for sp in r["products"]],
            solvent=[Species(**sp) for sp in r.get("solvent", [])],
        )

    return reactions