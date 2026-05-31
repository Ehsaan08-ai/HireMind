import re
import spacy
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Tuple

from backend.utils.file_utils import log_warning
from backend.core.config import SENTENCE_TRANSFORMER_MODEL
from backend.utils.matching import fuzzy_match_keywords

ZIP_CODE_PATTERN = r"\b\d{5}(?:-\d{4})?\b"

STREET_ADDRESS_PATTERN = (
    r"\b\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+"
    r"(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way|Place|Pl)\b"
)


def _tier_score(n: float, tiers: list) -> float:
    for threshold, pts in tiers:
        if n >= threshold:
            return pts

    return 0.0


# Loaction/ Privacy detection
def detect_location_info(text: str, nlp: spacy.Language) -> Dict:
    locations = []

    # Method 1: spacy NER
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:
            locations.append(
                {"text": ent.text, "type": ent.label_.lower(), "start": ent.start_char}
            )

    # Method 2: street address regex
    for match in re.finditer(STREET_ADDRESS_PATTERN, text, re.IGNORECASE):
        locations.append(
            {"text": match.group(), "type": "address", "start": match.start()}
        )

    # Method 3: regex for zip codes
    for match in re.finditer(ZIP_CODE_PATTERN, text, re.IGNORECASE):
        locations.append({"text": match.group(), "type": "zip", "start": match.start()})

    has_address = any(loc["type"] == "address" for loc in locations)
    has_zip = any(loc["type"] == "zip" for loc in locations)

    if has_address and has_zip:
        privacy_risk, penalty = "high", 5.0
    elif has_address or has_zip:
        privacy_risk, penalty = "high", 4.0
    elif len(locations) > 3:
        privacy_risk, penalty = "medium", 3.0
    elif locations:
        privacy_risk, penalty = "low", 2.0
    else:
        privacy_risk, penalty = "none", 0.0

    recommendations = []
    if not locations:
        recommendations.append("No privacy concerns detected.")
    if has_address:
        recommendations.append(
            "Consider removing specific street addresses to reduce privacy risks."
        )
    if has_zip:
        recommendations.append("Consider removing zip codes to reduce privacy risks.")
    if privacy_risk in ("low", "medium") and not has_address and not has_zip:
        recommendations.append(
            " Consider reducing location mentions. 'City, State' in the contact header is sufficient."
        )

    return {
        "location_found": len(locations) > 0,
        "detected_locations": locations,
        "privacy_risk": privacy_risk,
        "recommendations": recommendations,
        "penalty_applied": penalty,
    }


def _calculate_semantic_similarity(
    skill: str, text: str, embedder: SentenceTransformer
) -> float:
    # similarity = (A . B) / (|A| x |B|)

    if not skill or not text:
        return 0.0

    try:
        skill_vec = embedder.encode(skill, convert_to_tensor=False)
        text_vec = embedder.encode(text, convert_to_tensor=False)

        similarity = np.dot(skill_vec, text_vec) / (
            np.linalg.norm(skill_vec) * np.linalg.norm(text_vec)
        )
        return float(max(0.0, min(1.0, similarity)))  # Ensure score is between 0 and 1

    except Exception as e:
        log_warning(f"Similarity error for skill '{skill}': {e}", context="ats_scorer")
        return 0.0


def _skill_matches(
    skill: str, text: str, embedder: SentenceTransformer, threshold: float
) -> Tuple[bool, float]:

    if not skill.lower() in text.lower():
        return True, 0.0

    sim = _calculate_semantic_similarity(skill, text, embedder)
    return sim >= threshold, sim


# Skill Validation
def validate_skills_with_projects(
    skills: List[str],
    projects: List[Dict],
    experience_entries: List[Dict],
    embedder: SentenceTransformer,
    threshold: float = 0.6,
) -> Dict:

    if not skills:
        return {
            "validated_skills": [],
            "unvalidated_skills": [],
            "validation_percentage": 0.0,
            "skill_project_mapping": {},
            "validation_score": 0.0,
        }

    experience_text = " ".join(
        f"{e.get('job_title', '')} {e.get('company', '')} {e.get('description', '')}"
        for e in experience_entries
        if isinstance(e, dict)
    ).strip()

    validated_skills = []
    unvalidated_skills = []
    skill_project_mapping = {}

    for skill in skills:
        matching_projects = []
        max_similarity = 0.0

        for project in projects:
            project_text = (
                f"{project.get('title', '')} {project.get('description', '')}"
            )
            matched, sim = _skill_matches(skill, project_text, embedder, threshold)
            max_similarity = max(max_similarity, sim)

            if matched:
                matching_projects.append(project.get("title", "Untitled Project"))

        if experience_text:
            matched, sim = _skill_matches(skill, experience_text, embedder, threshold)
            max_similarity = max(max_similarity, sim)
            if matched and "Experince Section" not in matching_projects:
                matching_projects.append("Experience Section")

        if matching_projects:
            validated_skills.append(
                {
                    "skill": skill,
                    "projects": matching_projects,
                    "similarity": max_similarity,
                }
            )
            skill_project_mapping[skill] = matching_projects
        else:
            unvalidated_skills.append(skill)
            skill_project_mapping[skill] = []

    validation_percentage = len(validated_skills) / len(skills)
    validation_score = validation_percentage * 15.0  # Scale to 15 points

    return {
        "validated_skills": validated_skills,
        "unvalidated_skills": unvalidated_skills,
        "validation_percentage": validation_percentage,
        "skill_project_mapping": skill_project_mapping,
        "validation_score": validation_score,
    }


