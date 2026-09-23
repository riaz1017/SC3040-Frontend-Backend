import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_student_cannot_choose_tutor_at_register(client):
    res = client.post(
        "/auth/register",
        json={"name": "New Student", "email": "new.student@e.ntu.edu.sg", "password": "password123"},
    )
    assert res.status_code == 200
    assert res.json()["account"]["tutor_role"] is False
    assert res.json()["account"]["role"] == "student"


def test_login_query_and_match(client):
    res = client.post(
        "/auth/login",
        json={"email": "riaz@e.ntu.edu.sg", "password": "password123"},
    )
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    query = client.post(
        "/queries",
        json={"module": "SC2001 Algorithms", "text": "Why does Dijkstra fail with negative edge weights?"},
        headers=headers,
    )
    assert query.status_code == 200
    query_id = query.json()["id"]

    matches = client.post(f"/queries/{query_id}/matches", headers=headers)
    assert matches.status_code == 200
    names = [m["tutor_name"] for m in matches.json()]
    assert "Aisyah Rahman" in names
    assert "Marcus Lee" not in names
