import streamlit as st
from data.reactions import load_reactions
from utils.metrics import e_factor, atom_economy, solvent_toxicity
from utils.scoring import green_score
from utils.structures import render_equation

# ── Page config ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Green Chemistry Analysis",
    page_icon="🌿",
    layout="wide",
)

# ── Session state ────────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None
if "selected_reactions" not in st.session_state:
    st.session_state.selected_reactions = []

# ── Custom CSS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
    background-color: #0d1117;
    color: #e6edf3;
}

.stApp {
    background-color: #426e4a;
}

.block-container {
    padding: 2rem 2.5rem 3rem;
    max-width: 1400px;
}

#MainMenu, footer, header {
    visibility: hidden;
}

/* HOME */
.home-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 72vh;
    text-align: center;
    padding: 2rem 1rem;
}

.home-icon {
    font-size: 4rem;
    margin-bottom: 1.2rem;
}

.home-title {
    font-size: 3.4rem;
    font-weight: 800;
    color: white;
}

.home-accent {
    color: #3fb950;
}

.home-subtitle {
    font-size: 1rem;
    color: #cde8d5;
}

.home-divider {
    width: 60px;
    height: 3px;
    background: linear-gradient(90deg, #3fb950, #238636);
    border-radius: 999px;
    margin: 1rem auto 2rem;
}

/* ANALYSIS */
.main-title {
    font-size: 2.6rem;
    font-weight: 800;
    color: white;
}

.title-accent {
    color: #3fb950;
}

.selection-banner {
    border-radius: 12px;
    padding: 0.7rem 1.2rem;
    font-size: 0.95rem;
    font-weight: 600;
    display: inline-block;
}

/* CATEGORY */
.category-card {
    background: linear-gradient(160deg, #1b2a20 0%, #132019 100%);
    border: 1px solid #2d6a42;
    border-radius: 18px;
    padding: 2rem 1rem;
    text-align: center;
    min-height: 220px;
}

.category-icon {
    font-size: 2.8rem;
    margin-bottom: 0.8rem;
}

.category-title {
    font-size: 1rem;
    font-weight: 700;
    color: white;
}

.category-count {
    font-size: 0.8rem;
    color: #7ee8a2;
}

.section-divider {
    border: none;
    border-top: 1px solid #21262d;
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)
# ── Data ─────────────────────────────────────────────────────────────────────────
REACTIONS = load_reactions()

CATEGORY_LABELS = {
    "nighttime_sleep": "Nighttime Sleep",
    "seasonal_allergies": "Seasonal Allergies",
    "cold_flu_symptoms": "Cold & Flu Symptoms",
    "motion_sickness_nausea": "Motion Sickness & Nausea",
    "skin_allergies_hives": "Skin Allergies & Hives",
}

CATEGORY_ICONS = {
    "nighttime_sleep": "🌙",
    "seasonal_allergies": "🌼",
    "cold_flu_symptoms": "🤧",
    "motion_sickness_nausea": "🚢",
    "skin_allergies_hives": "🩹",
}

CATEGORIES = {}
for name, reaction in REACTIONS.items():
    cat = reaction.category
    if cat not in CATEGORIES:
        CATEGORIES[cat] = []
    CATEGORIES[cat].append(name)

PRINCIPLES = [
    "Prevention of waste",
    "Atom economy",
    "Less hazardous chemical syntheses",
    "Designing safer chemicals",
    "Safer solvents and reaction conditions",
    "Design for energy efficiency",
    "Use of renewable feedstocks",
    "Reduce derivatives",
    "Catalysis",
    "Design for degradation",
    "Real-time analysis for pollution prevention",
    "Inherently safer chemistry for accident prevention",
]

COLORS = ["#79c0ff", "#7ee8a2", "#ffa657", "#f778ba"]

FOOTER = """
<div style='text-align:center;font-size:0.99rem;color:#3d444d;letter-spacing:0.05em;'>
    GREEN CHEMISTRY ANALYSIS TOOL &nbsp;·&nbsp; Based on the 12 Principles of Green Chemistry (Anastas & Warner, 1998)
</div>
"""

# ── Fonctions utilitaires ─────────────────────────────────────────────────────────

def render_metric(css_class, label, metric_data):
    """Affiche une carte métrique — appelée dans le contexte de colonne actif."""
    hazard_html = ""
    if "list" in metric_data and metric_data["list"]:
        items = "".join(
            f'<div class="hazard-item"><span class="hazard-code">{h["code"]}</span>{h["label"]}</div>'
            for h in metric_data["list"]
        )
        hazard_html = f'<div class="hazard-list">{items}</div>'
    st.markdown(
        f'<div class="metric-card {css_class}">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{metric_data["value"]}</div>'
        f'<div class="metric-comment">{metric_data["comment"]}</div>'
        f'<div class="metric-badge badge-{metric_data["badge"]}">{metric_data["badge_text"]}</div>'
        f'{hazard_html}</div>',
        unsafe_allow_html=True
    )

def build_data(reaction):
    """Construit le dictionnaire de données d'affichage."""
    ef  = e_factor(reaction)
    ae  = atom_economy(reaction)
    st_ = solvent_toxicity(reaction)
    return {
        "efactor": {
            "value":      round(ef, 2),
            "comment":    "Waste per unit product",
            "badge":      "good" if ef < 5 else "ok" if ef < 15 else "warn",
            "badge_text": "Excellent" if ef < 5 else "Moderate" if ef < 15 else "Poor",
        },
        "pmi": {
            "value":      round(ae, 2),
            "comment":    "Mass efficiency indicator",
            "badge":      "good" if ae > 70 else "ok" if ae > 40 else "warn",
            "badge_text": "Excellent" if ae > 70 else "Moderate" if ae > 40 else "Poor",
        },
        "hazards": {
            "value":      round(st_, 1),
            "comment":    "Solvent hazard profile",
            "badge":      "good" if st_ < 1 else "ok" if st_ < 3 else "warn",
            "badge_text": "Low" if st_ < 1 else "Moderate" if st_ < 3 else "High",
            "list":       [],
        },
        "principles": getattr(reaction, "principles", [0, 1, 4, 5]),
    }

def render_principles(data):
    """Affiche le bloc des 12 principes."""
    highlighted = set(data["principles"])
    items_html = ""
    for i, p in enumerate(PRINCIPLES):
        css = "principle-highlighted" if i in highlighted else ""
        dot = "✔️" if i in highlighted else "•"
        items_html += f'<div class="principle-item"><span class="principle-num">{i+1:02d}</span><span class="{css}">{dot} {p}</span></div>'
    st.markdown(
        f'<div class="principles-card">'
        f'<div class="principles-title">📋 12 Principles of Green Chemistry</div>'
        f'{items_html}</div>',
        unsafe_allow_html=True
    )

# ══════════════════════════════════════════════════════════════════════════════
# HOME SCREEN
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "home":

    st.markdown("""
    <div class="home-wrapper">
        <div class="home-icon">🌿</div>
        <div class="home-title">Green Chemistry<br><span class="home-accent">Analysis Tool</span></div>
        <div class="home-divider"></div>
        <div class="home-subtitle">
            Select an antihistamine category to begin analysis.
        </div>
    </div>
    """, unsafe_allow_html=True)

    categories = list(CATEGORIES.keys())
    top = st.columns(3)
    bottom = st.columns(2)

    for i, cat in enumerate(categories[:3]):
        with top[i]:
            st.markdown(
                f"""
                <div class="category-card">
                    <div class="category-icon">{CATEGORY_ICONS[cat]}</div>
                    <div class="category-title">{CATEGORY_LABELS[cat]}</div>
                    <div class="category-count">{len(CATEGORIES[cat])} antihistamines</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"Choose {CATEGORY_LABELS[cat]}", key=f"cat_{cat}", use_container_width=True):
                st.session_state.selected_category = cat
                st.session_state.selected_reactions = []
                st.session_state.page = "analysis"
                st.rerun()

    for i, cat in enumerate(categories[3:]):
        with bottom[i]:
            st.markdown(
                f"""
                <div class="category-card">
                    <div class="category-icon">{CATEGORY_ICONS[cat]}</div>
                    <div class="category-title">{CATEGORY_LABELS[cat]}</div>
                    <div class="category-count">{len(CATEGORIES[cat])} antihistamines</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"Choose {CATEGORY_LABELS[cat]}", key=f"cat2_{cat}", use_container_width=True):
                st.session_state.selected_category = cat
                st.session_state.selected_reactions = []
                st.session_state.page = "analysis"
                st.rerun()

    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)
    st.markdown(FOOTER, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS SCREEN
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.selected_category is None:
    st.session_state.page = "home"
    st.rerun()

category = st.session_state.selected_category
available_reactions = [
    r for r in CATEGORIES[category]
    if r not in st.session_state.selected_reactions
]

if len(st.session_state.selected_reactions) < 4 and available_reactions:
    chosen = st.selectbox(
        "Select antihistamine",
        available_reactions,
        key="reaction_picker"
    )
    if st.button("➕ Add Antihistamine"):
        st.session_state.selected_reactions.append(chosen)
        st.rerun()

selected = st.session_state.selected_reactions
reactions = [REACTIONS[name] for name in selected]
datas = [build_data(r) for r in reactions]
n = len(reactions)

# Header
st.markdown('<div class="main-title">Green Chemistry <span class="title-accent">Comparison</span></div>', unsafe_allow_html=True)
st.markdown("<p style='color:#6e7681;font-size:0.85rem;margin-top:0.3rem;'>Side-by-side green chemistry analysis</p>", unsafe_allow_html=True)
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# Colonnes dynamiques
content_cols = []

if n == 1:
    content_cols = [st.container()]

elif n == 2:
    content_cols = st.columns(2)

elif n == 3:
    row1 = st.columns(2)
    row2 = st.columns(1)
    content_cols = [row1[0], row1[1], row2[0]]

elif n == 4:
    row1 = st.columns(2)
    row2 = st.columns(2)
    content_cols = [row1[0], row1[1], row2[0], row2[1]]


# ── Bannières
for i, (col, reaction) in enumerate(zip(content_cols, reactions)):
    with col:
        st.markdown(
            f"<div class='selection-banner' style='background:linear-gradient(135deg,#1e3a5f,#163356);"
            f"border:1px solid {COLORS[i]};color:{COLORS[i]};'>"
            f"🔬 {reaction.name}</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

# ── Métriques
for i, (col, data) in enumerate(zip(content_cols, datas)):
    with col:
        if n <= 2:
            mc1, mc2, mc3 = st.columns(3)
            with mc1: render_metric("efactor", "E-Factor", data["efactor"])
            with mc2: render_metric("pmi",     "PMI",      data["pmi"])
            with mc3: render_metric("hazards", "Hazards",  data["hazards"])
        else:
            render_metric("efactor", "E-Factor", data["efactor"])
            st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
            render_metric("pmi",     "PMI",      data["pmi"])
            st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
            render_metric("hazards", "Hazards",  data["hazards"])
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Equations
for i, (col, reaction) in enumerate(zip(content_cols, reactions)):
    with col:
        st.markdown(
            "<div class='equation-card'>"
            "<div class='equation-title'>Chemical Equation</div>",
            unsafe_allow_html=True
        )
        render_equation(reaction)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Principes
for i, (col, data) in enumerate(zip(content_cols, datas)):
    with col:
        render_principles(data)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    if st.button("🔄 Change Category"):
        st.session_state.page = "home"
        st.session_state.selected_reactions = []
        st.session_state.selected_category = None
        st.rerun()

with c2:
    if st.button("🗑 Clear Analysis"):
        st.session_state.selected_reactions = []
        st.rerun()

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
st.markdown(FOOTER, unsafe_allow_html=True)