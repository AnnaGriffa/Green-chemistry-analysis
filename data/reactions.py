from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


INPUT_PATH = Path(__file__).with_name("reactions.json")


@dataclass(frozen=True)
class Species:
    name: str
    coeff: float = 1.0


@dataclass(frozen=True)
class Reaction:
    name: str
    reactants: list[Species]
    products: list[Species]
    solvents: list[Species]
    yield_percent: float
    temperature: float
    steps: int


def load_reactions(path: Path = INPUT_PATH) -> dict[str, Reaction]:
    with open(path) as f:
        raw = json.load(f)

    reactions = {}

    for name, r in raw.items():
        reactions[name] = Reaction(
            name=name,
            reactants=[Species(**sp) for sp in r["reactants"]],
            products=[Species(**sp) for sp in r["products"]],
            solvents=[Species(**sp) for sp in r.get("solvents", [])],
            yield_percent=r["yield_percent"],
            temperature=r["temperature"],
            steps=r["steps"],
        )

    return reactions