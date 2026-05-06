import json


def load_json(path):
    with open(path) as f:
        return json.load(f)


def compute_mass(species_list, molecules_data):
    total = 0

    for sp in species_list:
        name = sp.name
        coeff = sp.coeff

        molar_mass = molecules_data[name]["molar_mass"]
        total += coeff * molar_mass

    return total


def compute_E_factor(reaction, molecules_data):
    react_mass = compute_mass(reaction.reactants, molecules_data)
    prod_mass = compute_mass(reaction.products, molecules_data)

    waste = react_mass - prod_mass

    return waste / prod_mass


# ---- Load files ----

molecule_data = load_json("data/molecules.json")
reaction = load_json("data/mreactions.json")

# ---- Compute ----

E_factor = compute_E_factor(reaction, molecule_data)

print(E_factor)