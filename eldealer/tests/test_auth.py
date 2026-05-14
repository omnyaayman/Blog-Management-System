from tests.conftest import _register_and_login, _auth_header


def test_register_reader(client):
    res = client.post("/register", json={
        "username": "reader1", "email": "reader1@test.com", "password": "pass123"
    })
    assert res.status_code == 200
    assert res.json()["role"] == "reader"


def test_register_author_forced_to_reader(client):
    # Registration no longer allows choosing role, so it should default to reader regardless of input if extra fields are ignored
    res = client.post("/register", json={
        "username": "author1", "email": "author1@test.com", "password": "pass123", "role": "author"
    })
    assert res.status_code == 200
    assert res.json()["role"] == "reader"


def test_register_admin_ignored_and_forced_to_reader(client):
    res = client.post("/register", json={
        "username": "hacker", "email": "hacker@test.com", "password": "pass123", "role": "admin"
    })
    # Since backend forces "reader", it's no longer "rejected" with 403, it's just "ignored" and registered as reader
    assert res.status_code == 200
    assert res.json()["role"] == "reader"


def test_register_duplicate_email(client):
    client.post("/register", json={
        "username": "u1", "email": "dup@test.com", "password": "pass"
    })
    res = client.post("/register", json={
        "username": "u2", "email": "dup@test.com", "password": "pass"
    })
    assert res.status_code == 400


def test_login_success(client, db):
    _register_and_login(client, db, "loguser", "log@test.com", "pass123", "reader")
    res = client.post("/login", json={"email": "log@test.com", "password": "pass123"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client, db):
    _register_and_login(client, db, "loguser", "log@test.com", "pass123", "reader")
    res = client.post("/login", json={"email": "log@test.com", "password": "wrong"})
    assert res.status_code == 400


def test_login_nonexistent_user(client):
    res = client.post("/login", json={"email": "nobody@test.com", "password": "pass"})
    assert res.status_code == 400


def test_protected_route_no_token(client):
    res = client.get("/posts/999")
    # Public route should work without token
    assert res.status_code in (404, 200)
