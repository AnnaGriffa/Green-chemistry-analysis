from __future__ import annotations
import streamlit as st
import pubchempy as pcp

# ── Internal name → PubChem name correspondence ────────────────────────────────────
# The names in reactions.json use underscores and abbreviations
# that PubChem may not necessarily recognize. We map here to IUPAC/common names.

PUBCHEM_NAMES: dict[str, str] = {
    "benzhydrol":                                       "benzhydrol",
    "hydrochloric_acid":                                "hydrochloric acid",
    "chlorodiphenylmethane":                            "chlorodiphenylmethane",
    "dimethylaminoethanol":                             "2-dimethylaminoethanol",
    "diphenhydramine":                                  "diphenhydramine",
    "4-chlorobenzhydryl_chloride":                      "4-chlorobenzhydryl chloride",
    "n-carbethoxy_piperazine":                          "ethyl piperazine-1-carboxylate",
    "ethyl_4-(4-chlorobenzhydryl)piperazine-1-carboxylate": "ethyl 4-(4-chlorobenzhydryl)piperazine-1-carboxylate",
    "methyl_2-(2-chloroethoxy)acetate":                 "methyl 2-(2-chloroethoxy)acetate",
    "cetirizine":                                       "cetirizine",
    "m-chlorophenylacetonitrile":                       "2-(3-chlorophenyl)acetonitrile",
    "ethyl_nicotinate":                                 "ethyl nicotinate",
    "loratadine_intermediate":                          "8-chloro-6,11-dihydro-5H-benzo[5,6]cyclohepta[1,2-b]pyridin-11-one",
    "loratadine":                                       "loratadine",
    "ethanol":                                          "ethanol",
    "dichloromethane":                                  "dichloromethane",
    "toluene":                                          "toluene",
    "sodium_hydroxide":                                 "sodium hydroxide",
    "water":                                            "water",
}


@st.cache_data(ttl=86400)  
def get_cid(internal_name: str) -> int | None:
    """Returns the PubChem CID for an internal name."""
    pubchem_name = PUBCHEM_NAMES.get(internal_name, internal_name.replace("_", " "))
    try:
        results = pcp.get_compounds(pubchem_name, "name")
        if results:
            return results[0].cid
        return None
    except Exception:
        return None


@st.cache_data(ttl=86400)
def get_structure_url(internal_name: str, size: int = 200) -> str | None:
    """Returns the URL of the PNG image of the PubChem structure."""
    cid = get_cid(internal_name)
    if cid:
        return (
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}"
            f"/PNG?image_size={size}x{size}"
        )
    return None


def render_equation(reaction) -> None:
    """
    Displays the chemical equation with PubChem PNG structures.
    Takes a Reaction object (dataclass from reactions.py).

    Displays: reactants → products
    Intermediates and solvents are not displayed in the equation.
    """

    # Build the ordered list of elements to display
    elements = []

    for i, sp in enumerate(reaction.reactants):
        elements.append({"type": "compound", "name": sp.name, "role": "reactant"})
        if i < len(reaction.reactants) - 1:
            elements.append({"type": "symbol", "text": "+"})

    elements.append({"type": "symbol", "text": "→"})

    for i, sp in enumerate(reaction.products):
        elements.append({"type": "compound", "name": sp.name, "role": "product"})
        if i < len(reaction.products) - 1:
            elements.append({"type": "symbol", "text": "+"})

    # Column widths proportional to the type
    col_widths = []
    for el in elements:
        if el["type"] == "compound":
            col_widths.append(2)
        elif el["text"] == "→":
            col_widths.append(0.8)
        else:
            col_widths.append(0.4)

    cols = st.columns(col_widths)

    for col, el in zip(cols, elements):
        with col:
            if el["type"] == "symbol":
                color = "#3fb950" if el["text"] == "→" else "#6e7681"
                st.markdown(
                    f"<div style='text-align:center; font-size:1.6rem; "
                    f"color:{color}; padding-top:2.8rem; font-weight:700;'>"
                    f"{el['text']}</div>",
                    unsafe_allow_html=True,
                )
            else:
                name_color = "#79c0ff" if el["role"] == "reactant" else "#7ee8a2"
                display_name = el["name"].replace("_", " ").replace("-", "‑")

                url = get_structure_url(el["name"])
                if url:
                    st.image(url, use_container_width=True)
                else:
                    st.markdown(
                        "<div style='height:120px; background:#21262d; "
                        "border-radius:8px; display:flex; align-items:center; "
                        "justify-content:center; color:#6e7681; font-size:0.72rem;'>"
                        "⚠️ not found</div>",
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    f"<div style='text-align:center; font-size:0.72rem; "
                    f"color:{name_color}; margin-top:0.3rem; font-weight:600; "
                    f"line-height:1.3;'>{display_name}</div>",
                    unsafe_allow_html=True,
                )