
import re


def validate_inputs(topic, subject, level):
    """Check the required user inputs."""

    if not topic or not topic.strip():
        return False, "Please enter a study topic."

    if not subject or not subject.strip():
        return False, "Please select a subject."

    if not level or not level.strip():
        return False, "Please select an education level."

    if len(topic.strip()) > 500:
        return False, "Topic must be 500 characters or fewer."

    return True, ""


def validate_study_pack(content):
    """Perform basic structural checks on the final study pack."""

    issues = []

    if not content or len(content.strip()) < 200:
        issues.append("The final study pack is empty or too short.")

    required_sections = [
        "Learning Objectives",
        "Study Notes",
        "Summary",
        "MCQs",
        "Flashcards",
    ]

    for section in required_sections:
        if not re.search(
            rf"^\s*#+\s*.*{re.escape(section)}",
            content or "",
            re.IGNORECASE | re.MULTILINE,
        ):
            issues.append(f"Missing section: {section}")

    return {
        "passed": len(issues) == 0,
        "issues": issues,
    }


def format_study_pack(topic, subject, level, content):
    """Add metadata to the downloadable Markdown document."""

    return (
        f"# AI Study Pack: {topic}\n\n"
        f"**Subject:** {subject}  \n"
        f"**Education Level:** {level}  \n"
        f"**Generated with:** AI Study Pack Generator\n\n"
        "---\n\n"
        f"{content.strip()}\n"
    )
