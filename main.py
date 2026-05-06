from data.reactions import load_reactions
from data.molecules import load_molecules
from Facteur_E import compute_E_factor

# load data
reactions = load_reactions()
molecules = load_molecules()

# pick a reaction
reaction = reactions["neutralization"]


E = compute_E_factor(reaction, molecules)
print("E-factor:", E)