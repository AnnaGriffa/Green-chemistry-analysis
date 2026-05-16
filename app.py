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
.stApp { background-color: #426e4a; }
.block-container { padding: 2rem 2.5rem 3rem; max-width: 1400px; }
#MainMenu, footer, header { visibility: hidden; }

/* HOME */
.home-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 72vh; text-align: center; padding: 2rem 1rem; }
.home-icon { font-size: 4rem; margin-bottom: 1.2rem; filter: drop-shadow(0 0 24px rgba(63,185,80,0.4)); }
.home-title { font-size: 3.4rem; font-weight: 800; color: #ffffff; letter-spacing: -0.03em; line-height: 1.1; margin-bottom: 0.8rem; }
.home-accent { color: #3fb950; }
.home-subtitle { font-size: 1rem; color: #0b4021; max-width: 460px; line-height: 1.7; margin-bottom: 2.8rem; }
.home-select-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.14em; color: #3fb950; font-weight: 700; margin-bottom: 0.4rem; text-align: left; }
.home-divider { width: 60px; height: 3px; background: linear-gradient(90deg, #3fb950, #238636); border-radius: 999px; margin: 0 auto 2.5rem; }

/* ANALYSIS */
.main-title { font-size: 2.6rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em; line-height: 1.1; }
.title-accent { color: #3fb950; }
.selection-banner { border-radius: 12px; padding: 0.7rem 1.2rem; font-size: 0.95rem; font-weight: 600; display: inline-block; margin-bottom: 0.5rem; }

/* Metric cards */
.metric-card { border-radius: 16px; padding: 1.2rem 0.8rem; text-align: center; height: 100%; }
.metric-card.efactor { background: linear-gradient(160deg, #7a6a1e 0%, #5c4f14 100%); border: 1px solid #a08c28; }
.metric-card.pmi     { background: linear-gradient(160deg, #5a3e7a 0%, #3d2857 100%); border: 1px solid #7b57a8; }
.metric-card.hazards { background: linear-gradient(160deg, #6e3f3f 0%, #4e2b2b 100%); border: 1px solid #9e5555; }
.metric-label { font-size: 0.75rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; opacity: 0.75; margin-bottom: 0.3rem; }
.metric-value { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 700; color: #ffffff; line-height: 1; margin-bottom: 0.4rem; }
.metric-comment { font-size: 0.72rem; opacity: 0.7; line-height: 1.4; }
.metric-badge { display: inline-block; border-radius: 999px; padding: 0.2rem 0.6rem; font-size: 0.65rem; font-weight: 700; margin-top: 0.4rem; letter-spacing: 0.05em; text-transform: uppercase; }
.badge-good { background: #1a4731; color: #3fb950; }
.badge-ok   { background: #3d3214; color: #d4a017; }
.badge-warn { background: #4e1e1e; color: #f85149; }

/* Hazard list */
.hazard-list { margin-top: 0.8rem; display: flex; flex-direction: column; gap: 0.3rem; text-align: left; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 0.7rem; }
.hazard-item { display: flex; align-items: flex-start; gap: 0.5rem; font-size: 0.72rem; color: rgba(255,255,255,0.75); line-height: 1.3; }
.hazard-code { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; font-weight: 700; background: rgba(0,0,0,0.3); border-radius: 4px; padding: 0.1rem 0.35rem; white-space: nowrap; color: #ffa657; margin-top: 0.05rem; }

/* Principles */
.principles-card { background: linear-gradient(160deg, #1a3d2b 0%, #132d1f 100%); border: 1px solid #2d6a42; border-radius: 16px; padding: 1.2rem 1.4rem; }
.principles-title { font-size: 0.95rem; font-weight: 700; color: #7ee8a2; margin-bottom: 0.8rem; }
.principle-item { display: flex; align-items: flex-start; gap: 0.5rem; padding: 0.25rem 0; font-size: 0.75rem; color: #cde8d5; border-bottom: 1px solid rgba(255,255,255,0.05); }
.principle-item:last-child { border-bottom: none; }
.principle-num { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #3fb950; font-weight: 700; min-width: 1.4rem; margin-top: 1px; }
.principle-highlighted { color: #7ee8a2; font-weight: 600; }

/* Equation */
.equation-card { background: #2e6d7d; border: 1px solid #1e5c6e; border-radius: 16px; padding: 1.4rem 1.2rem 1.6rem; font-family: 'JetBrains Mono', monospace; }
.equation-title { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.12em; color: #d0eef5; margin-bottom: 1rem; font-weight: 600; text-align: center; }

/* Buttons */
.stButton > button { background: linear-gradient(135deg, #238636, #1a6e2e) !important; color: white !important; border: 1px solid #2ea043 !important; border-radius: 10px !important; font-family: 'Sora', sans-serif !important; font-weight: 700 !important; font-size: 0.9rem !important; padding: 0.6rem 1.6rem !important; letter-spacing: 0.03em !important; transition: all 0.2s ease !important; }
.stButton > button:hover { background: linear-gradient(135deg, #2ea043, #238636) !important; transform: translateY(-1px) !important; box-shadow: 0 4px 16px rgba(46,160,67,0.3) !important; }
.stSelectbox > div > div { background-color: #21262d !important; border: 1px solid #30363d !important; border-radius: 10px !important; color: #e6edf3 !important; font-family: 'Sora', sans-serif !important; }
.stRadio > div { gap: 1rem; }
.section-divider { border: none; border-top: 1px solid #21262d; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Data ─────────────────────────────────────────────────────────────────────────
REACTIONS = load_reactions()

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
            Select reactions to compare their green chemistry profiles side by side.
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, col_center, _ = st.columns([1.2, 2, 1.2])
    with col_center:
        reaction_names = list(REACTIONS.keys())

        st.markdown('<div class="home-select-label">Number of reactions to compare</div>', unsafe_allow_html=True)
        n_reactions = st.radio(
            "n", [2, 3, 4],
            horizontal=True,
            label_visibility="collapsed",
            key="n_reactions",
        )

        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

        choices = []
        for i in range(n_reactions):
            st.markdown(f'<div class="home-select-label">Reaction {i + 1}</div>', unsafe_allow_html=True)
            choice = st.selectbox(
                f"reaction{i}",
                reaction_names,
                index=i if i < len(reaction_names) else 0,
                label_visibility="collapsed",
                key=f"home_select_{i}",
            )
            choices.append(choice)
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        has_duplicates = len(choices) != len(set(choices))
        if has_duplicates:
            st.markdown(
                "<div style='color:#f85149;font-size:0.8rem;text-align:center;'>"
                "⚠️ Please select different reactions.</div>",
                unsafe_allow_html=True
            )

        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

        if st.button("🔬 Compare Reactions", use_container_width=True, disabled=has_duplicates):
            st.session_state.selected_reactions = choices
            st.session_state.page = "analysis"
            st.rerun()

    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)
    st.markdown(FOOTER, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS SCREEN
# ══════════════════════════════════════════════════════════════════════════════
selected  = st.session_state.selected_reactions
reactions = [REACTIONS[name] for name in selected]
datas     = [build_data(r) for r in reactions]
n         = len(reactions)

# Header
st.markdown('<div class="main-title">Green Chemistry <span class="title-accent">Comparison</span></div>', unsafe_allow_html=True)
st.markdown("<p style='color:#6e7681;font-size:0.85rem;margin-top:0.3rem;'>Side-by-side green chemistry analysis</p>", unsafe_allow_html=True)
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# Colonnes dynamiques
col_widths = []
for i in range(n):
    col_widths.append(10)
    if i < n - 1:
        col_widths.append(0.3)

cols = st.columns(col_widths, gap="small")
content_cols = [cols[i * 2] for i in range(n)]
divider_cols = [cols[i * 2 + 1] for i in range(n - 1)]

# Séparateurs verticaux
for col in divider_cols:
    with col:
        st.markdown(
            "<div style='border-left:1px solid #21262d;height:100%;"
            "min-height:800px;margin:auto;width:1px;'></div>",
            unsafe_allow_html=True
        )

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

if st.button("🔄  Compare Another Set"):
    st.session_state.page = "home"
    st.rerun()

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
st.markdown(FOOTER, unsafe_allow_html=True)