
import streamlit as st

from workflow import run_workflow
from utils import (
    validate_inputs,
    validate_study_pack,
    format_study_pack,
)

st.set_page_config(
    page_title="AI Study Pack Generator",
    page_icon="📚",
    layout="wide",
)

st.title("📚 AI Study Pack Generator")
st.write(
    "Generate structured study notes, assessments, flashcards "
    "and a quality-reviewed revision pack."
)

with st.sidebar:
    st.header("Study Settings")

    subject = st.selectbox(
        "Subject",
        [
            "Computer Science",
            "Mathematics",
            "Physics",
            "Chemistry",
            "Biology",
            "English",
            "Other",
        ],
    )

    level = st.selectbox(
        "Education Level",
        [
            "School",
            "College",
            "Undergraduate",
            "Postgraduate",
        ],
    )

    mcq_count = st.select_slider(
        "Number of MCQs",
        options=[5, 10, 15],
        value=5,
        help="Choose how many multiple-choice questions to generate.",
    )

    flashcard_count = st.select_slider(
        "Number of Flashcards",
        options=[5, 10, 15],
        value=5,
        help="Choose how many flashcards to generate.",
    )

    model = st.text_input(
        "Groq model ID",
        value="openai/gpt-oss-20b",
        help="Use a model ID currently supported by your Groq account.",
    )

with st.form("study_pack_form"):
    topic = st.text_input(
        "Study Topic",
        placeholder="e.g. Machine Learning",
    )

    goals = st.text_area(
        "Learning Goals",
        placeholder="What do you want to learn?",
    )

    source_notes = st.text_area(
        "Optional: Syllabus or Class Notes",
        placeholder="Paste relevant class notes here...",
        height=160,
        max_chars=4000,
        help="Keep notes concise to reduce AI token usage.",
    )

    submitted = st.form_submit_button(
        "Generate Study Pack",
        type="primary",
        use_container_width=True,
    )

if submitted:
    valid, message = validate_inputs(topic, subject, level)

    if not valid:
        st.error(message)
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()

        def show_progress(stage_name, percent):
            progress_bar.progress(percent)
            status_text.write(stage_name)

        try:
            with st.spinner("Generating your study pack..."):
                result = run_workflow(
                    topic=topic.strip(),
                    subject=subject,
                    level=level,
                    goals=goals.strip()[:1000],
                    source_notes=source_notes.strip()[:4000],
                    mcq_count=mcq_count,
                    flashcard_count=flashcard_count,
                    model=model.strip(),
                    progress_callback=show_progress,
                )

            st.session_state["study_result"] = result
            st.session_state["study_metadata"] = {
                "topic": topic.strip(),
                "subject": subject,
                "level": level,
            }

            status_text.success(
                "All five workflow stages completed."
            )

        except Exception as error:
            status_text.empty()
            st.error("Actual workflow error:")
            st.exception(error)

if "study_result" in st.session_state:
    result = st.session_state["study_result"]
    metadata = st.session_state["study_metadata"]

    st.divider()
    st.header("AI Workflow Results")

    for stage_name, stage_output in result["stages"].items():
        with st.expander(stage_name, expanded=False):
            st.markdown(stage_output)

    st.subheader("Final Study Pack")
    st.markdown(result["final_pack"])

    check = validate_study_pack(result["final_pack"])

    if check["passed"]:
        st.success("Basic structural checks passed.")
    else:
        st.warning("Some structural checks need attention.")
        for issue in check["issues"]:
            st.write(f"- {issue}")

    with st.expander("AI Quality Control Report"):
        st.markdown(result["quality_report"])
        st.caption(
            "AI review is not a guarantee of factual accuracy. "
            "Check important information against trusted sources."
        )

    downloadable_content = format_study_pack(
        topic=metadata["topic"],
        subject=metadata["subject"],
        level=metadata["level"],
        content=result["final_pack"],
    )

    st.download_button(
        label="Download Study Pack (.md)",
        data=downloadable_content,
        file_name="ai_study_pack.md",
        mime="text/markdown",
        use_container_width=True,
    )
