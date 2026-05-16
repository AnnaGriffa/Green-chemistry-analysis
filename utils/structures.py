
from __future__ import annotations
import streamlit as st
import pubchempy as pcp

# ── Names used in the code → PubChem names ─────────────────────────────────────

PUBCHEM_NAMES: dict[str, str] = {
    # Diphenhydramine
    "benzhydrol": "benzhydrol",
    "hydrochloric_acid": "hydrochloric acid",
    "dimethylaminoethanol": "2-dimethylaminoethanol",
    "diphenhydramine": "diphenhydramine",

    # Cetirizine
    "4-chlorobenzhydryl_chloride": "4-chlorobenzhydryl chloride",
    "n-carbethoxy_piperazine": "ethyl piperazine-1-carboxylate",
    "methyl_2-(2-chloroethoxy)acetate": "methyl 2-(2-chloroethoxy)acetate",
    "cetirizine": "cetirizine",

    # Loratadine
    "2-(4-chlorobenzyl)acetonitrile": "2-(4-chlorobenzyl)acetonitrile",
    "ethyl_nicotinate": "ethyl nicotinate",
    "loratadine": "loratadine",

    # Brompheniramine
    "2-bromopyridine": "2-bromopyridine",
    "4-bromobenzyl_bromide": "4-bromobenzyl bromide",
    "dimethylaminoethyl_chloride": "2-chloro-N,N-dimethylethylamine",
    "brompheniramine": "brompheniramine",

    # Chlorpheniramine
    "4-chlorophenylacetonitrile": "4-chlorophenylacetonitrile",
    "2-chloropyridine": "2-chloropyridine",
    "chlorpheniramine": "chlorpheniramine",

    # Carbinoxamine
    "pyridine": "pyridine",
    "dimethylaminoethyl_chloride_hcl": "2-dimethylaminoethyl chloride hydrochloride",
    "carbinoxamine": "carbinoxamine",

    # Triprolidine
    "4-methylbenzophenone": "4-methylbenzophenone",
    "formaldehyde": "formaldehyde",
    "pyrrolidine": "pyrrolidine",
    "triprolidine": "triprolidine",

    # Doxylamine
    "methylbenzyl_ketone": "1-phenyl-2-propanone",
    "doxylamine": "doxylamine",

    # Promethazine
    "phenothiazine": "phenothiazine",
    "dimethylaminopropyl_chloride": "3-dimethylaminopropyl chloride",
    "promethazine": "promethazine",

    # Cyclizine
    "n-methyl_piperazine": "1-methylpiperazine",
    "cyclizine": "cyclizine",

    # Hydroxyzine
    "hydroxyzine_precursor": "cetirizine",
    "2-(2-chloroethoxy)ethanol": "2-(2-chloroethoxy)ethanol",
    "hydroxyzine": "hydroxyzine",

    # Dimenhydrinate
    "diphenhydramine_salt_partner": "8-chlorotheophylline",
    "dimenhydrinate": "dimenhydrinate",

    # Desloratadine
    "desloratadine_precursor": "loratadine",
    "methanol": "methanol",
    "desloratadine": "desloratadine",

    # Meclizine
    "meclizine_precursor": "piperazine",
    "m_tolualdehyde": "m-tolualdehyde",
    "meclizine": "meclizine",

    # Fexofenadine
    "fexofenadine_intermediate_1": "4-bromobutyrophenone",
    "azacyclonol": "azacyclonol",
    "fexofenadine": "fexofenadine",

    # Levocetirizine
    "levocetirizine": "levocetirizine",

    # Rupatadine
    "desloratadine_acid": "desloratadine",
    "rupatadine_precursor": "rupatadine",
    "rupatadine": "rupatadine",

    # Solvents
    "ethanol": "ethanol",
    "dichloromethane": "dichloromethane",
    "toluene": "toluene",
    "water": "water",
}

