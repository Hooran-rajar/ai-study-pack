
import os
import streamlit as st
from groq import Groq


def call_ai(
    prompt,
    system_prompt="You are a helpful AI assistant.",
    max_tokens=1500,
    model=None,
):
    api_key = None

    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to Streamlit Secrets."
        )

    client = Groq(api_key=api_key)

    selected_model = "openai/gpt-oss-20b"

    response = client.chat.completions.create(
        model=selected_model,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_completion_tokens=max_tokens,
        temperature=0.2,
        reasoning_effort="low",
        include_reasoning=False,
    )

    print("Finish reason:", response.choices[0].finish_reason)
    print("Usage:", response.usage)

    content = response.choices[0].message.content

    if not content or not content.strip():
        raise RuntimeError(
            "The AI returned an empty response. "
            f"Finish reason: {response.choices[0].finish_reason}"
        )

    return content.strip()
