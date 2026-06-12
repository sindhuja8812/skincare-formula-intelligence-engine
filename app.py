"""
app.py — Skincare Formula Intelligence Engine
Main Streamlit application entry point.

Responsibilities:
- Page layout, theming, and custom CSS injection
- Input collection (ingredient list + skin type)
- Orchestration of all backend utility calls
- Rendering: formula type detection, score drivers, strength meter,
  ingredient cards, recommendation table
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from collections import Counter
from typing import List

# ── Backend utility imports ───────────────────────────────────────────────────
from utils.knowledge_loader import load_knowledge_base, find_ingredient
from utils.parser import parse_ingredients
from utils.scorer import calculate_skin_match_score, calculate_overall_formula_score, SKIN_TYPE_COLUMNS
from utils.risk_analysis import analyze_risk
from utils.benefits import extract_benefits, extract_concerns
from utils.recommendations import (
    generate_addition_recommendations,
    generate_avoid_recommendations,
    get_formula_strengths,
    get_formula_weaknesses,
    PREFERRED_BY_SKIN_TYPE,
)
from utils.summary_generator import generate_formula_summary

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Skincare Formula Intelligence Engine",
    page_icon="",
    layout="wide",
    initial_sidebar_state="auto",   # sidebar hidden entirely via CSS below
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ─── Global ─── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background-color: #0e1117;
    color: #e0e0e0;
}
#MainMenu, footer, header { visibility: hidden; }

/* ─── Metric cards ─── */
div[data-testid="metric-container"] {
    background: #1a1d27;
    border: 1px solid #2a2d3e;
    border-radius: 12px;
    padding: 16px 20px;
}
div[data-testid="metric-container"] label {
    color: #888 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
div[data-testid="metric-container"] [data-testid="metric-value"] {
    font-size: 1.5rem !important;
    font-weight: 700;
    color: #ffffff !important;
}

/* ─── Generic card ─── */
.sf-card {
    background: #1a1d27;
    border: 1px solid #2a2d3e;
    border-radius: 14px;
    padding: 22px 26px;
    margin-bottom: 16px;
}
.sf-card h3 {
    margin-top: 0;
    color: #888;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

/* ─── Section label ─── */
.sf-section-title {
    font-size: 0.72rem;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: #555;
    margin-bottom: 12px;
    margin-top: 6px;
}

/* ─── Divider ─── */
.sf-divider { border: none; border-top: 1px solid #1e2130; margin: 24px 0; }

/* ─── Verdict banner ─── */
.verdict-banner {
    border-radius: 14px;
    padding: 24px 30px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 20px;
}
.vb-text  { flex: 1; }
.vb-label { font-size: 0.7rem; letter-spacing: 0.14em; text-transform: uppercase;
             opacity: 0.6; margin-bottom: 5px; }
.vb-main  { font-size: 1.6rem; font-weight: 700; line-height: 1.15; }
.vb-score { font-size: 0.9rem; opacity: 0.7; margin-top: 5px; }
.vb-green  { background: linear-gradient(135deg,#0b2419,#0e2d1f); border:1px solid #1a5e3a; }
.vb-blue   { background: linear-gradient(135deg,#0b1a2e,#0d2040); border:1px solid #1a3f78; }
.vb-orange { background: linear-gradient(135deg,#271708,#32190a); border:1px solid #7a3e08; }
.vb-red    { background: linear-gradient(135deg,#270b0b,#320e0e); border:1px solid #7a1515; }

/* ─── Formula health badge grid ─── */
.fh-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-top: 8px;
}
.fh-item {
    background: #13161f;
    border: 1px solid #1e2130;
    border-radius: 10px;
    padding: 14px 16px;
}
.fh-item .fh-lbl { font-size: 0.68rem; letter-spacing: 0.1em; text-transform: uppercase;
                    color: #555; margin-bottom: 5px; }
.fh-item .fh-val { font-size: 0.95rem; font-weight: 600; }
.fh-green  { color: #5de8a0; }
.fh-blue   { color: #4a9eff; }
.fh-orange { color: #ffaa44; }
.fh-red    { color: #f08080; }
.fh-neutral{ color: #c8d0e0; }

/* ─── Formula type chips ─── */
.ft-badge {
    display: inline-block;
    background: #0f2236;
    border: 1px solid #1a4060;
    color: #4a9eff;
    border-radius: 6px;
    padding: 5px 14px;
    font-size: 0.8rem;
    font-weight: 600;
    margin: 3px 4px 3px 0;
    letter-spacing: 0.03em;
}
.ft-primary {
    background: #102b1e;
    border: 1px solid #1a5034;
    color: #5de8a0;
    font-size: 0.9rem;
    padding: 7px 16px;
}


/* ─── Ingredient cards ─── */
.ic-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 12px;
    margin-top: 8px;
}
.ic-card {
    background: #13161f;
    border: 1px solid #1e2130;
    border-radius: 12px;
    padding: 12px 14px;
    min-height: auto;
    display: flex;
    flex-direction: column;
}
.ic-card.ic-risk-high   { border-left: 3px solid #f08080; }
.ic-card.ic-risk-mod    { border-left: 3px solid #ffaa44; }
.ic-card.ic-risk-low    { border-left: 3px solid #1e2130; }
.ic-name    { font-size: 0.88rem; font-weight: 600; color: #dde4f0;
               margin-bottom: 2px; }
.ic-fn      { font-size: 0.68rem; color: #555; text-transform: uppercase;
               letter-spacing: 0.08em; margin-bottom: 6px; }
.ic-score-row { display: flex; align-items: center; justify-content: space-between;
                 margin-bottom: 6px; gap: 8px; }
.ic-score-lbl { font-size: 0.68rem; color: #555; }
.ic-score-val { font-size: 0.82rem; font-weight: 700; }
.ic-risk-badge {
    display: inline-block;
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 2px 6px;
    border-radius: 3px;
    margin-bottom: 6px;
}
.ic-rb-low  { background:#0f2a1a; color:#5de8a0; border:1px solid #1a4a2a; }
.ic-rb-mod  { background:#2a1e08; color:#ffaa44; border:1px solid #5a3a08; }
.ic-rb-high { background:#2a0e0e; color:#f08080; border:1px solid #5a1818; }
.ic-benefit { font-size: 0.73rem; color: #6a8aaa; padding: 2px 0; line-height: 1.3; }
.ic-benefit::before { content: "✓ "; color: #5de8a0; margin-right: 3px; }

/* ─── Recommendation table ─── */
.rec-row {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 0;
    padding: 11px 0;
    border-bottom: 1px solid #1a1d27;
    font-size: 0.88rem;
    align-items: start;
}
.rec-row:last-child { border-bottom: none; }
.rec-name { color: #c8d0e0; font-weight: 500; }
.rec-why  { color: #666; font-size: 0.82rem; line-height: 1.45; }

/* ─── Tags ─── */
.tag-benefit {
    display: inline-block;
    background: #0f2419;
    border: 1px solid #1a4a2a;
    color: #5de8a0;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.76rem;
    margin: 3px 3px;
    font-weight: 500;
}
.tag-concern {
    display: inline-block;
    background: #2a0f0f;
    border: 1px solid #4a1a1a;
    color: #f08080;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.76rem;
    margin: 3px 3px;
    font-weight: 500;
}

/* ─── Summary box ─── */
.summary-box {
    background: #0e1117;
    border-left: 3px solid #2a5a9a;
    border-radius: 0 12px 12px 0;
    padding: 18px 22px;
    color: #9aa8be;
    font-size: 0.91rem;
    line-height: 1.8;
    white-space: pre-wrap;
    font-family: 'Inter', 'Segoe UI', monospace;
}

/* ─── Dataframe ─── */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* ─── Hide sidebar toggle button entirely ─── */
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helper functions for the 5 new features
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def get_knowledge_base():
    """Load and cache the ingredient knowledge base CSV once per session."""
    return load_knowledge_base()


def _score_color_class(score: float) -> str:
    """Map a 0–100 score to one of four CSS colour class names."""
    if score >= 85: return "fh-green"
    if score >= 75: return "fh-blue"
    if score >= 65: return "fh-orange"
    return "fh-red"


def _banner_class(score: float) -> str:
    """Map score to verdict banner background CSS class."""
    if score >= 85: return "vb-green"
    if score >= 75: return "vb-blue"
    if score >= 65: return "vb-orange"
    return "vb-red"


# ── Feature 1 helper: Formula Type Detection ─────────────────────────────────
# Maps benefit strings to formula type labels.
# If a formula accumulates enough of a given benefit, we classify it as that type.

_BENEFIT_TO_TYPE: dict[str, str] = {
    "Barrier Repair":         "Barrier Repair",
    "Soothing":               "Soothing",
    "Hydration":              "Hydrating",
    "Moisture Retention":     "Hydrating",
    "Anti-Inflammatory":      "Anti-Inflammatory",
    "Anti-Aging":             "Anti-Aging",
    "Brightening":            "Brightening",
    "Acne Support":           "Acne-Focused",
    "Oil Control":            "Oil Control",
    "Exfoliation":            "Exfoliating",
    "Antioxidant":            "Antioxidant-Rich",
    "Pigmentation Reduction": "Brightening",
    "Skin Recovery":          "Repair-Focused",
}

def detect_formula_type(matched_ingredients: List[dict]) -> tuple[str, List[str]]:
    """
    Derive the formula's primary type and secondary types from benefit counts.

    Counts how often each mapped type appears across all ingredient benefits,
    returns the most common as primary and up to 3 others as secondary labels.

    Returns:
        (primary_type, secondary_types)
    """
    type_counts: Counter = Counter()
    for ing in matched_ingredients:
        raw = ing.get("benefits", "None") or "None"
        for benefit in raw.split("|"):
            b = benefit.strip()
            if b in _BENEFIT_TO_TYPE:
                type_counts[_BENEFIT_TO_TYPE[b]] += 1   # accumulate type score

    if not type_counts:
        return "General Formula", []

    ordered = type_counts.most_common()          # sorted by frequency
    primary    = ordered[0][0]                   # top type is primary
    secondary  = [t for t, _ in ordered[1:4]]   # next up to 3 are secondary
    return primary, secondary



# ── Feature 3 helper: Strength Meter (Plotly chart) ──────────────────────────
# Maps benefit keywords to six formula strength dimensions.
# Keywords are intentionally specific: "Skin Recovery" is a repair benefit,
# not an aging benefit, so it belongs only to Soothing/Repair dimensions.

_STRENGTH_DIMENSIONS: dict[str, List[str]] = {
    "Hydration":      ["Hydration", "Moisture Retention"],
    "Barrier Repair": ["Barrier Repair"],
    "Soothing":       ["Soothing", "Redness Reduction", "Skin Recovery"],
    "Brightening":    ["Brightening", "Pigmentation Reduction"],
    "Anti-Aging":     ["Anti-Aging"],                          # strict — Skin Recovery removed
    "Oil Control":    ["Oil Control", "Acne Support", "Pore Care"],
}

def build_strength_meter(matched_ingredients: List[dict]) -> List[dict]:
    """
    Score each dimension by counting total benefit keyword hits across all ingredients.

    Unlike the previous binary version (ingredient either contributes or not),
    this counts every matching keyword, so an ingredient with 3 soothing benefits
    contributes more than one with 1. Scores are normalised against the maximum
    possible hits (n_ingredients × max_keywords_per_dimension) so the output
    is always 0–100 and comparable across dimensions.

    Returns:
        List of dicts: {dimension, score (0–100), color_hex}, sorted descending.
    """
    n = max(len(matched_ingredients), 1)

    # Count total keyword hits per dimension (not just "did any match?")
    dim_hits: dict[str, int] = {d: 0 for d in _STRENGTH_DIMENSIONS}

    for ing in matched_ingredients:
        raw = ing.get("benefits", "None") or "None"
        benefit_set = {b.strip() for b in raw.split("|")}
        for dim, keywords in _STRENGTH_DIMENSIONS.items():
            # Count how many keywords from this dimension the ingredient has
            hits = sum(1 for k in keywords if k in benefit_set)
            dim_hits[dim] += hits

    result = []
    for dim, hits in dim_hits.items():
        # Normalise: max possible = n_ingredients × n_keywords_for_this_dimension
        max_possible = n * len(_STRENGTH_DIMENSIONS[dim])
        score = round(min((hits / max_possible) * 100, 100)) if max_possible else 0

        if score >= 70:    color = "#5de8a0"
        elif score >= 40:  color = "#4a9eff"
        elif score >= 15:  color = "#ffaa44"
        else:              color = "#3a3d4e"

        result.append({"dimension": dim, "score": score, "color": color})

    result.sort(key=lambda x: x["score"], reverse=True)
    return result


# ── Feature 4 helper: Recommended additions with reasons ─────────────────────

# Per-ingredient rationale shown in the recommendation table
_ADDITION_REASONS: dict[str, str] = {
    "ceramide np":              "Reinforces the skin barrier and seals in moisture",
    "panthenol":                "Calms irritation and accelerates surface healing",
    "allantoin":                "Promotes cell renewal and soothes stressed skin",
    "centella asiatica extract":"Reduces inflammation and supports barrier recovery",
    "beta glucan":              "Deep-acting anti-inflammatory with barrier benefits",
    "aloe vera":                "Lightweight hydration with immediate soothing effect",
    "niacinamide":              "Regulates sebum, minimises pores, and brightens tone",
    "salicylic acid":           "Exfoliates inside pores and reduces breakouts",
    "zinc pca":                 "Controls oil production and provides antibacterial action",
    "green tea extract":        "Antioxidant protection with mild oil-regulating effect",
    "squalane":                 "Lightweight emollient that mimics skin's natural oils",
    "glycerin":                 "Draws moisture into the skin from the environment",
    "hyaluronic acid":          "Holds up to 1000x its weight in water for deep hydration",
    "urea":                     "Humectant and gentle exfoliant for dry, flaky skin",
    "petrolatum":               "Occlusive barrier that prevents transepidermal water loss",
}

def get_addition_reasons(additions: List[str]) -> List[dict]:
    """
    Pair each suggested ingredient with a plain-language explanation of why it helps.

    Falls back to a generic description if the ingredient isn't in the lookup table.

    Args:
        additions: Title-cased ingredient names from generate_addition_recommendations().

    Returns:
        List of dicts: {name, reason}.
    """
    result = []
    for name in additions:
        key    = name.lower()
        reason = _ADDITION_REASONS.get(key, "Beneficial ingredient for this skin type")
        result.append({"name": name, "reason": reason})
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Render helpers
# ─────────────────────────────────────────────────────────────────────────────

def render_ingredient_card(ing: dict, skin_type: str) -> str:
    """
    Build the HTML string for one ingredient card.

    Uses string concatenation (not a multiline f-string) so Streamlit's
    markdown parser never sees indented lines it could misread as a code block.

    Args:
        ing:       Matched ingredient dict from the knowledge base.
        skin_type: Used to pull the relevant score column.

    Returns:
        str: HTML block for one card, safe to concatenate into the ic-grid div.
    """
    col        = f"{skin_type.lower()}_score"
    score      = ing.get(col, "—")
    risk       = ing.get("risk_level", "Low")
    name       = ing["ingredient"].title()
    function   = ing.get("function", "—")
    raw_ben    = ing.get("benefits", "None") or "None"
    top_bens   = [b.strip() for b in raw_ben.split("|") if b.strip().lower() != "none"][:2]

    # CSS modifier classes for border and risk badge colour
    risk_border = {"High": "ic-risk-high", "Moderate": "ic-risk-mod"}.get(risk, "ic-risk-low")
    risk_badge  = {"High": "ic-rb-high",   "Moderate": "ic-rb-mod"  }.get(risk, "ic-rb-low")

    # Score value and colour
    if isinstance(score, (int, float)):
        if score >= 8:    score_color = "#5de8a0"
        elif score >= 6:  score_color = "#4a9eff"
        elif score >= 4:  score_color = "#ffaa44"
        else:             score_color = "#f08080"
        score_display = f"{score}/10"
    else:
        score_color   = "#888"
        score_display = "—"

    # Build benefit lines — one per benefit, no multiline template
    bens_html = "".join(f'<div class="ic-benefit">{b}</div>' for b in top_bens)

    # Assemble card with concatenation only — no indented multiline f-string
    html  = f'<div class="ic-card {risk_border}">'
    html += f'<div class="ic-name">{name}</div>'
    html += f'<div class="ic-fn">{function}</div>'
    html += f'<div class="ic-score-row">'
    html += f'<span class="ic-score-lbl">{skin_type} skin</span>'
    html += f'<span class="ic-score-val" style="color:{score_color}">{score_display}</span>'
    html += f'</div>'
    html += f'<span class="ic-risk-badge {risk_badge}">{risk} risk</span>'
    html += bens_html
    html += f'</div>'
    return html


# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="padding: 8px 0 22px 0;">
  <div style="font-size:1.9rem; font-weight:800; letter-spacing:-0.02em; color:#ffffff;">
    Skincare Formula Intelligence Engine
  </div>
  <div style="color:#555; font-size:0.9rem; margin-top:5px;">
    Analyse formulations using ingredient intelligence, risk profiling, and explainable scoring.
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Input panel
# ─────────────────────────────────────────────────────────────────────────────

col_input, col_right = st.columns([3, 1.2])

with col_input:
    st.markdown('<p class="sf-section-title">Ingredient List</p>', unsafe_allow_html=True)
    formula_input = st.text_area(
        label="ingredients",
        label_visibility="collapsed",
        height=130,
        placeholder="Ceramide NP\nPanthenol\nAllantoin\nCentella Asiatica\nNiacinamide",
    )

with col_right:
    st.markdown('<p class="sf-section-title">Skin Type</p>', unsafe_allow_html=True)
    skin_type = st.selectbox(
        label="skin_type",
        label_visibility="collapsed",
        options=["Sensitive", "Oily", "Dry", "Combination", "Normal"],
    )
    # Button sits directly below dropdown in the same column
    analyse_clicked = st.button("Analyse Formula", use_container_width=True, type="primary")

# About / disclaimer collapsed — frees full width for results
with st.expander("About this project"):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        **What this tool does**

        Rule-based ingredient intelligence engine built from a custom knowledge
        base covering 200+ skincare actives, humectants, occlusives, and irritants.
        Analyses compatibility, risk, and formula composition without any ML model.
        """)
    with c2:
        st.markdown("""
        **Technology**

        Python · Streamlit · Pandas · Plotly
        """)
    with c3:
        st.markdown("""
        **Disclaimer**

        Educational tool only. Does not replace professional dermatological advice.
        Scores reflect ingredient-level data and do not account for concentration or pH.
        """)


