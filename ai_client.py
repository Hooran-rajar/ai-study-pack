
import os

import streamlit as st
from groq import Groq


def get_api_key():
    """Read the API key from Streamlit Secrets or environment variables."""
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        api_key = ""

    return api_key or os.getenv("GROQ_API_KEY", "")


def call_ai(
    prompt,
    system_prompt="You are a helpful educational assistant.",
    model=None,
    max_tokens=3000,
):
    """Send a prompt to Groq and return the generated text."""

    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Configure it in Streamlit Secrets "
            "or as an environment variable."
        )

    client = Groq(api_key=api_key)

    selected_model = model or os.getenv(
        "GROQ_MODEL", "openai/gpt-oss-20b"
    )

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
print("Message:", response.choices[0].message)

content = response.choices[0].message.content

if not content or not content.strip():
    raise RuntimeError(
        f"The AI returned an empty response. "
        f"Finish reason: {response.choices[0].finish_reason}"
    )

    result = response.choices[0].message.content

    if not result or not result.strip():
        raise RuntimeError("The AI returned an empty response.")

    return result.strip()
