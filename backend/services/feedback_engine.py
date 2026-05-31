import re
from typing import List, Optional, Dict, Any
from backend.models.schemas import IssueDetail

def analyze_issues(
        resume_text: str,
        parsed_resume: Dict,
        skills: List[str],
        projects: List[Dict],
        action_verbs: List[str],
        skill_validation: Dict,
        scores: Dict,
        contact_info: Optional[Dict] = None,
) -> List[IssueDetail]:
    
    detected: List[IssueDetail] = []

    # Unpack frequently-used structure fields once at the top

    exp_entries = [e for e in parsed_resume.get('experience', []) if isinstance(e, dict)]
    edu_entries = [e for e in parsed_resume.get('education', []) if isinstance(e, dict)]
    proj_entries = [p for p in parsed_resume.get('projects', []) if isinstance(p, dict)]
    summary = (parsed_resume.get('professional_summary') or '').strip() # Handles None to prevent string concatenation errors

    # Build a combined experience text for regex-based checks that still need text
    experience_text = '\n'.join(e.get('description', '') for e in exp_entries).strip()

    # 1. Missing project section
    resume_lower = resume_text.lower()
    has_projects_signal = any(kw in resume_lower for kw in [
        'project', 'github.com', 'deployed', 'built a', 'developed a',
        'created a', 'implemented a', 'live demo', 'tech stack'
    ])

    if not proj_entries and len(projects) == 0 and not has_projects_signal:
        detected.append(IssueDetail(
            issue_title="Missing Projects Section",
            severity_level="High",
            ats_impact="High",
            explanation=(
                "Your resume does not have a dedicated Projects section. "
                "ATS systems and recruiters look for concrete projects to validate "
                "that your listed skills have been applied in practice."
            ),
            
            where_it_appears="Resume structure - no 'Projects' header was detected",
            how_to_fix=(
                "Add a Projects section to your resume. Include at least 2-3 projects that demonstrate "
                "your skills in action. For each project, provide a title, a brief description, the technologies used, "
                "and any measurable outcomes or achievements."
            ),

            action_items=[
                "Add a 'PROJECTS' section heading after your Experience section",
                "Include 2-3 projects (personal, academic, or open-source)",
                "For each project, provide: Title, Description, Technologies Used, Outcomes/Achievements",
                "Example: 'Personal Portfolio Website - Developed a responsive portfolio website using React and Node.js, showcasing my projects and skills. Achieved 500+ visits in the first month.'"
                "Link to Github or live demos if available"
            ],

            example_improvement=(
                "Add:\n"
                "PROJECTS\n"
                "• Personal Portfolio Website - Developed a responsive portfolio website using React and Node.js,"
                "showcasing my projects and skills. Achieved 500+ visits in the first month. [GitHub Link]\n"
                "• ML Sentiment Analyzer - Created a machine learning model to analyze sentiment in social media posts using Python and scikit-learn." 
                "Achieved 85% accuracy on test data. [GitHub Link]\n"
            ),
        ))

    # 2. Missing experience section
    has_experience_signal = any(kw in resume_lower for kw in [
        'experience', 'worked at', 'employed at', 'interned at', 'freelanced for',
        'contracted with', 'full-time at', 'part-time at', 'intern', 'job', 'role', 'position',
        'engineer', 'developer', 'analyst', 'manager', 'consultant', 'assistant', 'coordinator',
    ])

    if not exp_entries and not has_experience_signal:
        detected.append(IssueDetail(
            issue_title="Missing Work Experience Section",
            severity_level="High",
            ats_impact="High",
            explanation=(
                "Your resume does not have a dedicated Experience section. "
                "ATS systems and recruiters look for work experience to assess your practical application of skills and your career progression."
            ),
            
            where_it_appears="Resume structure - no 'Experience' header was detected",
            how_to_fix=(
                "Add an Experience section to your resume. Include any relevant internships, part-time jobs, freelance work, or volunteer positions. For each entry, provide the company name, your role/title, dates of employment, and a brief description of your responsibilities and achievements."
            ),

            action_items=[
                "Add an 'EXPERIENCE' section heading after your Professional Summary",
                "Include any relevant work experience (internships, part-time jobs, freelance work, volunteer positions)",
                "For each entry, provide: Company Name, Role/Title, Dates of Employment, Responsibilities/Achievements",
                "Example: 'Software Engineering Intern at Tech Company - Developed a feature that improved user engagement by 15% using React and Node.js. [Dates]'"
            ],

            example_improvement=(
                "Add:\n"
                "EXPERIENCE\n"
                "• Software Engineering Intern at Tech Company - Developed a feature that improved user engagement by 15% using React and Node.js. [Dates]\n"
                "• Freelance Web Developer - Built responsive websites for small businesses using HTML, CSS, and JavaScript. [Dates]\n"
            ),
        ))

    # 3. Missing education section
    has_education_signal = any(kw in resume_lower for kw in [
        'education', 'degree', 'university', 'college', 'school', 'graduated from',
        'bachelor', 'master', 'phd', 'associate', 'high school', 'b.tech', 'bsc', 'msc', 'ba', 'ma', 'bs', 'ms',
        'class of', 'diploma', 'batch of', 'graduation year', 'gpa'
    ])

    if not edu_entries and not has_education_signal:
        detected.append(IssueDetail(
            issue_title="Missing Education Section",
            severity_level="Medium",
            ats_impact="Medium",
            explanation=(
                "Your resume does not have a dedicated Education section. "
                "ATS systems and recruiters look for educational background to assess your qualifications and foundational knowledge."
            ),
            
            where_it_appears="Resume structure - no 'Education' header was detected",
            how_to_fix=(
                "Add an Education section to your resume. Include your highest degree, the institution you attended, your graduation year, and any relevant coursework or honors."
            ),

            action_items=[
                "Add an 'EDUCATION' section heading after your Experience section",
                "Include your highest degree (e.g., Bachelor of Science in Computer Science)",
                "Include the institution name (e.g., University of XYZ)",
                "Include graduation year (e.g., Graduated: 2023)",
                "Optionally include relevant coursework, honors, or GPA if it strengthens your candidacy"
            ],

            example_improvement=(
                "Add:\n"
                "EDUCATION\n"
                "• Bachelor of Science in Computer Science, University of XYZ, Graduated: 2023\n"
                "Relevant Coursework: Data Structures, Algorithms, Database Systems\n"
                "Honors: Dean's List for 6 semesters\n"
            ),
        ))

    # 4. Missing Skills Section
    if not parsed_resume.get('skills') and len(skills) < 3:
        detected.append(IssueDetail(
            issue_title="Missing Skills Section",
            severity_level="High",
            ats_impact="High",
            explanation=(
                f"Only {len(skills)} skill(s) were detected. ATS systems "
                "rely heavily on keyword matching from a dedicated Skills section. "
                "Without clear skills listed, your resume may fail automated filters."
            ),
            
            where_it_appears="Skills Section - either missing or contains fewer than 3 skills",
            how_to_fix=(
                "Add a Skills section to your resume. Include a list of relevant technical and soft skills that are pertinent to the jobs you are applying for."
            ),

            action_items=[
                "Add a 'SKILLS' section heading after your Education section",
                "Include a list of relevant technical and soft skills (e.g., Programming Languages, Tools, Communication, Leadership)",
                "Tailor your skills list to match the requirements of the jobs you are applying for"
            ],

            example_improvement=(
                "Add:\n"
                "SKILLS\n"
                "• Programming Languages: Python, Java, C++\n"
                "• Tools: Git, Docker, AWS\n"
                "• Soft Skills: Communication, Teamwork, Problem-Solving\n"
            ),
        ))

    # 5. Skills Lack Supporting Evidence
    unvalidated = skill_validation.get('unvalidated_skills', [])
    validated = skill_validation.get('validated_skills', [])
    total_skills = len(unvalidated) + len(validated)

    if total_skills > 0 and len(unvalidated) > len(validated):
        unsupported_list = ', '.join(unvalidated[:8])
        pct_unvalidated = round((len(unvalidated) / total_skills) * 100)
        action_items_skills = [
            f"Mention '{skill}' in a project or experience bullet point" for skill in unvalidated[:5]
        ]

        action_items_skills.append("Remove skills you cannot demonstrate with any experience or projects")
        if len(unvalidated) > 5:
            action_items_skills.append(f"({len(unvalidated) - 5} more unvalidated skills - review each one)")

        detected.append(IssueDetail(
            issue_title="Most Skills Lack Supporting Evidence",
            severity_level="Moderate",
            ats_impact="High",
            explanation=(
                f"You have {len(unvalidated)} skill(s) that were not supported by any experience or projects in your resume. "
                f"ATS systems and recruiters look for evidence that you have applied the skills you list. "
                f"Having a high percentage of unvalidated skills ({pct_unvalidated}%) can significantly weaken your resume's impact."
            ),
            
            where_it_appears=f"This skills have no supporting context: {unsupported_list}",
            how_to_fix=(
                "For each skill in your Skills section, ensure it appears atleast"
                "once in a project description or experience bullet point."
                "Describe how and where you used that technology."
            ),

            action_items=action_items_skills,

            example_improvement=(
                f"Your skill '{unvalidated[0]}' has no supporting evidence.\n\n"
                f"Fix: Add to a project or experience bullet:\n"
                f"'Built a data pipeline using {unvalidated[0]} that processed "
                "10K records daily, reducing manual effort by 60%.'"
            ),
        ))

    # 6. Weak Action Verbs
    description_lines = [
        line.strip()
        for exp in exp_entries
        for line in exp.get('description', '').split('\n')
        if line.strip()
    ]

    if len(description_lines) > 3 and len(action_verbs) < 3:
        detected.append(IssueDetail(
            issue_title="Bullet points lack strong action verbs",
            severity_level="Moderate",
            ats_impact="Medium",
            explanation=(
                f"Your experience section has {len(description_lines)} bullet points but "
                f"only {len(action_verbs)} start with strong action verbs. "
                "ATS systems and recruiters favor bullets that begin with verbs like "
                "'Developed', 'Implemented', 'Designed', 'Optimized'."
            ),
            
            where_it_appears="Experience section - bullet point openings",
            how_to_fix=(
                "Start every bullet point with a past-tense action verb. "
                "Avoid starting with 'Responsible for', 'Worked on', or 'Helped with'. "
                "Use verbs like: Developed, Built, Designed, Implemented, Led, Automated, Optimized."
            ),
            action_items=[
                "Rewrite every bullet that starts with 'Responsible for', 'Helped', 'Worked on', or 'Assisted'",
                "Use: Developed, Built, Designed, Implemented, Led, Automated, Optimized, Deployed, Reduced, Increased",
                "Make verbs past-tense for previous roles, present-tense for current role",
                f"Review all {len(description_lines)} bullet points — at least {len(description_lines)} should start with action verbs",
                "Avoid weak openers like 'Was responsible for...' or 'Involved in...'",
            ],
            example_improvement=(
                "Before:\n"
                "• Responsible for building the backend\n"
                "• Worked on the payment feature\n\n"
                "After:\n"
                "• Developed a REST API with FastAPI handling 5K daily requests\n"
                "• Implemented Stripe payment integration reducing checkout time by 30%"
            ),
        ))
    
    # 7. No Quatifiable Achievements
    number_pattern = r'\d+[%+]?|\$\d+'
    has_metrics = bool(re.findall(number_pattern, experience_text)) if experience_text else False

    if experience_text and not has_metrics:
        detected.append(IssueDetail(
            issue_title="No Quantifiable Achievements Found",
            severity_level="Moderate",
            ats_impact="Medium",
            explanation=(
                "Your experience section doeas not contain any measurable outcomes "
                "(numbers, percentages, or dollar amounts). Quantified achievements "
                "make you impact concrete and are strongly preferred by recruiters."
            ),
            where_it_appears="Experience Section - bullet point content",
            how_to_fix=(
                "Add numbers to at least 50% of your bullet points. "
                "Include metrics like: users served, response time improved, "
                "revenue generated, lines of code, team size, etc."
            ), 
            action_items=[
                "Go through each bullet point and ask: 'How much?', 'How many?', 'By what %?'",
                "Add metrics: users served, requests/day, % improvement, team size, time saved",
                "Examples: '500+ daily users', 'reduced load time by 40%', 'handled 10K API calls/day'",
                "If exact numbers aren't known, use reasonable estimates (e.g., '~200 users')",
                "Aim for numbers in at least 50% of your experience bullets",
            ],
            example_improvement=(
                "Before:\n"
                "• Improved application performance\n"
                "• Managed a team of developers\n\n"
                "After:\n"
                "• Improved API response time by 45% through Redis caching\n"
                "• Led a team of 5 developers delivering 3 features per sprint"
            ),
        ))

    # 8. Missing Contact Information
    if contact_info:
        missing_contacts = []
        if not contact_info.get('email'):
            missing_contacts.append('email')
        if not contact_info.get('phone'):
            missing_contacts.append('phone number')
        if not contact_info.get('linkedin'):
            missing_contacts.append('Linkedin URL')

        if len(missing_contacts) >= 2:
            contact_action_items = [f"Add you {item} to the header section" for item in missing_contacts]
            contact_action_items += [
                "Format the contact line as: email | phone | linkedin | github",
                "Make sure your Liinkedin URL is a custom short URL (linkedin.com/in/yourname)",
                "Add a Github link if you have public projects (github.com/yourame)",
            ]

            detected.append(IssueDetail(
                issue_title="Incomplete Contact Information",
                severity_level="High",
                ats_impact="High",
                explanation=(
                    f"Your resume is missing: {', '.join(missing_contacts)}. "
                    "Recruiters need reliable ways to reach you. Missing contact "
                    "details can cause your application to be skipped entirely."
                ),
                where_it_appears="Header / Contact section at the top of the resume",
                how_to_fix=(
                    "Add your full name, email, phone number, LinkedIn profile, "
                    "and optionally a GitHub or portfolio link at the top of your resume."
                ),
                action_items=contact_action_items,
                example_improvement=(
                    "Add at top:\n"
                    "John Doe\n"
                    "john.doe@email.com | +91-9876543210\n"
                    "linkedin.com/in/johndoe | github.com/johndoe"
                ),
            ))

    # 9. Low Formatting Score
    formatting_score = scores.get('formatting_score', 20)
    if formatting_score < 10:
        detected.append(IssueDetail(
            issue_title="Poor Resume Formatting",
            severity_level="High",
            ats_impact="High",
            explanation=(
                f"Your formatting score is {formatting_score}/20, which indicates "
                "problems like missing section headers, inconsistent structure, "
                "or non-standard layout that ATS parsers struggle with."
            ),
            where_it_appears="Overall document structure and formatting",
            how_to_fix=(
                "Use a clean, single-column layout with standard section headers "
                "(Experience, Education, Skills, Projects). Use consistent bullet "
                "points, standard fonts, and avoid tables, columns, or graphics."
            ),
            action_items=[
                "Switch to a single-column layout (avoid two-column templates for ATS)",
                "Use standard section headers: EXPERIENCE, EDUCATION, SKILLS, PROJECTS",
                "Use bullet points (•) consistently — don't mix with dashes or asterisks",
                "Remove all tables, text boxes, headers/footers, and images — ATS cannot parse them",
                "Use a standard font (Calibri, Arial, Times New Roman) at 10–12pt",
                "Order sections: Contact → Summary → Experience → Projects → Education → Skills",
            ],
            example_improvement=(
                "Use this structure:\n"
                "NAME & CONTACT\n"
                "SUMMARY (2-3 lines)\n"
                "EXPERIENCE (reverse chronological)\n"
                "PROJECTS (2-3 key projects)\n"
                "EDUCATION\n"
                "SKILLS (categorized)"
            ),
        ))

    # 10. Missing Summary/Objective
    if not summary:
        detected.append(IssueDetail(
            issue_title="Missing Professional Summary",
            severity_level="Low",
            ats_impact="Low",
            explanation=(
                "Your resume does not include a Professional Summary or Objective "
                "section at the top. While not required, a 2-3 line summary helps "
                "recruiters quickly understand your profile and target role."
            ),
            where_it_appears="Top of resume — below contact info",
            how_to_fix=(
                "Add a 2-3 sentence summary highlighting your experience level, "
                "key skills, and career focus. Tailor it to the job you're applying for."
            ),
            action_items=[
                "Add a 'PROFESSIONAL SUMMARY' or 'OBJECTIVE' section at the top of your resume",
                "Write 2–3 sentences: who you are, your key skills, and what role you seek",
                "Mention your years of experience or education level upfront",
                "Tailor this section for each job application — reference the specific role",
                "Keep it under 60 words — recruiters spend only 6 seconds on first scan",
            ],
            example_improvement=(
                "Add:\n"
                "PROFESSIONAL SUMMARY\n"
                "Full-stack developer with 2+ years of experience building scalable "
                "web applications using React, Node.js, and AWS. Passionate about "
                "clean architecture and performance optimization."
            ),
        ))

    return detected

def generate_issues_summary(detected_issues: List[IssueDetail]) -> List[str]:
    return [issue.issue_title for issue in detected_issues]