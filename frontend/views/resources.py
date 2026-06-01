import streamlit as st


def render():
    """Render the resources page"""

    st.title("📚 Resources & Tips")
    st.markdown("Learn how to optimize your resume for modern Applicant Tracking Systems.")
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ATS Tips
    st.markdown("## 🎯 ATS Optimization Guidelines")
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """<div class="metric-card" style="border-left: 5px solid var(--success-color); background: rgba(16, 185, 129, 0.04); height: 100%; padding: 1.5rem; border-top: 1px solid var(--glass-border); border-right: 1px solid var(--glass-border); border-bottom: 1px solid var(--glass-border);">
<h3 style="color: var(--success-color); font-weight: 700; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;"><span>✅</span> Do's</h3>
<ul style="color: var(--text-secondary); line-height: 1.8; font-size: 0.95rem; padding-left: 1.25rem; margin: 0;">
<li>Use standard, clear section headings (e.g. Experience, Education, Skills)</li>
<li>Integrate high-impact keywords directly from the target Job Description</li>
<li>Keep your formatting clean, standard, and strictly single-column</li>
<li>Explicitly list your core skills with clear, recognizable titles</li>
<li>Quantify your professional achievements with concrete numbers and data</li>
<li>Stick to modern, highly readable fonts (Arial, Calibri, Outfit, Inter)</li>
<li>Save and upload your documents in standard PDF or DOCX formats</li>
</ul>
</div>""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """<div class="metric-card" style="border-left: 5px solid var(--danger-color); background: rgba(239, 68, 68, 0.04); height: 100%; padding: 1.5rem; border-top: 1px solid var(--glass-border); border-right: 1px solid var(--glass-border); border-bottom: 1px solid var(--glass-border);">
<h3 style="color: var(--danger-color); font-weight: 700; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;"><span>❌</span> Don'ts</h3>
<ul style="color: var(--text-secondary); line-height: 1.8; font-size: 0.95rem; padding-left: 1.25rem; margin: 0;">
<li>Avoid complex multi-layered tables, grids, and isolated text boxes</li>
<li>Do not place essential contact info inside page headers or footers</li>
<li>Steer clear of graphics, charts, logos, and profile photographs</li>
<li>Avoid non-standard, decorative, or highly stylized custom fonts</li>
<li>Do not use multi-column layouts that confuse system parsers</li>
<li>Never stuff keywords unnaturally or list items without real context</li>
<li>Avoid using niche acronyms without spelling their meaning first</li>
</ul>
</div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Common ATS Keywords
    st.markdown("## 🔑 Common ATS Keywords by Industry")
    st.caption("Common ATS keywords that grab parsers' attention.")

    tab1, tab2, tab3 = st.tabs(["💻 Tech", "💼 Business", "🎨 Creative"])

    with tab1:
        st.markdown("##### 💻 Technology & Software Engineering")
        st.markdown(
            """<div style="display: flex; flex-wrap: wrap; gap: 0.5rem; padding: 0.5rem 0;">
<div class="skill-tag skill-tag-neutral">Python / Java / C++</div>
<div class="skill-tag skill-tag-neutral">JavaScript / TypeScript</div>
<div class="skill-tag skill-tag-neutral">React / Angular / Vue</div>
<div class="skill-tag skill-tag-neutral">Django / FastAPI / Spring</div>
<div class="skill-tag skill-tag-neutral">Docker / Kubernetes</div>
<div class="skill-tag skill-tag-neutral">Agile / Scrum / Kanban</div>
<div class="skill-tag skill-tag-neutral">CI/CD Pipelines</div>
<div class="skill-tag skill-tag-neutral">Machine Learning / AI</div>
<div class="skill-tag skill-tag-neutral">RESTful APIs / GraphQL</div>
<div class="skill-tag skill-tag-neutral">Cloud Solutions (AWS/GCP)</div>
<div class="skill-tag skill-tag-neutral">SQL / NoSQL Databases</div>
<div class="skill-tag skill-tag-neutral">System Architecture</div>
</div>""",
            unsafe_allow_html=True
        )

    with tab2:
        st.markdown("##### 💼 Business & Administration Management")
        st.markdown(
            """<div style="display: flex; flex-wrap: wrap; gap: 0.5rem; padding: 0.5rem 0;">
<div class="skill-tag skill-tag-neutral">Project Management</div>
<div class="skill-tag skill-tag-neutral">Stakeholder Management</div>
<div class="skill-tag skill-tag-neutral">Budget Allocation & Optimization</div>
<div class="skill-tag skill-tag-neutral">Strategic Planning & Execution</div>
<div class="skill-tag skill-tag-neutral">Cross-functional Leadership</div>
<div class="skill-tag skill-tag-neutral">Business Development</div>
<div class="skill-tag skill-tag-neutral">Quantitative Data Analytics</div>
<div class="skill-tag skill-tag-neutral">Resource Planning</div>
<div class="skill-tag skill-tag-neutral">Risk Assessment & Mitigation</div>
<div class="skill-tag skill-tag-neutral">Operational Efficiency</div>
<div class="skill-tag skill-tag-neutral">Change Management</div>
<div class="skill-tag skill-tag-neutral">KPI Performance Tracking</div>
</div>""",
            unsafe_allow_html=True
        )

    with tab3:
        st.markdown("##### 🎨 Creative & Digital Design")
        st.markdown(
            """<div style="display: flex; flex-wrap: wrap; gap: 0.5rem; padding: 0.5rem 0;">
<div class="skill-tag skill-tag-neutral">Adobe Creative Cloud</div>
<div class="skill-tag skill-tag-neutral">UI/UX Interaction Design</div>
<div class="skill-tag skill-tag-neutral">Wireframing & Prototyping</div>
<div class="skill-tag skill-tag-neutral">Figma / Sketch / Adobe XD</div>
<div class="skill-tag skill-tag-neutral">Brand Identity Strategy</div>
<div class="skill-tag skill-tag-neutral">Visual Communication</div>
<div class="skill-tag skill-tag-neutral">Typography Design</div>
<div class="skill-tag skill-tag-neutral">Digital Graphic Design</div>
<div class="skill-tag skill-tag-neutral">Creative Brief Development</div>
<div class="skill-tag skill-tag-neutral">Art Direction</div>
<div class="skill-tag skill-tag-neutral">Design System Governance</div>
<div class="skill-tag skill-tag-neutral">Responsive Layout Design</div>
</div>""",
            unsafe_allow_html=True
        )

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Resume Templates
    st.markdown("## 📄 ATS-Friendly Resume Templates")
    st.info("Coming soon: High-converting, professionally styled ATS-optimized resume templates.")
