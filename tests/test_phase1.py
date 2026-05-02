import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def register(username="alice", email="alice@example.com", password="secret123"):
    return client.post("/auth/register", json={"username": username, "email": email, "password": password})

def login(username="alice", password="secret123"):
    return client.post("/auth/login", json={"username": username, "password": password})

def auth_headers(username="alice", password="secret123"):
    token = login(username, password).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_health():
    assert client.get("/health").json()["status"] == "ok"

def test_register():
    r = register()
    assert r.status_code == 201
    assert r.json()["username"] == "alice"
    assert "hashed_password" not in r.json()

def test_register_duplicate_username():
    register()
    assert register().status_code == 400

def test_login():
    register()
    r = login()
    assert r.status_code == 200
    assert "access_token" in r.json()

def test_login_wrong_password():
    register()
    assert client.post("/auth/login", json={"username": "alice", "password": "wrong"}).status_code == 401

def test_me():
    register()
    assert client.get("/auth/me", headers=auth_headers()).json()["username"] == "alice"

def test_create_room():
    register()
    r = client.post("/rooms", json={"name": "general"}, headers=auth_headers())
    assert r.status_code == 201
    assert "invite_code" in r.json()

def test_list_rooms():
    register()
    client.post("/rooms", json={"name": "general"}, headers=auth_headers())
    assert len(client.get("/rooms", headers=auth_headers()).json()) == 1

def test_join_room():
    register()
    register("bob", "bob@example.com")
    code = client.post("/rooms", json={"name": "general"}, headers=auth_headers()).json()["invite_code"]
    assert client.post("/rooms/join", json={"invite_code": code}, headers=auth_headers("bob")).status_code == 200

def test_join_invalid_code():
    register()
    assert client.post("/rooms/join", json={"invite_code": "badcode"}, headers=auth_headers()).status_code == 404

def test_get_room():
    register()
    room_id = client.post("/rooms", json={"name": "general"}, headers=auth_headers()).json()["id"]
    assert client.get(f"/rooms/{room_id}", headers=auth_headers()).status_code == 200

def test_get_room_forbidden():
    register()
    register("bob", "bob@example.com")
    room_id = client.post("/rooms", json={"name": "private"}, headers=auth_headers()).json()["id"]
    assert client.get(f"/rooms/{room_id}", headers=auth_headers("bob")).status_code == 403

def test_get_messages_empty():
    register()
    room_id = client.post("/rooms", json={"name": "general"}, headers=auth_headers()).json()["id"]
    r = client.get(f"/rooms/{room_id}/messages", headers=auth_headers())
    assert r.status_code == 200
    assert r.json() == []
