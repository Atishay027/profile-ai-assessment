import pytest

from app.errors import (
    GeminiMalformedResponseError,
    GeminiServiceError,
    GeminiTimeoutError,
)
from app.models import Profile
from app.schemas import InsightResult
from app.services.gemini import _parse_and_validate, _strip_code_fences

USER = "user-001"


def _insert_profile(db):
    profile = Profile(user_id=USER, full_name="Jordan Rivera", city="Austin")
    db.add(profile)
    db.commit()
    return profile


def test_insight_missing_key_returns_503(client, db):
    _insert_profile(db)
    resp = client.post(f"/profiles/{USER}/insight")
    assert resp.status_code == 503
    assert resp.json()["code"] == "ai_not_configured"


def test_insight_missing_profile_returns_404(client, db):
    resp = client.post("/profiles/does-not-exist/insight")
    assert resp.status_code == 404


def test_insight_success(client, db, monkeypatch):
    _insert_profile(db)
    fake_result = InsightResult(
        summary="Friendly and curious.",
        communication_style="Direct and warm.",
        suggested_focus="Try hosting a small meetup.",
    )
    monkeypatch.setattr("app.routers.insight.generate_insight", lambda profile: fake_result)

    resp = client.post(f"/profiles/{USER}/insight")
    assert resp.status_code == 200
    assert resp.json() == fake_result.model_dump()


def test_insight_timeout_returns_504(client, db, monkeypatch):
    _insert_profile(db)

    def raise_timeout(profile):
        raise GeminiTimeoutError("AI insight timed out, please try again.")

    monkeypatch.setattr("app.routers.insight.generate_insight", raise_timeout)
    resp = client.post(f"/profiles/{USER}/insight")
    assert resp.status_code == 504


def test_insight_malformed_returns_502(client, db, monkeypatch):
    _insert_profile(db)

    def raise_malformed(profile):
        raise GeminiMalformedResponseError("AI returned an unexpected response.")

    monkeypatch.setattr("app.routers.insight.generate_insight", raise_malformed)
    resp = client.post(f"/profiles/{USER}/insight")
    assert resp.status_code == 502


def test_insight_service_error_returns_502(client, db, monkeypatch):
    _insert_profile(db)

    def raise_service_error(profile):
        raise GeminiServiceError("AI service error, please try again.")

    monkeypatch.setattr("app.routers.insight.generate_insight", raise_service_error)
    resp = client.post(f"/profiles/{USER}/insight")
    assert resp.status_code == 502


def test_strip_code_fences():
    raw = '```json\n{"a": 1}\n```'
    assert _strip_code_fences(raw) == '{"a": 1}'


def test_parse_and_validate_success():
    raw = '{"summary": "s", "communication_style": "c", "suggested_focus": "f"}'
    result = _parse_and_validate(raw)
    assert result.summary == "s"


def test_parse_and_validate_non_json_raises():
    with pytest.raises(GeminiMalformedResponseError):
        _parse_and_validate("this is not json")


def test_parse_and_validate_missing_field_raises():
    with pytest.raises(GeminiMalformedResponseError):
        _parse_and_validate('{"summary": "s"}')
