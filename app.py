"""
app.py — Skincare Formula Intelligence Engine
Main Streamlit application entry point.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from collections import Counter
from typing import List

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

st.set_page_config(
    page_title="Skincare Formula Intelligence Engine",
    page_icon="",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background-color: #0e1117;
    color: #e0e0e0;
}
#MainMenu, footer, header { visibility: hidden; }

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

.sf-section-title {
    font-size: 0.72rem;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: #555;
    margin-bottom: 12px;
    margin-top: 6px;
}

.sf-divider { border: none; border-top: 1px solid #1e2130; margin: 24px 0; }

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

/* ── Formula health badge grid — 3 cells now (Coverage removed) ── */
.fh-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
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

/* ── Skin type comparison table ── */
.stc-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 8px;
    font-size: 0.88rem;
}
.stc-table th {
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #555;
    padding: 6px 12px;
    text-align: left;
    border-bottom: 1px solid #1e2130;
}
.stc-table td {
    padding: 9px 12px;
    border-bottom: 1px solid #13161f;
    color: #c8d0e0;
}
.stc-table tr:last-child td { border-bottom: none; }
.stc-active-row td { background: #0f1e14; }
.stc-bar-wrap {
    background: #13161f;
    border-radius: 4px;
    height: 6px;
    width: 120px;
    display: inline-block;
    vertical-align: middle;
    margin-right: 8px;
}
.stc-bar-fill {
    height: 6px;
    border-radius: 4px;
    display: block;
}
.stc-badge {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 3px;
    vertical-align: middle;
}
.stc-best      { background:#0f2a1a; color:#5de8a0; border:1px solid #1a4a2a; }
.stc-secondary { background:#0b1a2e; color:#4a9eff; border:1px solid #1a3f78; }

[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def get_knowledge_base():
    return load_knowledge_base()


def _score_color_class(score: float) -> str:
    """Map 0–90 score to CSS colour class. Aligned with VERDICT_THRESHOLDS."""
    if score >= 82: return "fh-green"
    if score >= 72: return "fh-blue"
    if score >= 62: return "fh-orange"
    return "fh-red"


def _banner_class(score: float) -> str:
    if score >= 82: return "vb-green"
    if score >= 72: return "vb-blue"
    if score >= 62: return "vb-orange"
    return "vb-red"


# ── Formula Type Detection ────────────────────────────────────────────────────

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
    type_counts: Counter = Counter()
    for ing in matched_ingredients:
        raw = ing.get("benefits", "None") or "None"
        for benefit in raw.split("|"):
            b = benefit.strip()
            if b in _BENEFIT_TO_TYPE:
                type_counts[_BENEFIT_TO_TYPE[b]] += 1
    if not type_counts:
        return "General Formula", []
    ordered   = type_counts.most_common()
    primary   = ordered[0][0]
    secondary = [t for t, _ in ordered[1:4]]
    return primary, secondary


# ── Strength Meter ────────────────────────────────────────────────────────────

_STRENGTH_DIMENSIONS: dict[str, List[str]] = {
    "Hydration":      ["Hydration", "Moisture Retention"],
    "Barrier Repair": ["Barrier Repair"],
    "Soothing":       ["Soothing", "Redness Reduction", "Skin Recovery"],
    "Brightening":    ["Brightening", "Pigmentation Reduction"],
    "Anti-Aging":     ["Anti-Aging"],
    "Oil Control":    ["Oil Control", "Acne Support", "Pore Care"],
}

# Maps raw 0-100 score to a confidence tier label and a normalised display score
# so bars represent category confidence, not raw arithmetic counts.
_CONFIDENCE_TIERS: list[tuple[int, str, int]] = [
    # (min_raw, label,       display_score)
    (75, "Very High",  100),
    (45, "High",        78),
    (20, "Medium",      52),
    (5,  "Low",         28),
    (0,  "Minimal",     10),
]

def _to_confidence(raw_score: int) -> tuple[str, int]:
    """Convert a raw 0–100 score to (label, display_score) pair."""
    for min_raw, label, display in _CONFIDENCE_TIERS:
        if raw_score >= min_raw:
            return label, display
    return "Minimal", 10


def build_strength_meter(matched_ingredients: List[dict]) -> List[dict]:
    """
    Score each dimension by keyword hits, then convert to confidence tiers
    so the chart shows category confidence rather than raw arithmetic counts.
    """
    n = max(len(matched_ingredients), 1)
    dim_hits: dict[str, int] = {d: 0 for d in _STRENGTH_DIMENSIONS}

    for ing in matched_ingredients:
        raw         = ing.get("benefits", "None") or "None"
        benefit_set = {b.strip() for b in raw.split("|")}
        for dim, keywords in _STRENGTH_DIMENSIONS.items():
            dim_hits[dim] += sum(1 for k in keywords if k in benefit_set)

    result = []
    for dim, hits in dim_hits.items():
        max_possible = n * len(_STRENGTH_DIMENSIONS[dim])
        raw_score    = round(min((hits / max_possible) * 100, 100)) if max_possible else 0

        label, display_score = _to_confidence(raw_score)

        if label == "Very High": color = "#5de8a0"
        elif label == "High":    color = "#4a9eff"
        elif label == "Medium":  color = "#ffaa44"
        else:                    color = "#3a3d4e"

        result.append({
            "dimension":     dim,
            "raw_score":     raw_score,
            "display_score": display_score,
            "label":         label,
            "color":         color,
        })

    result.sort(key=lambda x: x["display_score"], reverse=True)
    return result


# ── Skin Type Comparison ──────────────────────────────────────────────────────

_ALL_SKIN_TYPES = ["oily", "combination", "normal", "dry", "sensitive"]

def calculate_skin_type_comparison(matched_ingredients: List[dict], total_count: int) -> List[dict]:
    """
    Score the formula against every skin type and return rows sorted best-first.
    Each row: {skin_type, score, verdict, color, bar_color}
    """
    rows = []
    for st_key in _ALL_SKIN_TYPES:
        result = calculate_skin_match_score(matched_ingredients, st_key, total_count)
        score  = result["score"]

        if score >= 82:   color, bar_color = "#5de8a0", "#5de8a0"
        elif score >= 72: color, bar_color = "#4a9eff", "#4a9eff"
        elif score >= 62: color, bar_color = "#ffaa44", "#ffaa44"
        else:             color, bar_color = "#f08080", "#f08080"

        rows.append({
            "skin_type": st_key.title(),
            "score":     score,
            "verdict":   result["verdict"],
            "color":     color,
            "bar_color": bar_color,
        })

    rows.sort(key=lambda r: r["score"], reverse=True)
    return rows


def render_skin_type_comparison(rows: List[dict], active_skin_type: str) -> str:
    """
    Build the HTML for the skin-type comparison table.
    The currently-selected skin type gets a highlighted row.
    Best and second-best rows get a badge.
    """
    active_lower = active_skin_type.lower()

    html  = '<table class="stc-table">'
    html += '<thead><tr>'
    html += '<th>Skin Type</th><th>Compatibility</th><th>Score</th><th></th>'
    html += '</tr></thead><tbody>'

    for i, row in enumerate(rows):
        is_active  = row["skin_type"].lower() == active_lower
        row_class  = ' class="stc-active-row"' if is_active else ""
        bar_width  = round((row["score"] / 90) * 120)   # max bar = 120px at score 90
        bar_width  = min(bar_width, 120)

        badge = ""
        if is_active:
            badge = '<span class="stc-badge" style="background:#1a2e40;color:#7ec8e3;border:1px solid #2a5a78;">▶ Selected</span>'
        elif i == 0:
            badge = '<span class="stc-badge stc-best">Best Match</span>'
        elif i == 1 and rows[0]["skin_type"].lower() != active_lower:
            badge = '<span class="stc-badge stc-secondary">Good Match</span>'

        html += f'<tr{row_class}>'
        html += f'<td style="color:{row["color"]};font-weight:600">{row["skin_type"]}</td>'
        html += (
            f'<td>'
            f'<span class="stc-bar-wrap">'
            f'<span class="stc-bar-fill" style="width:{bar_width}px;background:{row["bar_color"]}"></span>'
            f'</span>'
            f'</td>'
        )
        html += f'<td style="color:{row["color"]};font-weight:700">{round(row["score"])}</td>'
        html += f'<td>{badge}</td>'
        html += '</tr>'

    html += '</tbody></table>'
    return html


# ── Recommendation Reasons ────────────────────────────────────────────────────

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
    result = []
    for name in additions:
        key    = name.lower()
        reason = _ADDITION_REASONS.get(key, "Beneficial ingredient for this skin type")
        result.append({"name": name, "reason": reason})
    return result


# ── Ingredient Card ───────────────────────────────────────────────────────────

def render_ingredient_card(ing: dict, skin_type: str) -> str:
    col      = f"{skin_type.lower()}_score"
    risk_col = f"{skin_type.lower()}_risk"
    score    = ing.get(col, "—")          
    risk     = ing.get(risk_col) or ing.get("risk_level", "Low")
    name       = ing["ingredient"].title()
    function   = ing.get("function", "—")
    raw_ben    = ing.get("benefits", "None") or "None"
    top_bens   = [b.strip() for b in raw_ben.split("|") if b.strip().lower() != "none"][:2]

    risk_border = {"High": "ic-risk-high", "Moderate": "ic-risk-mod"}.get(risk, "ic-risk-low")
    risk_badge  = {"High": "ic-rb-high",   "Moderate": "ic-rb-mod"  }.get(risk, "ic-rb-low")

    if isinstance(score, (int, float)):
        if score >= 8:    score_color = "#5de8a0"
        elif score >= 6:  score_color = "#4a9eff"
        elif score >= 4:  score_color = "#ffaa44"
        else:             score_color = "#f08080"
        score_display = f"{score}/10"
    else:
        score_color   = "#888"
        score_display = "—"

    bens_html = "".join(f'<div class="ic-benefit">{b}</div>' for b in top_bens)

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
    analyse_clicked = st.button("Analyse Formula", use_container_width=True, type="primary")

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

    parsed   = parse_ingredients(formula_input)
    matched  = [find_ingredient(name, kb) for name in parsed]
    matched  = [m for m in matched if m is not None]
    recognised_names = {m["ingredient"] for m in matched}
    unrecognised     = [p for p in parsed if p not in recognised_names]

    if not matched:
        st.error("None of the entered ingredients were recognised. Check spelling or try INCI names.")
        st.stop()

    total_count = len(parsed)

    # Core calculations
    compat        = calculate_skin_match_score(matched, skin_type.lower(), total_count)
    overall       = calculate_overall_formula_score(matched, total_count)
    compat_score  = compat["score"]
    overall_score = overall["score"]
    verdict       = compat["verdict"]
    coverage      = compat["coverage"]["coverage"]

    risk       = analyze_risk(matched, skin_type=skin_type.lower())
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

    primary_type, secondary_types = detect_formula_type(matched)
    strength_meter   = build_strength_meter(matched)
    addition_reasons = get_addition_reasons(additions)
    comparison_rows  = calculate_skin_type_comparison(matched, total_count)   # NEW


    # ═══════════════════════════════════════════════════════════════
    # SECTION 1 — VERDICT BANNER
    # ═══════════════════════════════════════════════════════════════
    css_class = _banner_class(compat_score)
    st.markdown(f"""
    <div class="verdict-banner {css_class}">
      <div class="vb-text">
        <div class="vb-label">Formula Verdict</div>
        <div class="vb-main">{verdict} for {skin_type} Skin</div>
        <div class="vb-score">Compatibility Score: {compat_score} / 100</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # SECTION 2 — FORMULA HEALTH BADGES
    # Coverage removed from here — lives in Scoring Methodology only
    # "Formula Quality" renamed to "Balanced Formula Score"
    # ═══════════════════════════════════════════════════════════════
    sc  = _score_color_class(compat_score)
    osc = _score_color_class(overall_score)
    rc  = {"Low": "fh-green", "Moderate": "fh-orange", "High": "fh-red"}.get(risk_label, "fh-neutral")

    st.markdown(f"""
    <div class="fh-grid">
      <div class="fh-item">
        <div class="fh-lbl">Compatibility</div>
        <div class="fh-val {sc}">{round(compat_score)} / 100</div>
      </div>
      <div class="fh-item">
        <div class="fh-lbl">Balanced Formula Score</div>
        <div class="fh-val {osc}">{round(overall_score)} / 100</div>
      </div>
      <div class="fh-item">
        <div class="fh-lbl">Risk Profile</div>
        <div class="fh-val {rc}">{risk_label}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='sf-divider'>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # SECTION 3 — SKIN TYPE COMPARISON  (NEW)
    # ═══════════════════════════════════════════════════════════════
    col_comp, col_comp_side = st.columns([1.6, 1])

    with col_comp:
        st.markdown('<p class="sf-section-title">Skin Type Compatibility</p>',
                    unsafe_allow_html=True)
        table_html = render_skin_type_comparison(comparison_rows, skin_type)
        st.markdown(f'<div class="sf-card" style="padding:16px 20px;">{table_html}</div>',
                    unsafe_allow_html=True)

    with col_comp_side:
        st.markdown('<p class="sf-section-title">Best Suited For</p>',
                    unsafe_allow_html=True)

        best      = comparison_rows[0]
        second    = comparison_rows[1] if len(comparison_rows) > 1 else None

        best_html  = f'<div style="margin-bottom:16px;">'
        best_html += f'<div style="font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase;color:#555;margin-bottom:6px;">Primary Match</div>'
        best_html += f'<div style="font-size:1.3rem;font-weight:700;color:{best["color"]}">✓ {best["skin_type"]} Skin</div>'
        best_html += f'<div style="font-size:0.82rem;color:#555;margin-top:3px;">{round(best["score"])} / 100 · {best["verdict"]}</div>'
        best_html += f'</div>'

        if second and second["score"] >= 62:
            best_html += f'<div>'
            best_html += f'<div style="font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase;color:#555;margin-bottom:6px;">Secondary Match</div>'
            best_html += f'<div style="font-size:1.1rem;font-weight:600;color:{second["color"]}">✓ {second["skin_type"]} Skin</div>'
            best_html += f'<div style="font-size:0.82rem;color:#555;margin-top:3px;">{round(second["score"])} / 100</div>'
            best_html += f'</div>'

        st.markdown(f'<div class="sf-card" style="padding:20px 22px;">{best_html}</div>',
                    unsafe_allow_html=True)

    st.markdown("<hr class='sf-divider'>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # SECTION 4 — FORMULA STRENGTH PROFILE
    # Now uses confidence labels; bars show display_score not raw hits
    # ═══════════════════════════════════════════════════════════════
    st.markdown('<p class="sf-section-title">Formula Strength Profile</p>',
                unsafe_allow_html=True)

    dims        = [f'{d["dimension"]}  ·  {d["label"]}' for d in reversed(strength_meter)]
    disp_scores = [d["display_score"] for d in reversed(strength_meter)]
    colors      = [d["color"]         for d in reversed(strength_meter)]

    fig = go.Figure(go.Bar(
        x=disp_scores,
        y=dims,
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[d["label"] for d in reversed(strength_meter)],
        textposition="outside",
        textfont=dict(color="#888", size=11),
        hovertemplate="%{y}: %{text}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="#1a1d27",
        plot_bgcolor="#1a1d27",
        font=dict(color="#888", family="Inter, sans-serif", size=12),
        margin=dict(l=0, r=80, t=8, b=8),
        height=240,
        xaxis=dict(
            range=[0, 130],
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

    # ═══════════════════════════════════════════════════════════════
    # SECTION 5 — INGREDIENT CARDS
    # ═══════════════════════════════════════════════════════════════
    st.markdown('<p class="sf-section-title">Ingredient Breakdown</p>', unsafe_allow_html=True)

    cards_html = '<div class="ic-grid">'
    for m in matched:
        cards_html += render_ingredient_card(m, skin_type)
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    # FIX 3: friendlier coverage message — not "Coverage 75%" but ingredient count
    if unrecognised:
        st.caption(
            f"{len(matched)} ingredient{'s' if len(matched) != 1 else ''} analysed · "
            f"{len(unrecognised)} not yet in knowledge base: "
            + ", ".join(u.title() for u in unrecognised)
        )

    st.markdown("<hr class='sf-divider'>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # SECTION 6 — RECOMMENDATION TABLE
    # ═══════════════════════════════════════════════════════════════
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
            st.markdown(f'<div class="sf-card" style="padding:16px 20px;">{inner2}</div>',
                        unsafe_allow_html=True)

    st.markdown("<hr class='sf-divider'>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # SECTION 7 — BENEFITS / CONCERNS + SUMMARY
    # ═══════════════════════════════════════════════════════════════
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

    # ═══════════════════════════════════════════════════════════════
    # SCORING METHODOLOGY — Coverage lives here now, not in top badges
    # ═══════════════════════════════════════════════════════════════
    with st.expander("Scoring Methodology"):
        st.markdown(f"""
| Component | Value | Method |
|-----------|-------|--------|
| Compatibility Score | {compat_score} / 100 | Average {skin_type.lower()} skin score (0–10) across {len(matched)} recognised ingredients, scaled ×10 then ×0.90 realism factor |
| Balanced Formula Score | {overall_score} / 100 | Same method averaged across all five skin-type columns |
| Risk Level | {risk_label} | High if ≥3 high-risk ingredients; Moderate if ≥1; Low otherwise |
| Knowledge Base Coverage | {coverage}% | {compat['coverage']['recognized_ingredients']} of {compat['coverage']['total_ingredients']} ingredients matched to knowledge base |

> Scores reflect ingredient-level data only. Concentration, pH, and manufacturing are not accounted for.
        """)