from groq import APIStatusError, Groq

from app.core.config import settings


client = Groq(
    api_key=settings.GROQ_API_KEY
)


def generate_answer(prompt):

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=700,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
    except APIStatusError as error:
        if error.status_code == 413:
            return (
                "The request was too large for the current Groq model limit. "
                "Please ask a narrower question or ingest shorter transcripts."
            )

        raise

    return response.choices[0].message.content


def stream_answer(prompt):

    try:
        stream = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=700,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True
        )
    except APIStatusError as error:
        if error.status_code == 413:
            yield (
                "The request was too large for the current Groq model limit. "
                "Please ask a narrower question or ingest shorter transcripts."
            )
            return

        raise

    for chunk in stream:
        delta = chunk.choices[0].delta.content

        if delta:
            yield delta
