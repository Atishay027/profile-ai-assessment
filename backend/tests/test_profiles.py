from app.models import Profile

USER = "user-001"


def _insert_profile(db, **overrides):
    defaults = dict(
        user_id=USER,
        full_name="Jordan Rivera",
        city="Austin",
        occupation="Product Designer",
        bio="Enjoys hiking.",
    )
    defaults.update(overrides)
    profile = Profile(**defaults)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def test_get_existing_profile(client, db):
    _insert_profile(db)
    resp = client.get(f"/profiles/{USER}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["user_id"] == USER
    assert body["full_name"] == "Jordan Rivera"
    assert body["city"] == "Austin"


def test_get_missing_profile_returns_404(client, db):
    resp = client.get("/profiles/does-not-exist")
    assert resp.status_code == 404


def test_valid_partial_update(client, db):
    _insert_profile(db)
    original = client.get(f"/profiles/{USER}").json()

    resp = client.patch(f"/profiles/{USER}", json={"city": "Denver"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["city"] == "Denver"
    assert body["full_name"] == "Jordan Rivera"  # unchanged
    assert body["updated_at"] != original["updated_at"]


def test_update_missing_profile_returns_404(client, db):
    resp = client.patch("/profiles/does-not-exist", json={"city": "Denver"})
    assert resp.status_code == 404


def test_reject_empty_full_name(client, db):
    _insert_profile(db)
    resp = client.patch(f"/profiles/{USER}", json={"full_name": ""})
    assert resp.status_code == 422


def test_reject_empty_city(client, db):
    _insert_profile(db)
    resp = client.patch(f"/profiles/{USER}", json={"city": ""})
    assert resp.status_code == 422


def test_reject_bio_over_limit(client, db):
    _insert_profile(db)
    resp = client.patch(f"/profiles/{USER}", json={"bio": "x" * 501})
    assert resp.status_code == 422


def test_unknown_field_type_rejected(client, db):
    _insert_profile(db)
    resp = client.patch(f"/profiles/{USER}", json={"full_name": 12345})
    assert resp.status_code == 422