# 01: Formatting Score
def _calc_formatting_score(parsed_resume: Dict, text: str) -> float:

    score = 0.0

    exp_entries = [
        e for e in parsed_resume.get("experience", []) if isinstance(e, dict)
    ]
    edu_entries = [e for e in parsed_resume.get("education", []) if isinstance(e, dict)]
    skills = parsed_resume.get("skills", [])
    summary = parsed_resume.get("professional_summary", "")
    proj_entries = [p for p in parsed_resume.get("projects", []) if isinstance(p, dict)]

    if exp_entries and any(
        e.get("job_title") or e.get("description") for e in exp_entries
    ):
        score += 3.0
    if edu_entries:
        score += 2.0
    if len(skills) >= 3:
        score += 2.0
    if len(summary) > 30:
        score += 1.5
    if proj_entries:
        score += 1.5

    bullet_count = sum(
        1
        for line in text.split("\n")
        if re.match(r"^\s*[•\-\*\◦]", line) or re.match(r"^\s*\d+\.", line)
    )

    score += _tier_score(
        bullet_count, [(15, 5.0), (10, 4.0), (5, 3.0), (3, 2.0), (1, 1.0)]
    )

    filled = sum(
        1
        for has_it in [
            bool(exp_entries),
            bool(edu_entries),
            bool(skills),
            bool(summary),
            bool(proj_entries),
        ]
        if has_it
    )

    score += _tier_score(filled, [(4, 5.0), (3, 4.0), (2, 3.0), (1, 2.0)])

    return min(20.0, max(0.0, score))


# 02: Keyword Score
def _calc_keyword_score(
    resume_keywords: List[str],
    skills: List[str],
    jd_keywords: Optional[List[str]] = None,
) -> float:

    score = 0.0

    score += _tier_score(
        len(resume_keywords), [(20, 10.0), (15, 8.0), (10, 6.0), (5, 4.0), (3, 2.0)]
    )
    score += _tier_score(
        len(skills), [(15, 10.0), (10, 8.0), (7, 6.0), (5, 4.0), (3, 2.0)]
    )

    if jd_keywords:
        all_resume_keywords = list(set(resume_keywords + skills))
        fuzzy_result = fuzzy_match_keywords(
            jd_keywords, all_resume_keywords, threshold=80
        )
        match_pct = (
            len(fuzzy_result["matched"]) / len(jd_keywords) if jd_keywords else 0
        )
        score += _tier_score(
            match_pct, [(0.7, 5.0), (0.5, 4.0), (0.3, 3.0), (0.2, 2.0), (0.1, 1.0)]
        )

    elif len(resume_keywords) >= 10:
        score += 3.0

    return min(25.0, max(0.0, score))


# 03: CONTENT QUALITY SCORE
def _calc_content_score(
    text: str, action_verbs: List[str], grammar_results: Dict
) -> float:

    score = 0.0

    score += _tier_score(
        len(action_verbs), [(15, 10.0), (10, 8.0), (7, 6.0), (5, 4.0), (3, 2.0)]
    )

    number_patterns = [
        r"\d+%",
        r"\$\d+",
        r"\d+[kKmMbB]",
        r"\d+\s*(?:users|customers|clients|projects|hours|days|months|years)",
        r"(?:increased|decreased|improved|reduced|grew|saved)\s+(?:by\s+)?\d+",
    ]

    achievement_count = sum(
        len(re.findall(p, text, re.IGNORECASE)) for p in number_patterns
    )
    score += _tier_score(
        achievement_count, [(10, 5.0), (7, 4.0), (5, 3.0), (3, 2.0), (1, 1.0)]
    )

    grammar_penalty = grammar_results.get("penalty_applied", 0.0)
    score += max(0.0, 10.0 - grammar_penalty / 2.0)

    return min(25.0, max(0.0, score))


