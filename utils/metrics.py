import json
from pathlib import Path

from data.reactions import Reaction


MOLECULE_DATA_PATH = Path("data/molecule_datas.json")


def load_molecule_data():
    with open(MOLECULE_DATA_PATH) as f:
        return json.load(f)


MOLECULES = load_molecule_data()


def species_mass(species):
    molecule = MOLECULES[species.name]
    return species.coeff * molecule["molar_mass"]


def total_mass(species_list):
    return sum(species_mass(sp) for sp in species_list)


def atom_economy(reaction: Reaction):
    react_mass = total_mass(reaction.reactants)
    prod_mass = total_mass(reaction.products)

    if react_mass == 0:
        return 0

    return (prod_mass / react_mass) * 100


def e_factor(reaction: Reaction):
    react_mass = total_mass(reaction.reactants)
    prod_mass = total_mass(reaction.products)

    actual_product = prod_mass * reaction.yield_percent / 100

    if actual_product == 0:
        return float("inf")

    waste = react_mass - actual_product
    return waste / actual_product


def solvent_toxicity(reaction: Reaction):
    if not reaction.solvents:
        return 0

    total = 0

    for sp in reaction.solvents:
        pictograms = MOLECULES[sp.name]["ghs_pictograms"]
        total += len(pictograms)

    return total / len(reaction.solvents)