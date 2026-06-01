from typing import Any, Dict, List

import streamlit as st

from frontend.components._helpers import get_severity_style


SEVERITY_ORDER = ["critical", "high", "medium", "low"]


def _group_by_severity(issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {level: [] for level in SEVERITY_ORDER}
    for issue in issues:
        level = (issue.get("severity_level") or "low").lower()
        grouped.setdefault(level, []).append(issue)
    return grouped


def _render_issue(issue: Dict[str, Any]) -> None:
    icon, text_color, bg_color = get_severity_style(issue.get("severity_level"))
    title = issue.get("issue_title", "Untitled issue")
    impact = issue.get("ats_impact", "")
    explanation = issue.get("explanation", "")
    where = issue.get("where_it_appears", "")
    how_to_fix = issue.get("how_to_fix", "")
    action_items = issue.get("action_items") or []
    example = issue.get("example_improvement", "")

    st.markdown(
        f"""<div class="metric-card" style="border-left: 5px solid {text_color}; background: {bg_color}; padding: 1rem 1.25rem; margin-bottom: 0.75rem; border-radius: var(--radius-md); box-shadow: var(--shadow-sm); border-top: 1px solid var(--glass-border); border-right: 1px solid var(--glass-border); border-bottom: 1px solid var(--glass-border);">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
<span style="font-weight: 700; color: {text_color}; font-size: 1.05rem;">{icon} {title}</span>
<span style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); background: var(--background-white); padding: 0.25rem 0.6rem; border-radius: var(--radius-full); border: 1px solid var(--border-color);">{impact}</span>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    with st.expander("🔍 View Analysis & Action Items", expanded=False):
        if explanation:
            st.markdown(f"💡 **Explanation:** {explanation}")
        if where:
            st.markdown(f"📍 **Where it appears:** {where}")
        if how_to_fix:
            st.markdown(f"🔧 **How to fix:** {how_to_fix}")
        if action_items:
            st.markdown("📋 **Recommended action items:**")
            for item in action_items:
                st.markdown(f"- {item}")
        if example:
            st.markdown("✨ **Example improvement:**")
            st.code(example, language="text")


def display_detailed_feedback(analysis: Dict[str, Any]) -> None:
    issues = analysis.get("detailed_feedback") or []
    if not issues:
        return  # backend produce no per-issue feedback this run

    st.markdown("### 🔍 Detailed Feedback")
    st.caption(f"{len(issues)} issue(s) flagged - grouped by severity.")

    grouped = _group_by_severity(issues)
    for level in SEVERITY_ORDER:
        items = grouped.get(level, [])
        if not items:
            continue
        # Fixed critical TypeError bug where `level` string was called as a function: level(items) -> len(items)
        st.markdown(f"#### {level.title()} ({len(items)})")
        for issue in items:
            _render_issue(issue)
