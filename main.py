from rdkit import Chem

reaction = {
    "reactants": [
        {"smiles": "[Na+].[OH-]", "coeff": 1},
        {"smiles": "Cl", "coeff": 1}
    ],
    "products": [
        {"smiles": "[Na+].[Cl-]", "coeff": 1},
        {"smiles": "O", "coeff": 1}
    ],
    "solvent": [
        {"smiles": "O", "coeff": None} 
    ]
}

print(reaction)