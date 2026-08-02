import json
import re

from pydantic import ValidationError

from app.config import get_settings
from app.errors import (
    GeminiConfigError,
    GeminiMalformedResponseError,
    GeminiRateLimitError,
    GeminiServiceError,
    GeminiTimeoutError,
)
from app.models import Profile
from app.schemas import InsightResult

_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)


def _build_prompt(profile: Profile) -> str:
    return (
        "You are analysing a user profile for a community events app. "
        "Based on the profile below, respond with ONLY a JSON object (no markdown, no code fences, "
        "no extra commentary) with exactly these string fields: "
        '"summary", "communication_style", "suggested_focus".\n\n'
        f"Full name: {profile.full_name}\n"
        f"City: {profile.city}\n"
        f"Occupation: {profile.occupation or 'unspecified'}\n"
        f"Bio: {profile.bio or 'unspecified'}\n"
    )


def _strip_code_fences(text: str) -> str:
    return _CODE_FENCE_RE.sub("", text).strip()


def _parse_and_validate(raw_text: str) -> InsightResult:
    cleaned = _strip_code_fences(raw_text)
    try:
        data = json.loads(cleaned)
    except (json.JSONDecodeError, TypeError) as exc:
        raise GeminiMalformedResponseError("AI returned an unexpected response.") from exc

    try:
        return InsightResult.model_validate(data)
    except ValidationError as exc:
        raise GeminiMalformedResponseError("AI returned an unexpected response.") from exc


def generate_insight(profile: Profile) -> InsightResult:
    """Call Gemini with the saved profile and return a validated structured insight.

    Kept as a single seam so tests can monkeypatch this function (or the underlying
    client call below) without hitting the real API.
    """
    settings = get_settings()
    if not settings.gemini_api_key:
        raise GeminiConfigError("AI service is not configured.")

    raw_text = _call_gemini(profile)
    return _parse_and_validate(raw_text)


def _call_gemini(profile: Profile) -> str:
    """The actual network call, isolated so tests can patch just this seam if desired."""
    settings = get_settings()

    import google.generativeai as genai
    from google.api_core import exceptions as google_exceptions

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.gemini_model)
    prompt = _build_prompt(profile)

    try:
        response = model.generate_content(
            prompt,
            request_options={"timeout": settings.gemini_timeout_seconds},
        )
    except google_exceptions.DeadlineExceeded as exc:
        raise GeminiTimeoutError("AI insight timed out, please try again.") from exc
    except google_exceptions.ResourceExhausted as exc:
        raise GeminiRateLimitError("AI service is busy, please retry shortly.") from exc
    except google_exceptions.GoogleAPIError as exc:
        raise GeminiServiceError("AI service error, please try again.") from exc
    except TimeoutError as exc:
        raise GeminiTimeoutError("AI insight timed out, please try again.") from exc
    except Exception as exc:  # noqa: BLE001 - map any unexpected client error to a clean 502
        raise GeminiServiceError("AI service error, please try again.") from exc

    text = getattr(response, "text", None)
    if not text:
        raise GeminiMalformedResponseError("AI returned an unexpected response.")
    return text
