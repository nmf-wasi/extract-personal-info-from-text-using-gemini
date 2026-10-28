from google import genai
from app.schemas.person import PersonalInfo
from dotenv import load_dotenv
from google.genai import types, errors
from functools import lru_cache

load_dotenv()
MODEL = "gemini-3.5-flash-lite"
client = genai.Client()


config = types.GenerateContentConfig(
    system_instruction=(
        "Extract person's details into the schema. Never invent facts that are not provided.",
        "Calculate the age from date of birth if not provided directly.",
        "Leave not provided informations as null or empty",
    )
)


class LLMBadOutput(Exception):
    pass


class LLMUnavailable(Exception):
    pass


@lru_cache
def get_client():
    return genai.Client()


def extract_personal_info(text: str) -> PersonalInfo:
    """sends the text to the moels and model generates the content, it might generate non-parasable output or get API error as well, therefore, used try and expect block"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=text,
            config=config,
        )
    except errors.APIError as e:
        if e.code in (429, 500, 503):
            raise LLMUnavailable(str(e.message)) from e
        raise
    if response.parsed is None:
        raise LLMBadOutput(str(response.candidates[0].finish_reason))
    return response.parsed
