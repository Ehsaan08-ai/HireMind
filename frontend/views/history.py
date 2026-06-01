import requests
import streamlit as st

from frontend.services import api_client
from frontend.components._helpers import get_score_color


def _show_backend_error(exc: Exception) -> None:
    if isinstance(exc, requests.ConnectionError):
        st.error("Could not reach the backend. Is it running on port 8000?")
    elif isinstance(exc, requests.HTTPError) and exc.response is not None:
        st.error(f"Backend returned {exc.response.status_code}: {exc.response.text}")
    else:
        st.error(f"Unexpected error: {exc}")


def render() -> None:
    st.title("📊 Analysis History")
    st.markdown("Past analyses saved against your account.")

    access_token = st.session_state.get("access_token")
    if not access_token:
        st.warning("⚠️ Sign in from the sidebar to view your history.")
        return

    try:
        history = api_client.get_history(access_token)
    except requests.RequestException as exc:
        _show_backend_error(exc)
        return

    if not history:
        st.info(
            "No analyses yet for this account. Run a scoring on the ATS Scorer page first."
        )
        if st.button("🎯 Go to ATS Scorer"):
            st.session_state.current_view = "scorer"
            st.rerun()
        return

    st.markdown(f"**Total analyses:** {len(history)}")
    st.markdown("---")

    for idx, entry in enumerate(history):
        filename = entry.get("filename", "resume")
        ats_score = float(entry.get("ats_score", 0))
        created_at = entry.get("created_at", "")
        analysis = entry.get("analysis_result", {}) or {}

        component_scores = analysis.get("component_scores", {}) or {}
        jd_comparison = analysis.get("jd_comparison") or analysis.get(
            "jd_match_analysis"
        )

        score_text_color, score_bg_color = get_score_color(ats_score)
        
        # Elegant expander banner title
        expander_title = f"📄 {filename}  •  Score: {ats_score:.0f}/100  •  {created_at}"
        
        with st.expander(expander_title):
            st.markdown(
                f"""<div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; background: {score_bg_color}; padding: 1rem; border-radius: var(--radius-md); border: 1px solid {score_text_color}15;">
<div style="font-size: 2.25rem; font-weight: 800; color: {score_text_color};">{ats_score:.0f}</div>
<div>
<div style="font-weight: 700; font-size: 0.95rem; color: var(--text-primary);">Overall ATS Score</div>
<div style="font-size: 0.8rem; color: var(--text-muted);">Completed parsing successfully</div>
</div>
{"<div style='margin-left: auto; font-weight: 700; font-size: 0.9rem; color: var(--primary-color); background: rgba(99, 102, 241, 0.08); padding: 0.4rem 0.8rem; border-radius: var(--radius-full); border: 1px solid rgba(99, 102, 241, 0.15);'>🎯 Job Description Match: " + f"{jd_comparison.get('match_percentage', 0):.0f}%" + "</div>" if jd_comparison else ""}
</div>""",
                unsafe_allow_html=True
            )

            c1, c2, c3, c4, c5 = st.columns(5)
            
            c1.markdown(
                f"""<div class="metric-card" style="text-align: center; padding: 1rem; background: var(--background-white); border: 1px solid var(--border-color);">
<div style="font-size: 1.5rem; font-weight: 800; color: var(--text-primary);">{component_scores.get('formatting', 0):.0f}<span style="font-size:0.75rem; font-weight:500; color:var(--text-muted);">/20</span></div>
<div style="font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; margin-top: 0.25rem;">📝 Format</div>
</div>""",
                unsafe_allow_html=True
            )
            c2.markdown(
                f"""<div class="metric-card" style="text-align: center; padding: 1rem; background: var(--background-white); border: 1px solid var(--border-color);">
<div style="font-size: 1.5rem; font-weight: 800; color: var(--text-primary);">{component_scores.get('keywords', 0):.0f}<span style="font-size:0.75rem; font-weight:500; color:var(--text-muted);">/25</span></div>
<div style="font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; margin-top: 0.25rem;">🔑 Keywords</div>
</div>""",
                unsafe_allow_html=True
            )
            c3.markdown(
                f"""<div class="metric-card" style="text-align: center; padding: 1rem; background: var(--background-white); border: 1px solid var(--border-color);">
<div style="font-size: 1.5rem; font-weight: 800; color: var(--text-primary);">{component_scores.get('content', 0):.0f}<span style="font-size:0.75rem; font-weight:500; color:var(--text-muted);">/25</span></div>
<div style="font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; margin-top: 0.25rem;">📄 Quality</div>
</div>""",
                unsafe_allow_html=True
            )
            c4.markdown(
                f"""<div class="metric-card" style="text-align: center; padding: 1rem; background: var(--background-white); border: 1px solid var(--border-color);">
<div style="font-size: 1.5rem; font-weight: 800; color: var(--text-primary);">{component_scores.get('skill_validation', 0):.0f}<span style="font-size:0.75rem; font-weight:500; color:var(--text-muted);">/15</span></div>
<div style="font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; margin-top: 0.25rem;">✅ Skills</div>
</div>""",
                unsafe_allow_html=True
            )
            c5.markdown(
                f"""<div class="metric-card" style="text-align: center; padding: 1rem; background: var(--background-white); border: 1px solid var(--border-color);">
<div style="font-size: 1.5rem; font-weight: 800; color: var(--text-primary);">{component_scores.get('ats_compatibility', 0):.0f}<span style="font-size:0.75rem; font-weight:500; color:var(--text-muted);">/15</span></div>
<div style="font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; margin-top: 0.25rem;">🤖 ATS Comp</div>
</div>""",
                unsafe_allow_html=True
            )

            st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
            
            c_btn, _ = st.columns([1, 4])
            with c_btn:
                entry_id = entry.get("id")
                if entry_id:
                    if st.button("🗑️ Delete Entry", key=f"delete_{idx}", type="secondary", use_container_width=True):
                        try:
                            api_client.delete_history_entry(str(entry_id), access_token)
                            st.success("Deleted.")
                            st.rerun()
                        except requests.RequestException as exc:
                            _show_backend_error(exc)