KNOWN_CIDS: dict[str, int] = {
    # Diphenhydramine
    "benzhydrol": 7037,
    "hydrochloric_acid": 313,
    "dimethylaminoethanol": 7767,
    "diphenhydramine": 3989,

    # Cetirizine
    "4-chlorobenzhydryl_chloride": 12673,
    "n-carbethoxy_piperazine": 68141,
    "methyl_2-(2-chloroethoxy)acetate": 522258,
    "cetirizine": 2678,

    # Loratadine
    "2-(4-chlorobenzyl)acetonitrile": 73722,
    "ethyl_nicotinate": 69188,
    "loratadine": 3957,

    # Brompheniramine
    "2-bromopyridine": 7969,
    "4-bromobenzyl_bromide": 78017,
    "dimethylaminoethyl_chloride": 10966,
    "brompheniramine": 2559,

    # Chlorpheniramine
    "4-chlorophenylacetonitrile": 22172,
    "2-chloropyridine": 11254,
    "chlorpheniramine": 2725,

    # Carbinoxamine
    "pyridine": 1049,
    "dimethylaminoethyl_chloride_hcl": 13840,
    "carbinoxamine": 2745,

    # Triprolidine
    "4-methylbenzophenone": 7408,
    "formaldehyde": 712,
    "pyrrolidine": 31268,
    "triprolidine": 5568,

    # Doxylamine
    "methylbenzyl_ketone": 7678,
    "doxylamine": 8113,

    # Promethazine
    "phenothiazine": 4760,
    "dimethylaminopropyl_chloride": 17156,
    "promethazine": 4927,

    # Cyclizine
    "n-methyl_piperazine": 6329,
    "cyclizine": 6726,

    # Hydroxyzine
    "2-(2-chloroethoxy)ethanol": 81773,
    "hydroxyzine": 3658,

    # Dimenhydrinate
    "dimenhydrinate": 3047,

    # Desloratadine
    "methanol": 887,
    "desloratadine": 124087,

    # Meclizine
    "m_tolualdehyde": 7410,
    "meclizine": 4168,

    # Fexofenadine
    "azacyclonol": 15461,
    "fexofenadine": 3348,

    # Levocetirizine
    "levocetirizine": 1549008,

    # Rupatadine
    "rupatadine": 133124,

    # Solvents
    "ethanol": 702,
    "dichloromethane": 6344,
    "toluene": 1140,
    "water": 962,
}


@st.cache_data(ttl=86400)
def get_cid(internal_name: str) -> int | None:
    # 1. Vérifier d'abord les CID hardcodés — toujours fiable
    if internal_name in KNOWN_CIDS:
        return KNOWN_CIDS[internal_name]
    # 2. Fallback : chercher via l'API PubChem
    pubchem_name = PUBCHEM_NAMES.get(internal_name, internal_name.replace("_", " "))
    try:
        results = pcp.get_compounds(pubchem_name, "name")
        if results:
            return results[0].cid
        return None
    except Exception as e:
        print(f"[DEBUG] PubChem error for {internal_name!r}: {e}")
        return None


@st.cache_data(ttl=86400)
def get_structure_url(internal_name: str) -> str | None:
    cid = get_cid(internal_name)
    if cid:
        # SVG = meilleur rendu, fond transparent
        return (
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}"
            f"/PNG?image_size=300x300&record_type=2d"
        )
    return None


def build_equation_elements(reactants: list[str], products: list[str]) -> list[dict]:
    """
    Construit la liste ordonnée des éléments de l'équation.
    Chaque élément est un dict avec type 'compound' ou 'symbol'.
    """
    elements = []
    for i, name in enumerate(reactants):
        elements.append({"type": "compound", "name": name, "role": "reactant"})
        if i < len(reactants) - 1:
            elements.append({"type": "symbol", "text": "+"})
    elements.append({"type": "symbol", "text": "→"})
    for i, name in enumerate(products):
        elements.append({"type": "compound", "name": name, "role": "product"})
        if i < len(products) - 1:
            elements.append({"type": "symbol", "text": "+"})
    return elements


def render_equation(reaction) -> None:
    """
    Affiche l'équation chimique avec les structures PNG de PubChem.
    Utilise du HTML/CSS flexbox pour éviter les colonnes imbriquées Streamlit.
    """
    elements = build_equation_elements(
        [sp.name for sp in reaction.reactants],
        [sp.name for sp in reaction.products],
    )

    items_html = ""
    for el in elements:
        if el["type"] == "symbol":
            color = "#3fb950" if el["text"] == "→" else "#6e7681"
            items_html += (
                f'<div style="display:flex;align-items:center;'
                f'font-size:1.6rem;color:{color};font-weight:700;'
                f'padding:0 0.3rem;">{el["text"]}</div>'
            )
        else:
            name_color = "#79c0ff" if el["role"] == "reactant" else "#7ee8a2"
            display_name = el["name"].replace("_", " ").replace("-", "‑")
            url = get_structure_url(el["name"])

            if url:
                img_html = (
                    f'<img src="{url}" style="width:100px;height:100px;'
                    f'object-fit:contain;border-radius:8px;'
                    f'background:#f0f0f0;padding:6px;'  # ← fond gris clair
                    f'border:1px solid #ddd;"/>'
                )
                
            else:
                img_html = (
                    '<div style="width:100px;height:100px;background:#21262d;'
                    'border-radius:8px;display:flex;align-items:center;'
                    'justify-content:center;color:#6e7681;font-size:0.7rem;">'
                    '⚠️ not found</div>'
                )

            items_html += (
                f'<div style="display:flex;flex-direction:column;'
                f'align-items:center;gap:0.4rem;">'
                f'{img_html}'
                f'<span style="font-size:0.7rem;color:{name_color};'
                f'font-weight:600;text-align:center;max-width:110px;'
                f'line-height:1.3;">{display_name}</span>'
                f'</div>'
            )

    st.markdown(
        f'<div style="display:flex;flex-wrap:wrap;align-items:center;'
        f'justify-content:center;gap:0.5rem;padding:0.5rem 0;">'
        f'{items_html}</div>',
        unsafe_allow_html=True,
    )