# ─────────────────────────────────────────────────────────────────────────────
# Analysis
# ─────────────────────────────────────────────────────────────────────────────

if analyse_clicked:
    if not formula_input.strip():
        st.error("Enter at least one ingredient before analysing.")
        st.stop()

    kb = get_knowledge_base()

    # Parse → match → identify unrecognised
    parsed   = parse_ingredients(formula_input)
    matched  = [find_ingredient(name, kb) for name in parsed]
    matched  = [m for m in matched if m is not None]
    recognised_names = {m["ingredient"] for m in matched}
    unrecognised     = [p for p in parsed if p not in recognised_names]

    if not matched:
        st.error("None of the entered ingredients were recognised. Check spelling or try INCI names.")
        st.stop()

    total_count = len(parsed)

    # ── Core calculations ─────────────────────────────────────────────────────
    compat        = calculate_skin_match_score(matched, skin_type.lower(), total_count)
    overall       = calculate_overall_formula_score(matched, total_count)
    compat_score  = compat["score"]
    overall_score = overall["score"]
    verdict       = compat["verdict"]
    coverage      = compat["coverage"]["coverage"]

    risk       = analyze_risk(matched)
    risk_label = risk["overall_risk"]

    benefits   = extract_benefits(matched)
    concerns   = extract_concerns(matched)

    additions  = generate_addition_recommendations(skin_type.lower(), matched)
    avoid_list = generate_avoid_recommendations(skin_type.lower(), matched)
    strengths  = get_formula_strengths(matched, skin_type.lower())
    weaknesses = get_formula_weaknesses(matched, skin_type.lower())

    summary = generate_formula_summary(
        skin_type=skin_type,
        compatibility_score=compat_score,
        risk_level=risk_label,
        benefits=benefits,
        concerns=concerns,
        strengths=strengths,
        weaknesses=weaknesses,
    )

    # ── New feature data ──────────────────────────────────────────────────────
    primary_type, secondary_types = detect_formula_type(matched)     # Feature: formula type
    strength_meter = build_strength_meter(matched)                   # Feature: strength meter
    addition_reasons = get_addition_reasons(additions)               # Feature: rec table

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 1 — VERDICT BANNER
    # ═════════════════════════════════════════════════════════════════════════
    css_class = _banner_class(compat_score)
    st.markdown(f"""
    <div class="verdict-banner {css_class}">
      <div class="vb-text">
        <div class="vb-label">Formula Verdict</div>
        <div class="vb-main">{verdict} for {skin_type} Skin</div>
        <div class="vb-score">Compatibility Score: {compat_score} / 100 &nbsp;·&nbsp;
          {compat['coverage']['recognized_ingredients']} of {compat['coverage']['total_ingredients']} ingredients recognised</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 2 — FORMULA HEALTH BADGE (replaces metrics row)
    # ═════════════════════════════════════════════════════════════════════════
    sc  = _score_color_class(compat_score)
    osc = _score_color_class(overall_score)
    rc  = {"Low": "fh-green", "Moderate": "fh-orange", "High": "fh-red"}.get(risk_label, "fh-neutral")
    cvc = "fh-green" if coverage >= 80 else ("fh-orange" if coverage >= 50 else "fh-red")

    st.markdown(f"""
    <div class="fh-grid">
      <div class="fh-item">
        <div class="fh-lbl">Compatibility</div>
        <div class="fh-val {sc}">{compat_score} / 100</div>
      </div>
      <div class="fh-item">
        <div class="fh-lbl">Formula Quality</div>
        <div class="fh-val {osc}">{overall_score} / 100</div>
      </div>
      <div class="fh-item">
        <div class="fh-lbl">Risk Profile</div>
        <div class="fh-val {rc}">{risk_label}</div>
      </div>
      <div class="fh-item">
        <div class="fh-lbl">Coverage</div>
        <div class="fh-val {cvc}">{coverage}%</div>
        <div style="font-size:0.68rem;color:#666;margin-top:5px;">{compat['coverage']['recognized_ingredients']}/{compat['coverage']['total_ingredients']} recognised</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='sf-divider'>", unsafe_allow_html=True)

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 3 — FORMULA STRENGTH METER (Feature 3)
    # ═════════════════════════════════════════════════════════════════════════
    st.markdown('<p class="sf-section-title">Formula Strength Profile</p>', unsafe_allow_html=True)

    # Build Plotly horizontal bar chart — sorted ascending so highest is at top
    dims   = [d["dimension"] for d in reversed(strength_meter)]
    scores = [d["score"]     for d in reversed(strength_meter)]
    colors = [d["color"]     for d in reversed(strength_meter)]

    fig = go.Figure(go.Bar(
        x=scores,
        y=dims,
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{s}" for s in scores],
        textposition="outside",
        textfont=dict(color="#888", size=11),
        hovertemplate="%{y}: %{x}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="#1a1d27",
        plot_bgcolor="#1a1d27",
        font=dict(color="#888", family="Inter, sans-serif", size=12),
        margin=dict(l=0, r=40, t=8, b=8),
        height=240,
        xaxis=dict(
            range=[0, 110],
            showgrid=False, zeroline=False,
            showticklabels=False, fixedrange=True,
        ),
        yaxis=dict(
            showgrid=False, tickfont=dict(size=11, color="#888"),
            fixedrange=True,
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<hr class='sf-divider'>", unsafe_allow_html=True)

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 4 — INGREDIENT CARDS  (Feature 4)
    # ═════════════════════════════════════════════════════════════════════════
    st.markdown('<p class="sf-section-title">Ingredient Breakdown</p>', unsafe_allow_html=True)

    cards_html = '<div class="ic-grid">'
    for m in matched:
        cards_html += render_ingredient_card(m, skin_type)
    cards_html += '</div>'

    st.markdown(cards_html, unsafe_allow_html=True)

    if unrecognised:
        st.caption(
            f"{len(unrecognised)} ingredient(s) not in knowledge base: "
            + ", ".join(u.title() for u in unrecognised)
        )

    st.markdown("<hr class='sf-divider'>", unsafe_allow_html=True)

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 5 — RECOMMENDATION TABLE  (Feature 5)
    # ═════════════════════════════════════════════════════════════════════════
    col_rec, col_avoid_col = st.columns(2)

    with col_rec:
        st.markdown('<p class="sf-section-title">Suggested Ingredients</p>',
                    unsafe_allow_html=True)

        if addition_reasons:
            inner  = '<div class="rec-row" style="border-bottom:1px solid #2a2d3e;padding-bottom:8px;margin-bottom:4px;">'
            inner += '<span style="color:#555;font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;">Ingredient</span>'
            inner += '<span style="color:#555;font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;">Why it helps</span>'
            inner += '</div>'
            inner += "".join(
                f'<div class="rec-row"><span class="rec-name">{r["name"]}</span>'
                f'<span class="rec-why">{r["reason"]}</span></div>'
                for r in addition_reasons
            )
        else:
            inner = '<div style="color:#555;font-size:0.88rem;">Formula already contains all recommended ingredients for this skin type.</div>'

        # Single call — full card including open and close div
        st.markdown(f'<div class="sf-card" style="padding:16px 20px;">{inner}</div>',
                    unsafe_allow_html=True)

    with col_avoid_col:
        if avoid_list:
            st.markdown('<p class="sf-section-title">Ingredients to Reconsider</p>',
                        unsafe_allow_html=True)

            inner2  = '<div class="rec-row" style="border-bottom:1px solid #2a2d3e;padding-bottom:8px;margin-bottom:4px;">'
            inner2 += '<span style="color:#555;font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;">Ingredient</span>'
            inner2 += '<span style="color:#555;font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;">Concern</span>'
            inner2 += '</div>'

            for av in avoid_list:
                av_ing = find_ingredient(av.lower(), kb)
                concern_text = "Not recommended for this skin type"
                if av_ing:
                    raw_c  = av_ing.get("concerns", "") or ""
                    c_list = [c.strip() for c in raw_c.split("|") if c.strip().lower() != "none"]
                    if c_list:
                        concern_text = ", ".join(c_list[:2])
                inner2 += (
                    f'<div class="rec-row">'
                    f'<span class="rec-name" style="color:#f08080">{av}</span>'
                    f'<span class="rec-why">{concern_text}</span>'
                    f'</div>'
                )

            # Single call — full card
            st.markdown(f'<div class="sf-card" style="padding:16px 20px;">{inner2}</div>',
                        unsafe_allow_html=True)

    st.markdown("<hr class='sf-divider'>", unsafe_allow_html=True)

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 6 — BENEFITS / CONCERNS TAGS + FORMULA SUMMARY
    # ═════════════════════════════════════════════════════════════════════════
    col_ben, col_con = st.columns(2)

    with col_ben:
        st.markdown('<p class="sf-section-title">Formula Benefits</p>', unsafe_allow_html=True)
        if benefits:
            tags = "".join(f'<span class="tag-benefit">{b}</span>' for b in benefits[:12])
            st.markdown(tags, unsafe_allow_html=True)
        else:
            st.caption("No benefits detected.")

    with col_con:
        if concerns:
            st.markdown('<p class="sf-section-title">Concern Flags</p>', unsafe_allow_html=True)
            tags = "".join(f'<span class="tag-concern">{c}</span>' for c in concerns[:10])
            st.markdown(tags, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="sf-section-title">Formula Summary</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

    # Score explanation — collapsed by default, available for recruiters / curious users
    with st.expander("Scoring Methodology"):
        st.markdown(f"""
| Component | Value | Method |
|-----------|-------|--------|
| Compatibility Score | {compat_score} / 100 | Average {skin_type.lower()} skin score (0–10) across {len(matched)} recognised ingredients, scaled ×10 then ×0.95 realism factor |
| Overall Formula Score | {overall_score} / 100 | Same method averaged across all five skin-type columns |
| Risk Level | {risk_label} | High if ≥3 high-risk ingredients; Moderate if ≥1; Low otherwise |

> Scores reflect ingredient-level data only. Concentration, pH, and manufacturing are not accounted for.
        """)