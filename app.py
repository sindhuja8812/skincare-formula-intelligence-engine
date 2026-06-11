"""
app.py — Skincare Formula Intelligence Engine
Main Streamlit application entry point.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

# ── Backend utility imports ──────────────────────────────────────────────────
from utils.knowledge_loader import load_knowledge_base, find_ingredient
from utils.parser import parse_ingredients
from utils.scorer import calculate_skin_match_score, calculate_overall_formula_score
from utils.risk_analysis import analyze_risk
from utils.benefits import extract_benefits, extract_concerns
from utils.recommendations import (
    generate_addition_recommendations,
    generate_avoid_recommendations,
    get_formula_strengths,
    get_formula_weaknesses,
)
from utils.summary_generator import generate_formula_summary

# ── Page configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Skincare Formula Intelligence Engine",
    page_icon="🧴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS — dark SaaS theme with rounded cards ──────────────────────────
st.markdown("""
<style>
/* ─── Global reset & base ─── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background-color: #0e1117;
    color: #e0e0e0;
}

/* ─── Hide Streamlit chrome ─── */
#MainMenu, footer, header { visibility: hidden; }

/* ─── Metric cards ─── */
div[data-testid="metric-container"] {
    background: #1a1d27;
    border: 1px solid #2a2d3e;
    border-radius: 12px;
    padding: 18px 20px;
}
div[data-testid="metric-container"] label {
    color: #888 !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
div[data-testid="metric-container"] [data-testid="metric-value"] {
    font-size: 1.6rem !important;
    font-weight: 700;
    color: #ffffff !important;
}

/* ─── Custom card ─── */
.sf-card {
    background: #1a1d27;
    border: 1px solid #2a2d3e;
    border-radius: 14px;
    padding: 22px 26px;
    margin-bottom: 16px;
}
.sf-card h3 { margin-top: 0; color: #c9d1e0; font-size: 0.85rem;
              letter-spacing: 0.1em; text-transform: uppercase; }

/* ─── Verdict banner ─── */
.verdict-banner {
    border-radius: 14px;
    padding: 26px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 18px;
}
.verdict-banner .vb-emoji { font-size: 2.8rem; line-height: 1; }
.verdict-banner .vb-text  { flex: 1; }
.verdict-banner .vb-label { font-size: 0.75rem; letter-spacing: 0.12em;
                             text-transform: uppercase; opacity: 0.75; margin-bottom: 4px; }
.verdict-banner .vb-main  { font-size: 1.7rem; font-weight: 700; line-height: 1.15; }
.verdict-banner .vb-score { font-size: 1rem; opacity: 0.8; margin-top: 4px; }

.vb-green  { background: linear-gradient(135deg, #0d2b1f 0%, #0f3329 100%);
             border: 1px solid #1a6644; }
.vb-blue   { background: linear-gradient(135deg, #0d1e36 0%, #102040 100%);
             border: 1px solid #1a4a8a; }
.vb-orange { background: linear-gradient(135deg, #2b1c0a 0%, #3a2210 100%);
             border: 1px solid #8a4a10; }
.vb-red    { background: linear-gradient(135deg, #2b0d0d 0%, #3a1010 100%);
             border: 1px solid #8a1a1a; }

/* ─── Tag chips ─── */
.tag-benefit {
    display: inline-block;
    background: #1a3d2b;
    border: 1px solid #2a6644;
    color: #5de8a0;
    border-radius: 20px;
    padding: 4px 13px;
    font-size: 0.78rem;
    margin: 3px 3px;
    font-weight: 500;
}
.tag-concern {
    display: inline-block;
    background: #3d1a1a;
    border: 1px solid #6a2a2a;
    color: #f08080;
    border-radius: 20px;
    padding: 4px 13px;
    font-size: 0.78rem;
    margin: 3px 3px;
    font-weight: 500;
}

/* ─── Strength / avoid items ─── */
.strength-item { color: #5de8a0; padding: 3px 0; font-size: 0.9rem; }
.avoid-item    { color: #f08080; padding: 3px 0; font-size: 0.9rem; }

/* ─── Summary box ─── */
.summary-box {
    background: #151822;
    border-left: 3px solid #4a9eff;
    border-radius: 0 12px 12px 0;
    padding: 18px 22px;
    color: #c8d0e0;
    font-size: 0.95rem;
    line-height: 1.7;
}

/* ─── Section headings ─── */
.sf-section-title {
    font-size: 0.72rem;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: #666;
    margin-bottom: 10px;
    margin-top: 4px;
}

/* ─── Dataframe override ─── */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* ─── Divider ─── */
.sf-divider { border: none; border-top: 1px solid #2a2d3e; margin: 20px 0; }

/* ─── Sidebar ─── */
[data-testid="stSidebar"] { background-color: #13161f; border-right: 1px solid #22253a; }
</style>
""", unsafe_allow_html=True)

# ── Knowledge base (cached so it only loads once per session) ─────────────────
@st.cache_data
def get_knowledge_base():
    """Load and cache the ingredient knowledge base CSV."""
    return load_knowledge_base()


# ── Helper: pick verdict banner colour class ──────────────────────────────────
def _banner_class(score: float) -> str:
    """Return CSS class name based on compatibility score band."""
    if score >= 85:
        return "vb-green"
    if score >= 75:
        return "vb-blue"
    if score >= 65:
        return "vb-orange"
    return "vb-red"


def _banner_emoji(score: float) -> str:
    """Return colour-coded circle emoji for verdict banner."""
    if score >= 85:
        return "🟢"
    if score >= 75:
        return "🔵"
    if score >= 65:
        return "🟠"
    return "🔴"


def _score_color(score: float) -> str:
    """Return hex colour string for inline score displays."""
    if score >= 85:
        return "#5de8a0"
    if score >= 75:
        return "#4a9eff"
    if score >= 65:
        return "#ffaa44"
    return "#f08080"


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧴 About This Tool")
    st.markdown("""
    This application uses a **rule-based ingredient intelligence engine**
    built from a custom skincare knowledge base covering 200+ ingredients.

    It analyses formulas for:
    - Skin-type compatibility
    - Risk profiling
    - Benefits & concerns
    - Ingredient recommendations
    """)
    st.markdown("---")

    st.markdown("### 🛠 Technology Stack")
    st.markdown("""
    - **Python 3.11**
    - **Streamlit** — UI framework
    - **Pandas** — data processing
    - **Plotly** — interactive charts
    """)

    st.markdown("---")
    st.caption(
        "⚠️ **Disclaimer:** This tool is for educational purposes only "
        "and does not replace professional dermatological advice."
    )


# ── Main header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 10px 0 24px 0;">
  <div style="font-size:2.2rem; font-weight:800; letter-spacing:-0.02em; color:#ffffff;">
    🧴 Skincare Formula Intelligence Engine
  </div>
  <div style="color:#888; font-size:1rem; margin-top:6px;">
    Analyze skincare formulations using ingredient intelligence,
    risk assessment, and explainable recommendations.
  </div>
</div>
""", unsafe_allow_html=True)


# ── Input card ────────────────────────────────────────────────────────────────
with st.container():
    st.markdown('<div class="sf-card">', unsafe_allow_html=True)

    col_input, col_skin, col_btn = st.columns([3, 1.2, 0.8])

    with col_input:
        st.markdown('<p class="sf-section-title">Ingredient List</p>', unsafe_allow_html=True)
        formula_input = st.text_area(
            label="ingredients",
            label_visibility="collapsed",
            height=140,
            placeholder="Ceramide NP\nPanthenol\nAllantoin\nCentella Asiatica\nNiacinamide",
        )

    with col_skin:
        st.markdown('<p class="sf-section-title">Skin Type</p>', unsafe_allow_html=True)
        skin_type = st.selectbox(
            label="skin_type",
            label_visibility="collapsed",
            options=["Sensitive", "Oily", "Dry", "Combination", "Normal"],
        )

    with col_btn:
        st.markdown('<p class="sf-section-title">&nbsp;</p>', unsafe_allow_html=True)
        analyse_clicked = st.button("🔬 Analyze Formula", use_container_width=True, type="primary")

    st.markdown('</div>', unsafe_allow_html=True)


# ── Analysis workflow ─────────────────────────────────────────────────────────
if analyse_clicked:
    if not formula_input.strip():
        st.error("Please enter at least one ingredient before analysing.")
        st.stop()

    kb = get_knowledge_base()

    # Step 1 — Parse raw text into normalised ingredient tokens
    parsed = parse_ingredients(formula_input)

    # Step 2 — Match each token against the knowledge base
    matched = [find_ingredient(name, kb) for name in parsed]
    matched = [m for m in matched if m is not None]

    # Step 3 — Identify unrecognised ingredients for transparency
    recognised_names = {m["ingredient"] for m in matched}
    unrecognised = [p for p in parsed if p not in recognised_names]

    if not matched:
        st.error("None of the entered ingredients were recognised. Check spelling or try INCI names.")
        st.stop()

    total_count = len(parsed)

    # Step 4 — Scoring
    compat   = calculate_skin_match_score(matched, skin_type.lower(), total_count)
    overall  = calculate_overall_formula_score(matched, total_count)

    compat_score  = compat["score"]
    overall_score = overall["score"]
    verdict       = compat["verdict"]
    coverage      = compat["coverage"]["coverage"]

    # Step 5 — Risk analysis
    risk = analyze_risk(matched)
    risk_label = risk["overall_risk"]

    # Step 6 — Benefits & concerns tags
    benefits = extract_benefits(matched)
    concerns = extract_concerns(matched)

    # Step 7 — Recommendations
    additions  = generate_addition_recommendations(skin_type.lower(), matched)
    avoid_list = generate_avoid_recommendations(skin_type.lower(), matched)
    strengths  = get_formula_strengths(matched, skin_type.lower())
    weaknesses = get_formula_weaknesses(matched, skin_type.lower())

    # Step 8 — Natural language summary
    summary = generate_formula_summary(
        skin_type=skin_type,
        compatibility_score=compat_score,
        risk_level=risk_label,
        benefits=benefits,
        concerns=concerns,
        strengths=strengths,
        weaknesses=weaknesses,
    )

    # ── VERDICT BANNER ────────────────────────────────────────────────────────
    css_class = _banner_class(compat_score)
    emoji     = _banner_emoji(compat_score)
    st.markdown(f"""
    <div class="verdict-banner {css_class}">
      <div class="vb-emoji">{emoji}</div>
      <div class="vb-text">
        <div class="vb-label">Formula Verdict</div>
        <div class="vb-main">{verdict} for {skin_type} Skin</div>
        <div class="vb-score">Compatibility Score: {compat_score} / 100</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── METRICS ROW ───────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Compatibility Score",  f"{compat_score} / 100")
    m2.metric("Overall Formula Score", f"{overall_score} / 100")
    m3.metric("Risk Level",            risk_label)
    m4.metric("Ingredient Coverage",   f"{coverage}%")

    st.markdown("<hr class='sf-divider'>", unsafe_allow_html=True)

    # ── HOW THE SCORE WORKS (expandable) ──────────────────────────────────────
    with st.expander("📊 How was this score calculated?"):
        st.markdown(f"""
        | Component | Value | Notes |
        |-----------|-------|-------|
        | **Compatibility Score** | {compat_score} / 100 | Average {skin_type.lower()} skin score across recognised ingredients, scaled 0–100 with a 5% realism adjustment |
        | **Overall Formula Score** | {overall_score} / 100 | Average score across all five skin types — measures general formulation quality |
        | **Risk Level** | {risk_label} | Based on count of High/Moderate risk ingredients: ≥3 High = High risk, ≥1 High = Moderate risk |
        | **Coverage** | {coverage}% | {compat['coverage']['recognized_ingredients']} of {compat['coverage']['total_ingredients']} ingredients matched in the knowledge base |

        > **Note:** Scores reflect ingredient compatibility only and do not account for concentration,
        > pH, formulation method, or manufacturing differences.
        """)

    # ── FORMULA COMPOSITION CHART ─────────────────────────────────────────────
    st.markdown('<p class="sf-section-title">Formula Composition</p>', unsafe_allow_html=True)

    category_counts = Counter(m["category"] for m in matched)
    cat_df = pd.DataFrame(
        list(category_counts.items()),
        columns=["Category", "Count"]
    ).sort_values("Count", ascending=True)

    fig = go.Figure(go.Bar(
        x=cat_df["Count"],
        y=cat_df["Category"],
        orientation="h",
        marker=dict(
            color=cat_df["Count"],
            colorscale=[[0, "#1a3d5c"], [0.5, "#2a6aad"], [1.0, "#4a9eff"]],
            line=dict(color="#0e1117", width=0.5),
        ),
        text=cat_df["Count"],
        textposition="outside",
        textfont=dict(color="#c8d0e0", size=12),
    ))
    fig.update_layout(
        paper_bgcolor="#1a1d27",
        plot_bgcolor="#1a1d27",
        font=dict(color="#c8d0e0", family="Inter, sans-serif"),
        margin=dict(l=10, r=30, t=10, b=10),
        height=max(180, len(category_counts) * 38),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                   title=None, fixedrange=True),
        yaxis=dict(showgrid=False, title=None, tickfont=dict(size=12)),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='sf-divider'>", unsafe_allow_html=True)

    # ── STRENGTHS + CONCERNS ROW ─────────────────────────────────────────────
    col_str, col_wk = st.columns(2)

    with col_str:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown('<h3>⭐ Top Strengths</h3>', unsafe_allow_html=True)
        for s in strengths:
            st.markdown(f'<div class="strength-item">✓ {s}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_wk:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown('<h3>⚠ Flagged Ingredients</h3>', unsafe_allow_html=True)
        if weaknesses:
            for w in weaknesses:
                st.markdown(f'<div class="avoid-item">⚠ {w}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#888; font-size:0.9rem;">No flagged ingredients detected.</div>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── BENEFITS + CONCERNS TAGS ──────────────────────────────────────────────
    col_ben, col_con = st.columns(2)

    with col_ben:
        st.markdown('<p class="sf-section-title">Formula Benefits</p>', unsafe_allow_html=True)
        if benefits:
            tags_html = "".join(f'<span class="tag-benefit">{b}</span>' for b in benefits[:12])
            st.markdown(tags_html, unsafe_allow_html=True)
        else:
            st.caption("No benefits detected.")

    with col_con:
        st.markdown('<p class="sf-section-title">Concern Flags</p>', unsafe_allow_html=True)
        if concerns:
            tags_html = "".join(f'<span class="tag-concern">{c}</span>' for c in concerns[:10])
            st.markdown(tags_html, unsafe_allow_html=True)
        else:
            st.markdown('<span class="tag-benefit">No Concerns Detected ✓</span>',
                        unsafe_allow_html=True)

    st.markdown("<hr class='sf-divider'>", unsafe_allow_html=True)

    # ── RECOMMENDATIONS ROW ───────────────────────────────────────────────────
    col_add, col_avoid = st.columns(2)

    with col_add:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown('<h3>➕ Suggested Additions</h3>', unsafe_allow_html=True)
        if additions:
            for a in additions:
                st.markdown(f'<div class="strength-item">✓ {a}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#888; font-size:0.9rem;">Formula already contains all recommended ingredients.</div>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_avoid:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown('<h3>🚫 Ingredients To Avoid</h3>', unsafe_allow_html=True)
        if avoid_list:
            for av in avoid_list:
                st.markdown(f'<div class="avoid-item">⚠ {av}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#888; font-size:0.9rem;">No problematic ingredients for this skin type.</div>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── FORMULA SUMMARY ───────────────────────────────────────────────────────
    st.markdown('<p class="sf-section-title">Formula Summary</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

    st.markdown("<hr class='sf-divider'>", unsafe_allow_html=True)

    # ── INGREDIENT ANALYSIS TABLE ─────────────────────────────────────────────
    st.markdown('<p class="sf-section-title">Full Ingredient Analysis</p>', unsafe_allow_html=True)

    table_rows = []
    for m in matched:
        # Build a coloured risk badge string
        risk_val = m.get("risk_level", "Low")
        table_rows.append({
            "Ingredient": m["ingredient"].title(),
            "Category":   m.get("category", "—"),
            "Function":   m.get("function", "—"),
            "Risk Level": risk_val,
            f"{skin_type} Score": m.get(f"{skin_type.lower()}_score", "—"),
        })

    if unrecognised:
        for u in unrecognised:
            table_rows.append({
                "Ingredient":        u.title(),
                "Category":          "Unknown",
                "Function":          "—",
                "Risk Level":        "—",
                f"{skin_type} Score": "—",
            })

    table_df = pd.DataFrame(table_rows)
    st.dataframe(table_df, use_container_width=True, hide_index=True)

    if unrecognised:
        st.caption(
            f"ℹ️ {len(unrecognised)} ingredient(s) not found in knowledge base: "
            + ", ".join(u.title() for u in unrecognised)
        )