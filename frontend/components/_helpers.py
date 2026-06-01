from typing import Tuple


def get_score_color(score: float) -> Tuple[str, str]:
    """Return (text_color, background_color) for the score circle or panel."""
    if score >= 80:
        return "#10B981", "rgba(16, 185, 129, 0.08)"  # vibrant emerald green
    if score >= 60:
        return "#F59E0B", "rgba(245, 158, 11, 0.08)"  # warm modern amber
    return "#EF4444", "rgba(239, 68, 68, 0.08)"  # coral/rose red


def get_score_emoji(score: float) -> str:
    """Emoji that matches the score band — used in headlines."""
    if score >= 90:
        return "🌟"
    if score >= 80:
        return "✨"
    if score >= 70:
        return "📈"
    if score >= 60:
        return "⚠️"
    return "🚨"


def get_severity_style(severity: str) -> Tuple[str, str, str]:
    """
    Return (icon, text_color, background_color) for an IssueDetail severity.
    Matches the values the backend emits in `detailed_feedback[].severity_level`.
    """
    level = (severity or "").lower()
    if level in ("critical", "high"):
        return "🔴", "#EF4444", "rgba(239, 68, 68, 0.06)"  # modern rose error card
    if level == "medium":
        return "🟡", "#F59E0B", "rgba(245, 158, 11, 0.06)"  # warm amber warning card
    return "🟢", "#10B981", "rgba(16, 185, 129, 0.06)"  # vibrant emerald success card
