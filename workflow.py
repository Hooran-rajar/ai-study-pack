
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
    """Run the complete five-stage AI study-pack workflow."""

    stages = {}

    def update_progress(name, percent):
        if progress_callback:
            progress_callback(name, percent)

    # Stage 1: Planning
    update_progress("Stage 1/5: Planning", 10)

    planning = call_ai(
        prompt=f"""
Create a clear study plan.

Subject: {subject}
Topic: {topic}
Education level: {level}
Learning goals: {goals or "Suggest suitable learning goals."}
Available source notes:
{source_notes or "No source notes provided."}

Include:
- Learning Objectives
- Key Concepts
- Suggested Study Order
- Important Prerequisites

Do not invent syllabus requirements.
""",
        system_prompt="You are an educational planning agent.",
        model=model,
        max_tokens=1500,
    )
    stages["Planning"] = planning

    # Stage 2: Content Generation
    update_progress("Stage 2/5: Content Generation", 30)

    content = call_ai(
        prompt=f"""
Create educational study material using the plan below.

Subject: {subject}
Topic: {topic}
Education level: {level}
Learning goals: {goals or "Use the learning objectives in the plan."}

PLAN:
{planning}

SOURCE NOTES:
{source_notes or "No source notes provided."}

Requirements:
- Use the heading Learning Objectives.
- Use the heading Study Notes.
- Explain key concepts in clear language.
- Include relevant examples.
- Use the heading Summary.
- Do not invent citations or unsupported facts.
- If source material is incomplete, acknowledge uncertainty.
- Keep the content appropriate for the specified level.
""",
        system_prompt="You are an educational content generation agent.",
        model=model,
        max_tokens=3500,
    )
    stages["Content Generation"] = content

    # Stage 3: Assessment Generation
    update_progress("Stage 3/5: Assessment", 50)

    assessment = call_ai(
        prompt=f"""
Create assessments based on the study material below.

TOPIC: {topic}
SUBJECT: {subject}
EDUCATION LEVEL: {level}

STUDY MATERIAL:
{content}

Generate:
1. Exactly {mcq_count} multiple-choice questions.
2. Four options per MCQ, labelled A, B, C, D.
3. The correct answer and a short explanation for each MCQ.
4. Exactly {flashcard_count} flashcards in Question / Answer format.
5. A short-answer revision section.

Use the headings MCQs and Flashcards.
Make questions relevant to the supplied material.
Do not create questions that require facts absent from the material.
""",
        system_prompt="You are an educational assessment agent.",
        model=model,
        max_tokens=3500,
    )
    stages["Assessment"] = assessment

    # Stage 4: AI Quality Control
    update_progress("Stage 4/5: AI Quality Control", 70)

    quality_report = call_ai(
        prompt=f"""
Review the following educational study pack.

TOPIC: {topic}
SUBJECT: {subject}
LEVEL: {level}

STUDY CONTENT:
{content}

ASSESSMENTS:
{assessment}

Check:
- Relevance to the requested topic.
- Coverage of the learning objectives.
- Internal factual consistency.
- Whether MCQ answers match their explanations.
- Duplicate questions and flashcards.
- Ambiguous questions or answer options.
- Missing or poorly formatted sections.
- Unsupported claims and uncertainty.

Return:
1. Overall quality assessment.
2. A list of specific issues found.
3. Suggested corrections.
4. State "No major issues identified" only if appropriate.

Do not claim that external facts have been independently verified.
""",
        system_prompt="You are a strict educational quality-control reviewer.",
        model=model,
        max_tokens=5000,
    )
    stages["AI Quality Control"] = quality_report

    # Stage 5: Refinement
    update_progress("Stage 5/5: Refinement", 90)

    final_pack = call_ai(
        prompt=f"""
Produce the final, improved study pack.

TOPIC: {topic}
SUBJECT: {subject}
EDUCATION LEVEL: {level}

PLANNING:
{planning}

GENERATED STUDY CONTENT:
{content}

ASSESSMENTS:
{assessment}

AI QUALITY CONTROL REPORT:
{quality_report}

Requirements:
- Correct issues identified by quality control where possible.
- Preserve accurate, relevant educational material.
- Include Learning Objectives, Study Notes, Summary, MCQs,
  Flashcards and Short-Answer Questions.
- Keep MCQ answers and explanations consistent.
- Include a Revision Checklist.
- Do not invent facts, citations or sources.
- If an issue cannot be resolved confidently, disclose it.
- Return the complete study pack in clean Markdown.
""",
        system_prompt="You are an educational refinement agent.",
        model=model,
        max_tokens=5000,
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
