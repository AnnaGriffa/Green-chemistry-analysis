import streamlit as st
import streamlit.components.v1 as components
import math

from data.reactions import load_reactions
from utils.metrics import e_factor, atom_economy, solvent_toxicity
from utils.scoring import green_score
from utils.compare import rank_reactions
from utils.structures import render_equation
from data.principles import PRINCIPLE_FLAGS



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

.comparison-panel {
    background: transparent;
    border: none;
    border-radius: 22px;
    padding: 0;
    box-shadow: none;
    margin-bottom: 1.5rem;
    transition: none;
}
.comparison-panel:hover {
    transform: translateY(-3px);
    box-shadow: 0 18px 36px rgba(0,0,0,0.35);
}
/* METRIC CARDS */
.metric-grid {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    margin-top: 1rem;
    margin-bottom: 1.2rem;
}

.metric-vertical {
    flex: 1;
    background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 1rem;
    text-align: center;
    min-height: 360px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}

.metric-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #f0f6fc;
    margin-bottom: 0.5rem;
}

.metric-number {
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 0.3rem;
}

.metric-desc {
    font-size: 0.72rem;
    color: #d0d7de;
    margin-bottom: 1rem;
}

.bar-shell {
    width: 70px;
    height: 180px;
    margin: 0 auto;
    border-radius: 18px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    display: flex;
    align-items: flex-end;
    overflow: hidden;
    position: relative;
}

.bar-fill {
    width: 100%;
    border-radius: 18px;
    animation: growBar 2s ease forwards;
    height: 0;
}

.bar-blue {
    background: linear-gradient(180deg, #4ea8ff, #1f6feb);
}

.bar-green {
    background: linear-gradient(180deg, #7ee787, #238636);
}

.bar-orange {
    background: linear-gradient(180deg, #ffd166, #f59e0b);
}

.metric-badge {
    margin-top: 1rem;
    display: inline-block;
    padding: 0.4rem 0.9rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
}

.badge-excellent {
    background: rgba(46,160,67,0.15);
    color: #7ee787;
    border: 1px solid rgba(126,231,135,0.3);
}

.badge-good {
    background: rgba(78,168,255,0.15);
    color: #79c0ff;
    border: 1px solid rgba(121,192,255,0.3);
}

.badge-moderate {
    background: rgba(245,158,11,0.15);
    color: #ffd166;
    border: 1px solid rgba(255,209,102,0.3);
}

@keyframes growBar {
    from {
        height: 0;
    }
    to {
        height: var(--target-height);
    }
}

.metric-desc {
    font-size: 0.9rem;
    font-weight: 500;
    color: #d0d7de !important;
    margin-bottom: 1rem;
    line-height: 1.3;
}
}

.metric-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #f0f6fc !important;
    margin-bottom: 0.5rem;
}

.bar-pink {
    background: linear-gradient(180deg, #f778ba, #db61a2);
}

.score-card {
    background: linear-gradient(
        135deg,
        rgba(247,120,186,0.18),
        rgba(255,255,255,0.03)
    ) !important;

    border: 2.5px solid #f778ba !important;

    box-shadow:
        0 0 35px rgba(247,120,186,0.45),
        inset 0 0 20px rgba(247,120,186,0.12);

    border-radius: 20px;
    transform: scale(1.03);
}

.badge-score {
    background: rgba(247,120,186,0.22);
    color: #ffd6ea;
    border: 1px solid rgba(247,120,186,0.55);
    box-shadow: 0 0 12px rgba(247,120,186,0.2);
}
            
.metric-number {
    font-size: 2.15rem;
    font-weight: 800;
    margin-bottom: 0.3rem;
    color: white !important;
}        

.ranking-panel {
    background: linear-gradient(
        135deg,
        rgba(247,120,186,0.12),
        rgba(255,255,255,0.03)
    );

    border: 2px solid #f778ba;

    border-radius: 24px;
    padding: 1.6rem;
    margin: 1.2rem 0 2rem 0;

    box-shadow:
        0 0 35px rgba(247,120,186,0.35),
        inset 0 0 20px rgba(247,120,186,0.08);
}            

.ranking-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: white;
    margin-bottom: 1rem;
}

.ranking-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.65rem;
    font-size: 0.95rem;
    color: #d0d7de;
}