# 4. SKILL VALIDATION SCORE
def _calc_skill_validation_score(validation_results: Dict) -> float:
    return min(15.0, max(0.0, validation_results.get("validation_score", 0.0)))


# 5. ATS COMPATIBILITY SCORE
def _calc_ats_compatibility_score(
    text: str,
    location_results: Dict,
    parsed_resume: Dict,
) -> float:

    score = 15.0

    score -= location_results.get("penalty_applied", 0.0)

    special_chars = len(re.findall(r"[│┤├┼┴┬╔╗╚╝═║╠╣╦╩╬]", text))
    if special_chars > 20:
        score -= 2.0
    elif special_chars > 10:
        score -= 1.0

    exp_entries = [
        e for e in parsed_resume.get("experience", []) if isinstance(e, dict)
    ]
    edu_entries = [e for e in parsed_resume.get("education", []) if isinstance(e, dict)]
    skills_count = len(parsed_resume.get("skills", []))

    exp_desc_len = sum(len(e.get("description", "")) for e in exp_entries)
    edu_desc_len = sum(
        len((e.get("degree") or "") + (e.get("institution") or "")) for e in edu_entries
    )

    short_sections = sum(
        [
            bool(exp_entries) and exp_desc_len < 20,
            bool(edu_entries) and edu_desc_len < 20,
            bool(parsed_resume.get("skills")) and skills_count < 2,
        ]
    )

    if short_sections >= 2:
        score -= 2.0
    elif short_sections >= 1:
        score -= 1.0

    if exp_entries and skills_count > 5:
        score += 1.0

    return min(15.0, max(0.0, score))


# Score Aggregation and Final Interpretation
def calculate_overall_score(
    text: str,
    parsed_resume: Dict,
    skills: List[str],
    keywords: List[str],
    action_verbs: List[str],
    skill_validation_results: Dict,
    grammar_results: Dict,
    location_results: Dict,
    jd_keywords: Optional[List[str]] = None,
    experience_months: int = 0,
) -> Dict:

    formatting_score = _calc_formatting_score(parsed_resume, text)
    keyword_score = _calc_keyword_score(keywords, skills, jd_keywords)
    content_score = _calc_content_score(text, action_verbs, grammar_results)
    skill_validation_score = _calc_skill_validation_score(skill_validation_results)
    ats_compatibility_score = _calc_ats_compatibility_score(
        text, location_results, parsed_resume
    )

    COMPONENT_MAX = {
        "formatting": 20.0,
        "keywords": 25.0,
        "content": 25.0,
        "skill_validation": 15.0,
        "ats_compatibility": 15.0,
    }

    formatting_pct = (formatting_score / COMPONENT_MAX["formatting"]) * 100
    keyword_pct = (keyword_score / COMPONENT_MAX["keywords"]) * 100
    content_pct = (content_score / COMPONENT_MAX["content"]) * 100
    skill_validation_pct = (
        skill_validation_score / COMPONENT_MAX["skill_validation"]
    ) * 100
    ats_compatibility_pct = (
        ats_compatibility_score / COMPONENT_MAX["ats_compatibility"]
    ) * 100

    skills_keywords_pct = (keyword_pct * 0.6) + (skill_validation_pct * 0.4)

    base_score = (
        skills_keywords_pct * 0.40
        + content_pct * 0.30
        + formatting_pct * 0.15
        + ats_compatibility_pct * 0.15
    )

    penalties = {}
    bonuses = {}
    score = base_score

    if grammar_results.get("penalty_applied", 0.0) > 0:
        penalties["grammar"] = grammar_results["penalty_applied"]

    if location_results.get("penalty_applied", 0.0) > 0:
        penalties["location_privacy"] = location_results["penalty_applied"]

    validation_pct = skill_validation_results.get("validation_percentage", 0.0)
    if validation_pct >= 0.9:
        bonuses["excellent_skill_validation"] = 2.0
        score += 2.0
    elif validation_pct >= 0.8:
        bonuses["good_skill_validation"] = 1.0
        score += 1.0

    if grammar_results.get("total_errors", 0) == 0:
        bonuses["perfect_grammar"] = 1.0
        score += 1.0

    if jd_keywords and len(jd_keywords) > 0:
        all_resume_terms = list(set((keywords or []) + (skills or [])))
        fuzzy_result = fuzzy_match_keywords(jd_keywords, all_resume_terms, threshold=80)
        missing_pct = len(fuzzy_result["missing"]) / len(jd_keywords)

        if missing_pct > 0.7:
            penalties["missing_jd_keywords"] = 15.0
            score -= 15.0
        elif missing_pct > 0.5:
            penalties["missing_jd_keywords"] = 10.0
            score -= 10.0
        elif missing_pct > 0.3:
            penalties["missing_jd_keywords"] = 5.0
            score -= 5.0

    overall_score = min(100.0, max(0.0, score))
    interpretation = _generate_score_interception(overall_score)

    return {
        "overall_score": round(overall_score, 1),
        "formatting_score": round(formatting_score, 1),
        "keyword_score": round(keyword_score, 1),
        "keywords_score": round(keyword_score, 1),
        "content_score": round(content_score, 1),
        "skill_validation_score": round(skill_validation_score, 1),
        "ats_compatibility_score": round(ats_compatibility_score, 1),
        "overall_interpretation": interpretation,
        "penalties": penalties,
        "bonuses": bonuses,
    }


