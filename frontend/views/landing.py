import streamlit as st


def render():
    # Hero Section
    st.markdown(
        """<div class="card-gradient" style="padding: 3.5rem 2rem; text-align: center; border-radius: var(--radius-xl); margin-bottom: 2.5rem; position: relative; overflow: hidden;">
<div style="position: absolute; top: -50px; left: -50px; width: 180px; height: 180px; border-radius: 50%; background: rgba(255,255,255,0.12); filter: blur(25px);"></div>
<div style="position: absolute; bottom: -60px; right: -60px; width: 220px; height: 220px; border-radius: 50%; background: rgba(255,255,255,0.08); filter: blur(35px);"></div>
<h1 style="color: white !important; font-size: 3.2rem; font-weight: 800; margin-bottom: 0.75rem; letter-spacing: -0.03em; text-shadow: 0 4px 12px rgba(0,0,0,0.15);">🧠 HireMind: ATS Resume Scorer</h1>
<h3 style="color: rgba(255, 255, 255, 0.95) !important; font-size: 1.45rem; font-weight: 400; margin-bottom: 1.5rem; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">Optimize Your Resume for Applicant Tracking Systems</h3>
<p style="color: rgba(255, 255, 255, 0.85) !important; font-size: 1.1rem; max-width: 750px; margin: 0 auto 2.5rem; line-height: 1.6; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">Get instant feedback on your resume's ATS compatibility and verify your real skill coverage with state-of-the-art semantic AI models.</p>
</div>""",
        unsafe_allow_html=True,
    )

    # CTA Button
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "🚀 Start Analyzing Your Resume", use_container_width=True, type="primary"
        ):
            st.session_state.current_view = "scorer"
            st.rerun()

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Features Overview
    st.markdown(
        "<h2 style='text-align: center; margin-bottom: 2rem; font-weight: 700;'>✨ Key Capabilities</h2>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """<div class="feature-card">
<div class="feature-icon">📊</div>
<div class="feature-title">Comprehensive Scoring</div>
<div class="feature-description">
Get detailed metrics evaluated across 5 key dimensions:
<ul style="margin-top: 0.5rem; padding-left: 1.2rem; line-height: 1.6;">
<li>📝 Formatting (20%)</li>
<li>🔑 Keywords &amp; Skills (25%)</li>
<li>📄 Content Quality (25%)</li>
<li>✅ Skill Validation (15%)</li>
<li>🤖 ATS Compatibility (15%)</li>
</ul>
</div>
</div>""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """<div class="feature-card">
<div class="feature-icon">🔍</div>
<div class="feature-title">Semantic Skill Validation</div>
<div class="feature-description">
Verify that your claimed skills are genuinely demonstrated in your projects and work history using deep contextual AI analysis.
<br/><br/>
<strong style="color: var(--primary-color);">🚀 Stop using empty keyword lists!</strong>
</div>
</div>""",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """<div class="feature-card">
<div class="feature-icon">🛡️</div>
<div class="feature-title">Privacy-First AI</div>
<div class="feature-description">
All analysis and parsing runs locally with offline models. Your sensitive career, contact, and project history never leaves your system.
<br/><br/>
<strong style="color: var(--success-color);">🔒 100% Private &amp; Secure</strong>
</div>
</div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # How It Works
    st.markdown(
        "<h2 style='text-align: center; margin-bottom: 2.5rem; font-weight: 700;'>🚀 How It Works</h2>",
        unsafe_allow_html=True
    )

    step1, step2, step3 = st.columns(3)

    with step1:
        st.markdown(
            """<div class="step-item card-elevated" style="height: 100%;">
<div class="step-number" style="background: var(--primary-color); color: white; margin: 0 auto 1rem; width: 45px; height: 45px; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-weight: 700; box-shadow: 0 4px 10px rgba(99, 102, 241, 0.25);">1</div>
<div class="feature-title" style="text-align: center;">Upload Resume</div>
<div class="feature-description" style="text-align: center;">Upload your resume. We support PDF, DOC, and DOCX formats up to 5MB.</div>
</div>""",
            unsafe_allow_html=True,
        )

    with step2:
        st.markdown(
            """<div class="step-item card-elevated" style="height: 100%;">
<div class="step-number" style="background: var(--primary-color); color: white; margin: 0 auto 1rem; width: 45px; height: 45px; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-weight: 700; box-shadow: 0 4px 10px rgba(99, 102, 241, 0.25);">2</div>
<div class="feature-title" style="text-align: center;">AI Analysis</div>
<div class="feature-description" style="text-align: center;">(Optional) Paste a job description to perform targeted keyword alignment and gap analyses.</div>
</div>""",
            unsafe_allow_html=True,
        )

    with step3:
        st.markdown(
            """<div class="step-item card-elevated" style="height: 100%;">
<div class="step-number" style="background: var(--success-color); color: white; margin: 0 auto 1rem; width: 45px; height: 45px; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-weight: 700; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.25);">3</div>
<div class="feature-title" style="text-align: center;">Optimize &amp; Excel</div>
<div class="feature-description" style="text-align: center;">Receive clear, actionable feedback, custom recommendations, and ATS tips to maximize impact.</div>
</div>""",
            unsafe_allow_html=True,
        )
    st.markdown("<br/>", unsafe_allow_html=True)
