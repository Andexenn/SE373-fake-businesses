from fastapi.testclient import TestClient
from app.main import app
from app.core import init_db

init_db()
client = TestClient(app)

def test_health_has_seeded_data():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["members"] >= 50
    assert data["bookings"] >= 100

def test_catalog_endpoints():
    assert client.get("/branches").status_code == 200
    plans = client.get("/subscriptions/plans")
    assert plans.status_code == 200
    assert plans.json()["count"] >= 1

def test_member_search():
    response = client.get("/members", params={"limit": 5})
    assert response.status_code == 200
    assert len(response.json()["items"]) <= 5


def test_sql_seed_reference_data():
    from app.core import conn
    with conn() as db:
        branches = db.execute("SELECT COUNT(*) FROM branches WHERE is_active=1").fetchone()[0]
        methods = db.execute("SELECT COUNT(*) FROM payment_methods WHERE enabled=1").fetchone()[0]
        activity_types = db.execute("SELECT COUNT(*) FROM activity_types").fetchone()[0]
    assert branches >= 2
    assert methods >= 2
    assert activity_types >= 2


def test_branch_endpoint_uses_sql_seed():
    response = client.get("/branches")
    assert response.status_code == 200
    assert {item["branch_id"] for item in response.json()} >= {"quan-4", "quan-7"}


def test_consultation_availability_endpoint():
    response = client.get("/consultations/availability", params={"date": "2026-10-25", "branch": "quan-7", "activity_type": "class"})
    assert response.status_code == 200
    assert response.json()["date"] == "2026-10-25"
    assert "slots" in response.json()
