from datetime import datetime, timezone


def now_utc() -> datetime:
    """Single clock source for the app so tests can freeze/monkeypatch time."""
    return datetime.now(timezone.utc)
