from typing import Any, Dict

import streamlit as st

from frontend.components._helpers import get_score_color, get_score_emoji


# Component max scores match backend/core/config.py SCORE_WEIGHTS.
# (Backend returns each component's score on its own scale, not 0-100.)
COMPONENTS = [
    ("Formatting", "formatting", 20, "📝"),
    ("Keywords & Skills", "keywords", 25, "🔑"),
    ("Content Quality", "content", 25, "📄"),
    ("Skill Validation", "skill_validation", 15, "✅"),
    ("ATS Compatibility", "ats_compatibility", 15, "🤖"),
]


def display_overall_score(analysis: Dict[str, Any]) -> None:
    """Big colored score card with a short interpretation line."""
    score = float(analysis.get("ATS_score", analysis.get("ats_score", 0)))
    interpretation = analysis.get("interpretation", "")
    text_color, bg_color = get_score_color(score)
    emoji = get_score_emoji(score)

    st.markdown("## 📊 Analysis Results")
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown(
            f"""<div class="metric-card" style="text-align:center; padding:2.5rem 1.5rem; background: var(--glass-bg); border-radius: var(--radius-lg); box-shadow: var(--glass-shadow); border: 2px solid {text_color}22; position: relative;">
<div style="font-size: 5rem; line-height: 1; font-weight: 800; color: {text_color}; margin-bottom: 0.5rem; text-shadow: 0 4px 20px {text_color}33;">{score:.0f}<span style="font-size: 2rem; font-weight: 500; opacity: 0.7;">/100</span></div>
<div style="display: inline-flex; align-items: center; gap: 0.5rem; background: {bg_color}; color: {text_color}; padding: 0.4rem 1rem; border-radius: var(--radius-full); font-weight: 600; font-size: 0.95rem; margin-bottom: 1rem; border: 1px solid {text_color}15;"><span>{emoji}</span> Overall ATS Score</div>
<p style="color: var(--text-secondary); margin: 0.5rem 0 0; font-size: 1.05rem; line-height: 1.5; font-weight: 500;">{interpretation}</p>
</div>""",
            unsafe_allow_html=True,
        )


def display_score_breakdown(analysis: Dict[str, Any]) -> None:
    """Five progress bars, one per scoring component."""
    component_scores = analysis.get("component_scores") or {}
    st.markdown("### 📈 Score Breakdown")

    left, right = st.columns(2)
    for i, (label, key, max_score, icon) in enumerate(COMPONENTS):
        value = float(component_scores.get(key, 0))
        percentage = value / max_score if max_score else 0
        
        # Match class names from styles.css
        bar_class = (
            "progress-bar-success" if percentage >= 0.8 
            else "progress-bar-warning" if percentage >= 0.6 
            else "progress-bar-danger"
        )

        with left if i % 2 == 0 else right:
            st.markdown(
                f"""<div class="metric-card" style="padding: 1.25rem; margin-bottom: 1rem; border-radius: var(--radius-md); border: 1px solid var(--border-color); background: var(--background-white);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
<span style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">{icon} {label}</span>
<span style="font-weight: 700; color: var(--text-primary); font-size: 0.95rem;">{value:.0f} <span style="font-weight: 500; color: var(--text-muted); font-size: 0.8rem;">/ {max_score}</span></span>
</div>
<div class="progress-container" style="height: 8px; background: var(--border-light);">
<div class="progress-bar {bar_class}" style="width: {percentage * 100}%;"></div>
</div>
</div>""",
                unsafe_allow_html=True,
            )
