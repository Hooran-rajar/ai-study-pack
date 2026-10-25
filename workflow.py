
from ai_client import call_ai


def run_workflow(
    topic,
    subject,
    level,
    goals="",
    source_notes="",
    mcq_count=5,
    flashcard_count=5,
    model=None,
    progress_callback=None,
):
    """Generate a concise study pack using two AI requests."""

    stages = {}

    def update_progress(name, percent):
        if progress_callback:
            progress_callback(name, percent)

    # Limit input size to control token usage.
    source_notes = (source_notes or "").strip()[:3000]
    goals = (goals or "").strip()[:500]
    topic = (topic or "").strip()

    model_args = {"model": model} if model else {}

    # Stage 1: Planning and Study Notes in ONE API request.
    update_progress("Stage 1/2: Study Notes and Planning", 10)

    content = call_ai(
        prompt=f"""
Create a concise study pack section.

Subject: {subject}
Topic: {topic}
Education Level: {level}
Learning Goals: {goals or "Suggest suitable learning goals."}

Source Notes:
{source_notes or "No source notes provided."}

Include these headings:
1. Learning Objectives
2. Key Concepts
3. Study Notes
4. Simple Examples
5. Summary

Requirements:
- Explain the topic clearly for the specified level.
- Keep notes concise and useful for revision.
- Use examples where helpful.
- Use the source notes when provided.
- Do not invent citations or claim unsupported facts.
- Use clean Markdown.
""",
        system_prompt=(
            "You are a concise educational tutor. "
            "Create clear, accurate, student-friendly study notes."
        ),
        max_tokens=1200,
        **model_args,
    )

    stages["Study Notes and Planning"] = content

    # Stage 2: MCQs, flashcards and revision questions
    # using ONE additional API request.
    update_progress("Stage 2/2: Assessment", 55)

    assessment = call_ai(
        prompt=f"""
Create a concise assessment from the study notes below.

Subject: {subject}
Topic: {topic}
Level: {level}

Study Notes:
{content[:4500]}

Create exactly:
- {mcq_count} multiple-choice questions (MCQs).
- {flashcard_count} flashcards.
- 3 short-answer revision questions.

For every MCQ:
- Give options A, B, C and D.
- Mark the correct answer.
- Add a brief explanation.

For every flashcard:
- Include a Question and Answer.

Use these headings:
1. MCQs
2. Flashcards
3. Short-Answer Questions

Keep all items concise and relevant to the study notes.
Avoid duplicate questions.
Use clean Markdown.
Do not invent citations or sources.
""",
        system_prompt=(
            "You are an educational assessment generator. "
            "Follow the requested question counts exactly."
        ),
        max_tokens=1400,
        **model_args,
    )

    stages["Assessment"] = assessment

    # Combine the two outputs without another AI request.
    final_pack = f"""# {topic}

**Subject:** {subject}  
**Education Level:** {level}

{content}

---

# Assessment

{assessment}

---

## Revision Checklist

- [ ] Review the learning objectives.
- [ ] Revise the key concepts and examples.
- [ ] Attempt the MCQs before checking answers.
- [ ] Review the flashcards.
- [ ] Practise the short-answer questions.
"""

    # Inform the user that no separate AI review was performed.
    quality_report = (
        "A separate AI Quality Control request was skipped to reduce "
        "API usage. Review the study notes and answers carefully. "
        "The content has not been independently fact-checked."
    )

    stages["Quality Control (manual review)"] = quality_report

    update_progress("Study pack completed", 100)

    return {
        "stages": stages,
        "planning": (
            "Planning was combined with study notes generation "
            "to reduce API requests."
        ),
        "content": content,
        "assessment": assessment,
        "quality_report": quality_report,
        "final_pack": final_pack,
    }
