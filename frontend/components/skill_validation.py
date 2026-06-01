from typing import Any, Dict

import streamlit as st


def display_skill_validation(analysis: Dict[str, Any]) -> None:
    details = analysis.get("skill_validation_details") or {}
    validated = details.get("validated", [])
    unvalidated = details.get("unvalidated", [])
    total = details.get("total", len(validated) + len(unvalidated))
    pct = details.get("validation_pct", 0.0)

    st.markdown("### ✅ Skill Validation")

    if total == 0:
        st.info("No skills detected on the resume.")
        return

    c1, c2, c3 = st.columns(3)
    c1.markdown(
        f"""<div class="metric-card" style="text-align: center; padding: 1.25rem;">
<div style="font-size: 2.25rem; font-weight: 800; color: var(--primary-color);">{total}</div>
<div style="font-size: 0.85rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.25rem;">Total Skills</div>
</div>""",
        unsafe_allow_html=True
    )
    c2.markdown(
        f"""<div class="metric-card" style="text-align: center; padding: 1.25rem;">
<div style="font-size: 2.25rem; font-weight: 800; color: var(--success-color);">{len(validated)}</div>
<div style="font-size: 0.85rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.25rem;">Validated</div>
</div>""",
        unsafe_allow_html=True
    )
    c3.markdown(
        f"""<div class="metric-card" style="text-align: center; padding: 1.25rem;">
<div style="font-size: 2.25rem; font-weight: 800; color: var(--info-color);">{pct:.0f}%</div>
<div style="font-size: 0.85rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.25rem;">Validation %</div>
</div>""",
        unsafe_allow_html=True
    )

    st.markdown("<br/>", unsafe_allow_html=True)
    st.progress(min(max(pct / 100.0, 0.0), 1.0))

    if validated:
        with st.expander(f"✅ Validated skills ({len(validated)})", expanded=True):
            st.caption("These skills are validated with evidence in your experience and project sections.")
            
            tags_html = "<div style='display: flex; flex-wrap: wrap; gap: 0.5rem; padding: 0.5rem 0;'>"
            for entry in validated:
                skill = entry.get("skill", "?")
                projects = entry.get("projects", []) or []
                similarity = entry.get("similarity")

                project_text = ", ".join(projects[:2]) if projects else "experience section"
                sim_text = f" ({similarity * 100:.0f}% match)" if isinstance(similarity, (int, float)) else ""
                
                tags_html += f"""<div class="skill-tag skill-tag-validated" title="Demonstrated in: {project_text}">{skill}{sim_text}</div>"""
            tags_html += "</div>"
            st.markdown(tags_html, unsafe_allow_html=True)

    if unvalidated:
        with st.expander(f"⚠️ Unvalidated skills ({len(unvalidated)})", expanded=False):
            st.caption("These skills are listed in your skills section but lack contextual evidence in your experience bullet points.")
            
            tags_html = "<div style='display: flex; flex-wrap: wrap; gap: 0.5rem; padding: 0.5rem 0;'>"
            for skill in unvalidated:
                tags_html += f"""<div class="skill-tag skill-tag-unvalidated">{skill}</div>"""
            tags_html += "</div>"
            st.markdown(tags_html, unsafe_allow_html=True)