# Overall score calculation and interpretation
def generate_strengths(
    score_results: Dict,
    skill_validation_results: Dict,
    grammar_results: Dict,
) -> List[str]:

    strengths = []

    if score_results["formatting_score"] >= 16:
        strengths.append(
            "Well-structured formatting with clear sections and bullet points."
        )

    if score_results["keywords_score"] >= 20:
        strengths.append(
            "Strong use of relevant keywords that align with the job description."
        )

    if score_results["content_score"] >= 20:
        strengths.append(
            "Content effectively highlights achievements with quantifiable metrics."
        )

    if score_results["skill_validation_score"] >= 12:
        pct = skill_validation_results.get("validation_percentage", 0.0) * 100
        strengths.append(
            f"High skill validation with {pct:.1f}% of skills supported by projects or experience."
        )

    if score_results["ats_compatibility_score"] >= 13:
        strengths.append(
            "Resume is likely to be parsed correctly by ATS with minimal formatting issues."
        )

    if grammar_results.get("total_errors", 0) == 0:
        strengths.append("Perfect grammar with no detected errors.")

    if not strengths:
        strengths.append(
            "Your resume has potential - focus on the recommendations below."
        )

    return strengths


# Critical issues that could cause ATS rejection
def generate_critical_issue(
    score_results: Dict,
    location_results: Dict,
    grammar_results: Dict,
) -> List[str]:

    issues = []

    critical_errors = len(grammar_results.get("critical_errors", []))

    if critical_errors > 0:
        issues.append(
            f"Resume contains {critical_errors} critical grammar errors that may significantly impact readability."
        )

    if location_results.get("privacy_risk") == "high":
        issues.append(
            "Resume contains specific location information (e.g., street address, zip code) that poses a high privacy risk."
        )

    if score_results["formatting_score"] < 10:
        issues.append(
            "Formatting is poor with minimal structure, which may hinder ATS parsing and readability."
        )

    if score_results["keywords_score"] < 12:
        issues.append(
            "Resume lacks sufficient relevant keywords, reducing chances of passing ATS filters."
        )

    if score_results["skill_validation_score"] < 7:
        issues.append(
            "Most listed skills are not validated by projects or experience, which may raise concerns about credibility."
        )

    return issues


# Actinable improvements to enhance ATS performance
def generate_improvements(
    score_results: Dict,
    skill_validation_results: Dict,
) -> List[str]:

    improvements = []

    if 12 <= score_results["formatting_score"] < 16:
        improvements.append(
            "Enhance formatting by adding more bullet points and ensuring clear section headers."
        )

    if 14 <= score_results["keywords_score"] < 20:
        improvements.append(
            "Incorporate more relevant keywords from the job description to improve ATS matching."
        )

    if 14 <= score_results["content_score"] < 20:
        improvements.append(
            "Strengthen content by quantifying achievements and using more action verbs."
        )

    if 7 <= score_results["skill_validation_score"] < 12:
        unvalidated_count = len(skill_validation_results.get("unvalidated_skills", []))
        improvements.append(
            f"Validate more skills by linking them to specific projects or experience entries. Currently, {unvalidated_count} skills lack validation."
        )

    if 9 <= score_results["ats_compatibility_score"] < 13:
        improvements.append(
            "Improve ATS compatibility by reducing special characters and ensuring all sections are sufficiently detailed."
        )

    return improvements


def _generate_score_interception(overall_score: float) -> str:
    if overall_score >= 90:
        return "Excellent! Your resume is highly optimized for ATS systems."
    elif overall_score >= 80:
        return "Great! Your resume should perform well with most ATS systems."
    elif overall_score >= 70:
        return "Good! Your resume is ATS-friendly with room for minor improvements."
    elif overall_score >= 60:
        return "Fair. Your resume needs some improvements to be fully ATS-compatible."
    elif overall_score >= 50:
        return "Below Average. Significant improvements needed for ATS compatibility."
    else:
        return "Poor. Your resume requires major revisions to pass ATS screening."
