import json


def load_json(path):
    with open(path) as f:
        return json.load(f)


def compute_mass(species, data):
    total = 0

    for sp in species:
        name = sp["name"]
        coeff = sp.get("coeff", 1)

        molar_mass = data[name]["molar_mass"]
        total += coeff * molar_mass

    return total


def compute_E_factor(reaction, data):
    react_mass = compute_mass(reaction["reactants"], data)
    prod_mass = compute_mass(reaction["products"], data)

    waste = react_mass - prod_mass

    return waste / prod_mass


# ---- Load files ----

molecule_data = load_json("data/molecule_datas.json")
reaction = load_json("data/similar.json")

# ---- Compute ----

E_factor = compute_E_factor(reaction, molecule_data)

print(E_factor)