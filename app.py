
        try:
            with st.spinner("Generating your study pack..."):
                result = run_workflow(
                    topic=topic.strip(),
                    subject=subject,
                    level=level,
                    goals=goals.strip(),
                    source_notes=source_notes.strip(),
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

            status_text.success("All five workflow stages completed.")

        except Exception as error:
            status_text.empty()
            st.error("Actual workflow error:")
            st.exception(error)