.ranking-score {
    color: #f778ba;
    font-weight: 800;
}
/* CHEMICAL EQUATION */
.equation-box {
    background: linear-gradient(
        135deg,
        rgba(19,50,28,0.95),
        rgba(35,90,50,0.65)
    );
    border: 1.5px solid rgba(126,231,135,0.45);
    border-radius: 24px;
    padding: 1.4rem;
    margin-top: 1rem;
    box-shadow:
        0 12px 30px rgba(0,0,0,0.22),
        inset 0 1px 0 rgba(255,255,255,0.06);
}

.equation-box img,
.equation-box svg {
    max-width: 100% !important;
    height: auto !important;
    display: block;
    margin: 0 auto;
}

.equation-title {
    font-size: 1rem;
    font-weight: 800;
    color: white;
    margin-bottom: 1rem;
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

def build_data(reaction):
    """Construit le dictionnaire de données d'affichage."""
    ef  = e_factor(reaction)
    ae  = atom_economy(reaction)
    st_ = solvent_toxicity(reaction)
    score = green_score(reaction)
    return {
        "score": {
            "value": score,
            "comment": "Overall sustainability score",
            "badge": "good" if score > 75 else "ok" if score > 50 else "warn",
            "badge_text": "Excellent" if score > 75 else "Moderate" if score > 50 else "Poor"
        },
        "efactor": {
            "value":      round(ef, 2),
            "comment":    "Waste per unit product",
            "badge":      "good" if ef < 5 else "ok" if ef < 15 else "warn",
            "badge_text": "Excellent" if ef < 5 else "Moderate" if ef < 15 else "Poor",
        },
        "atom_economy": {
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
       "principles": compute_principles(reaction, ef, ae, st_),
    }

def compute_principles(reaction, ef, ae, hz):
    principles = []

    flags = PRINCIPLE_FLAGS.get(reaction.name, {})
 
    # 1. Prevention of waste
    if ef < 10:
        principles.append(0)

    # 2. Atom economy
    if ae > 50:
        principles.append(1)

    # 3. Less hazardous syntheses
    if hz < 1.5:
        principles.append(2)

    # 4. Designing safer chemicals
    if hz < 1:
        principles.append(3)

    # 5. Safer solvents
    if hz < 2:
        principles.append(4)

    # 6. Energy efficiency
    if reaction.temperature <= 60:
        principles.append(5)

    # 7. Renewable feedstocks
    if flags.get("renewable_feedstocks", False):
        principles.append(6)

    # 8. Reduce derivatives
    if reaction.steps <= 2 and len(reaction.intermediates) <= 1:
        principles.append(7)

    # 9. Catalysis
    if flags.get("catalysis", False):
        principles.append(8)

    # 10. Design for degradation
    if flags.get("design_for_degradation", False):
        principles.append(9)

    # 11. Real-time analysis
    if flags.get("real_time_monitoring", False):
        principles.append(10)

    # 12. Accident prevention
    if flags.get("accident_prevention", False):
        principles.append(11)

    return principles

def render_principles(data):
    highlighted = set(data["principles"])

    items_html = ""

    for i, p in enumerate(PRINCIPLES):
        active = i in highlighted

        bg = "rgba(46,160,67,0.12)" if active else "rgba(255,255,255,0.03)"
        border = "#3fb950" if active else "rgba(255,255,255,0.06)"
        color = "#7ee787" if active else "#8b949e"
        icon = "✓" if active else "○"

        items_html += f"""
        <div style="
            padding:0.65rem 0.9rem;
            margin-bottom:0.45rem;
            border-radius:14px;
            background:{bg};
            border:1px solid {border};
            color:{color};
            font-size:0.82rem;
            font-weight:600;
        ">
            {icon} Principle {i+1}: {p}
        </div>
        """

    st.markdown(
        f"""
        <div style="
            background:linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
            border:1px solid rgba(255,255,255,0.08);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
            border-radius:20px;
            padding:1.2rem;
            margin-top:1rem;
        ">
            <div style="
                font-size:1rem;
                font-weight:800;
                color:white;
                margin-bottom:1rem;
            ">
                🌿 Green Chemistry Principles
            </div>

            {items_html}
        </div>
        """,
        unsafe_allow_html=True
    )

 
def render_metric_dashboard(data):
    ef = data["efactor"]["value"]
    ae = data["atom_economy"]["value"]
    hz = data["hazards"]["value"]
    score = data["score"]["value"]

    ef_height = min(max((ef / 50) * 100, 5), 100)
    ae_height = min(max(ae, 5), 100)
    hz_height = min(max((hz / 5) * 100, 5), 100)
    score_height = min(max(score, 5), 100)

    ef_badge = "Excellent" if ef < 5 else "Good" if ef < 15 else "Needs Improvement"
    ae_badge = "Excellent" if ae > 70 else "Good" if ae > 40 else "Moderate"
    hz_badge = "Low Risk" if hz < 1 else "Moderate" if hz < 3 else "High"
    score_badge = "Excellent" if score > 75 else "Good" if score > 50 else "Moderate"

    ef_class = "badge-excellent" if ef < 5 else "badge-good" if ef < 15 else "badge-moderate"
    ae_class = "badge-excellent" if ae > 70 else "badge-good" if ae > 40 else "badge-moderate"
    hz_class = "badge-excellent" if hz < 1 else "badge-good" if hz < 3 else "badge-moderate"

    html = f"""
    <style>
    html, body {{
        margin: 0;
        padding: 0;
        background: transparent !important;
        overflow: hidden;
    }}

    .metric-grid {{
        display: flex;
        gap: 1rem;
        width: 100%;
        padding: 0.5rem;
        box-sizing: border-box;
    }}

    .metric-vertical {{
        flex: 1;
        background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.015));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 1rem;
        text-align: center;
        min-height: 360px;
        color: white;
        box-sizing: border-box;
    }}

    .score-card {{
        background: linear-gradient(
            135deg,
            rgba(247,120,186,0.18),
            rgba(255,255,255,0.03)
        );
        border: 2px solid #f778ba;
        box-shadow:
            0 0 35px rgba(247,120,186,0.45),
            inset 0 0 20px rgba(247,120,186,0.12);
        transform: scale(1.02);
    }}

    .metric-title {{
        font-size: 0.95rem;
        font-weight: 800;
        color: white;
        margin-bottom: 0.5rem;
    }}

    .metric-number {{
        font-size: 2.15rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }}

    .metric-blue {{ color: #79c0ff; }}
    .metric-green {{ color: #7ee787; }}
    .metric-orange {{ color: #ffd166; }}

    .metric-pink {{
        color: #ff8ec8;
        text-shadow:
            0 0 10px rgba(247,120,186,0.45),
            0 0 20px rgba(247,120,186,0.25);
    }}

    .metric-desc {{
        font-size: 0.85rem;
        color: #d0d7de;
        min-height: 50px;
        line-height: 1.3;
    }}

    .bar-shell {{
        width: 70px;
        height: 180px;
        margin: 1rem auto;
        border-radius: 18px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        display: flex;
        align-items: flex-end;
        overflow: hidden;
    }}

    .bar-fill {{
        width: 100%;
        height: 0;
        border-radius: 18px;
        animation: growBar 1.8s ease forwards;
    }}

    .bar-blue {{ background: linear-gradient(180deg,#4ea8ff,#1f6feb); }}
    .bar-green {{ background: linear-gradient(180deg,#7ee787,#238636); }}
    .bar-orange {{ background: linear-gradient(180deg,#ffd166,#f59e0b); }}
    .bar-pink {{ background: linear-gradient(180deg,#f778ba,#db61a2); }}

    .metric-badge {{
        margin-top: 1rem;
        display: inline-block;
        padding: 0.4rem 0.9rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
    }}

    .badge-excellent {{
        background: rgba(46,160,67,0.15);
        color:#7ee787;
        border:1px solid rgba(126,231,135,0.3);
    }}

    .badge-good {{
        background: rgba(78,168,255,0.15);
        color:#79c0ff;
        border:1px solid rgba(121,192,255,0.3);
    }}

    .badge-moderate {{
        background: rgba(245,158,11,0.15);
        color:#ffd166;
        border:1px solid rgba(255,209,102,0.3);
    }}

    .badge-score {{
        background: rgba(247,120,186,0.22);
        color:#ffd6ea;
        border:1px solid rgba(247,120,186,0.55);
    }}

    @keyframes growBar {{
        from {{ height: 0; }}
        to {{ height: var(--target-height); }}
    }}
    </style>

    <div class="metric-grid">

        <div class="metric-vertical">
            <div class="metric-title">🌿 E-Factor</div>
            <div class="metric-number metric-blue">{ef}</div>
            <div class="metric-desc">Waste per unit product</div>
            <div class="bar-shell">
                <div class="bar-fill bar-blue" style="--target-height:{ef_height}%"></div>
            </div>
            <div class="metric-badge {ef_class}">{ef_badge}</div>
        </div>

        <div class="metric-vertical">
            <div class="metric-title">⚛ Atom Economy</div>
            <div class="metric-number metric-green">{ae}%</div>
            <div class="metric-desc">Mass efficiency indicator</div>
            <div class="bar-shell">
                <div class="bar-fill bar-green" style="--target-height:{ae_height}%"></div>
            </div>
            <div class="metric-badge {ae_class}">{ae_badge}</div>
        </div>

        <div class="metric-vertical">
            <div class="metric-title">⚠ Hazard Score</div>
            <div class="metric-number metric-orange">{hz}</div>
            <div class="metric-desc">Solvent hazard profile</div>
            <div class="bar-shell">
                <div class="bar-fill bar-orange" style="--target-height:{hz_height}%"></div>
            </div>
            <div class="metric-badge {hz_class}">{hz_badge}</div>
        </div>

        <div class="metric-vertical score-card">
            <div class="metric-title">🏆 Green Score</div>
            <div class="metric-number metric-pink">{score}</div>
            <div class="metric-desc">Overall sustainability score</div>
            <div class="bar-shell">
                <div class="bar-fill bar-pink" style="--target-height:{score_height}%"></div>
            </div>
            <div class="metric-badge badge-score">{score_badge}</div>
        </div>

    </div>
    """

    components.html(html, height=470, scrolling=False) 
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
st.markdown(
"<p style='color:#d0d7de;font-size:1rem;margin-top:0.35rem;font-weight:500;'>"
    "Compare multiple antihistamine synthesis pathways side by side"
    "</p>",
    unsafe_allow_html=True
)
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

if n > 1:
    ranking = rank_reactions(reactions)

    ranking_html = ""

    medals = ["🥇", "🥈", "🥉", "🏅"]

    for i, item in enumerate(ranking):
        ranking_html += f"""
        <div class='ranking-item'>
            {medals[i]} <strong>{item['name']}</strong>
            — Green Score:
            <span style="
                color:#ff8ec8;
                font-weight:900;
                text-shadow:0 0 12px rgba(247,120,186,0.45);
                padding:0.2rem 0.55rem;
                border:1px solid rgba(247,120,186,0.45);
                border-radius:999px;
                background:rgba(247,120,186,0.08);
            ">
                {item['score']}
            </span>
        </div>
        """

    st.markdown(
        f"""
        <div class='ranking-panel'>
            <div class='ranking-title'>🏆 Overall Sustainability Ranking</div>
            {ranking_html}
        </div>
        """,
        unsafe_allow_html=True
    )

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


# ── Bannières et métriques
for i, (col, reaction, data) in enumerate(zip(content_cols, reactions, datas)):
    with col:
        st.markdown("<div class='comparison-panel'>", unsafe_allow_html=True)

        st.markdown(
            f"<div class='selection-banner' "
            f"style='background:linear-gradient(135deg,#10243d,#0d1b2a);"
            f"border:1px solid {COLORS[i]};color:{COLORS[i]};"
            f"padding:0.9rem 1.3rem;font-size:1.05rem;border-radius:16px;'>"
            f"⚗ {reaction.name}</div>",
            unsafe_allow_html=True
        )

        render_metric_dashboard(data)

        st.markdown("</div>", unsafe_allow_html=True)


# ── Equations
for i, (col, reaction) in enumerate(zip(content_cols, reactions)):
    with col:
        equation_html = render_equation(reaction)

        total_species = len(reaction.reactants) + len(reaction.products)
        rows = math.ceil(total_species / 3)
        eq_height = 180 + rows * 120

        st.components.v1.html(
            f"""
            <html>
            <body style="
                margin:0;
                padding:0;
                background:transparent;
                overflow:hidden;
                font-family:Arial,sans-serif;
            ">

            <div style="
                background:linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
                border:1px solid rgba(255,255,255,0.08);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
                border-radius:20px;
                padding:1.2rem;
                width:100%;
                box-sizing:border-box;
            ">

                <div style="
                    font-size:1rem;
                    font-weight:800;
                    color:white;
                    margin-bottom:1rem;
                ">
                    🧪 Chemical Equation
                </div>

                {equation_html}

            </div>

            </body>
            </html>
            """,
            height=eq_height,
            scrolling=False
        )

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

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