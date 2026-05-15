
from __future__ import annotations
import streamlit as st
import pubchempy as pcp

# ── Names used in the code → PubChem names ─────────────────────────────────────
PUBCHEM_NAMES: dict[str, str] = {
    "benzhydrol":                                           "benzhydrol",
    "hydrochloric_acid":                                    "hydrochloric acid",
    "chlorodiphenylmethane":                                "chlorodiphenylmethane",
    "dimethylaminoethanol":                                 "2-dimethylaminoethanol",
    "diphenhydramine":                                      "diphenhydramine",
    "4-chlorobenzhydryl_chloride":                          "4-chlorobenzhydryl chloride",
    "n-carbethoxy_piperazine":                              "ethyl piperazine-1-carboxylate",
    "ethyl_4-(4-chlorobenzhydryl)piperazine-1-carboxylate": "ethyl 4-(4-chlorobenzhydryl)piperazine-1-carboxylate",
    "methyl_2-(2-chloroethoxy)acetate":                     "methyl 2-(2-chloroethoxy)acetate",
    "cetirizine":                                           "cetirizine",
    "2-(3-chlorophenyl)acetonitrile":                           "2-(3-chlorophenyl)acetonitrile",
    "ethyl_nicotinate":                                     "ethyl_nicotinate",
    "loratadine_intermediate":                              "8-chloro-6,11-dihydro-5H-benzo[5,6]cyclohepta[1,2-b]pyridin-11-one",
    "loratadine":                                           "loratadine",
    "ethanol":                                              "ethanol",
    "dichloromethane":                                      "dichloromethane",
    "toluene":                                              "toluene",
    "sodium_hydroxide":                                     "sodium hydroxide",
    "water":                                                "water",
}


KNOWN_CIDS: dict[str, int] = {
    "benzhydrol":                                           91526,
    "hydrochloric_acid":                                    313,
    "chlorodiphenylmethane":                                11756,
    "dimethylaminoethanol":                                 7767,
    "diphenhydramine":                                      3989,
    "4-chlorobenzhydryl_chloride":                          12673,
    "n-carbethoxy_piperazine":                              68141,
    "ethyl_4-(4-chlorobenzhydryl)piperazine-1-carboxylate": 2723949,
    "methyl_2-(2-chloroethoxy)acetate":                     522258,
    "cetirizine":                                           2678,
    "2-(3-chlorophenyl)acetonitrile":                       73722,
    "ethyl_nicotinate":                                     69188,
    "loratadine":                                           3957,
    "ethanol":                                              702,
    "dichloromethane":                                      6344,
    "toluene":                                              1140,
    "sodium_hydroxide":                                     14798,
    "water":                                                962,
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