
from ai_client import call_ai


def run_workflow(
    topic,
    subject,
    level,
    goals="",
    source_notes="",
    mcq_count=10,
    flashcard_count=10,
    model=None,
    progress_callback=None,
):
    """Generate a study pack using a token-conscious five-stage workflow."""

    stages = {}

    def update_progress(name, percent):
        if progress_callback:
            progress_callback(name, percent)

    # Keep user-provided source notes within a reasonable size.
    source_notes = (source_notes or "").strip()[:4000]
    goals = (goals or "").strip()[:1000]

    model_args = {"model": model} if model else {}

    # Stage 1: Planning
    update_progress("Stage 1/5: Planning", 10)

    planning = call_ai(
        prompt=f"""
Create a concise study plan.

Subject: {subject}
Topic: {topic}
Education level: {level}
Learning goals: {goals or "Suggest suitable goals."}
Source notes: {source_notes or "None provided."}

Include:
- Learning Objectives
- Key Concepts
- Study Order
- Prerequisites

Do not invent syllabus requirements.
Keep the plan brief.
""",
        system_prompt="You are an educational planning agent.",
        max_tokens=800,
        **model_args,
    )
    stages["Planning"] = planning

    # Stage 2: Content Generation
    update_progress("Stage 2/5: Content Generation", 30)

    content = call_ai(
        prompt=f"""
Create clear study material.

Subject: {subject}
Topic: {topic}
Level: {level}
Goals: {goals or "Use the plan below."}

PLAN:
{planning[:3000]}

SOURCE NOTES:
{source_notes or "None provided."}

Include:
- Learning Objectives
- Study Notes with explanations and examples
- Summary

Use clear language suitable for the specified level.
Do not invent citations or unsupported facts.
Keep the material focused and concise.
""",
        system_prompt="You are an educational content generation agent.",
        max_tokens=1800,
        **model_args,
    )
    stages["Content Generation"] = content

    # Stage 3: Assessment Generation
    update_progress("Stage 3/5: Assessment", 50)

    assessment = call_ai(
        prompt=f"""
Create an assessment using the study material below.

Subject: {subject}
Topic: {topic}
Level: {level}

STUDY MATERIAL:
{content[:7000]}

Create:
1. Exactly {mcq_count} MCQs, each with A, B, C, D options,
   the correct answer, and a brief explanation.
2. Exactly {flashcard_count} flashcards in Question / Answer format.
3. Short-answer revision questions.

Use headings MCQs, Flashcards, and Short-Answer Questions.
Keep each item concise and relevant to the supplied material.
""",
        system_prompt="You are an educational assessment agent.",
        max_tokens=1800,
        **model_args,
    )
    stages["Assessment"] = assessment

    # Stage 4: AI Quality Control
    update_progress("Stage 4/5: AI Quality Control", 70)

    quality_report = call_ai(
        prompt=f"""
Review this study pack for important problems only.

TOPIC: {topic}
SUBJECT: {subject}
LEVEL: {level}

STUDY MATERIAL:
{content[:5000]}

ASSESSMENT:
{assessment[:5000]}

Check topic relevance, factual consistency within the material,
MCQ answer correctness, duplicate items, ambiguity, and missing sections.

Return:
- Overall assessment
- Up to 5 specific issues, if any
- Brief suggested corrections

Do not claim external facts were independently verified.
Keep your report concise.
""",
        system_prompt="You are a strict educational quality-control reviewer.",
        max_tokens=600,
        **model_args,
    )
    stages["AI Quality Control"] = quality_report

    # Stage 5: Refinement
    update_progress("Stage 5/5: Refinement", 90)

    final_pack = call_ai(
        prompt=f"""
Create the final study pack using the material and review below.

SUBJECT: {subject}
TOPIC: {topic}
LEVEL: {level}

STUDY MATERIAL:
{content[:5000]}

ASSESSMENT:
{assessment[:5000]}

QUALITY REVIEW:
{quality_report[:1500]}

Correct clear issues where possible. Preserve useful material.
Do not regenerate everything unnecessarily.

Include:
- Learning Objectives
- Study Notes
- Summary
- MCQs with answers and explanations
- Flashcards
- Short-Answer Questions
- Revision Checklist

Do not invent facts, citations, or sources.
Use clean Markdown and concise explanations.
""",
        system_prompt="You are an educational refinement agent.",
        max_tokens=1500,
        **model_args,
    )
    stages["Refinement"] = final_pack

    update_progress("Workflow completed", 100)

    return {
        "stages": stages,
        "planning": planning,
        "content": content,
        "assessment": assessment,
        "quality_report": quality_report,
        "final_pack": final_pack,
    }
