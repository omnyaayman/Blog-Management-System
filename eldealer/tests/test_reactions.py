from tests.conftest import _register_and_login, _auth_header


def _make_post(client, db, token):
    res = client.post("/posts/", json={"title": "P", "content": "C"}, headers=_auth_header(token))
    return res.json()["id"]


def test_add_reaction(client, db):
    at = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    pid = _make_post(client, db, at)
    rt = _register_and_login(client, db, "reader1", "r1@test.com", "pass", "reader")
    res = client.post(f"/posts/{pid}/react", json={"type": "like"}, headers=_auth_header(rt))
    assert res.status_code == 200
    assert res.json()["action"] == "added"


def test_toggle_reaction_same_type_removes(client, db):
    at = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    pid = _make_post(client, db, at)
    rt = _register_and_login(client, db, "reader1", "r1@test.com", "pass", "reader")
    headers = _auth_header(rt)
    client.post(f"/posts/{pid}/react", json={"type": "like"}, headers=headers)
    res = client.post(f"/posts/{pid}/react", json={"type": "like"}, headers=headers)
    assert res.json()["action"] == "removed"


def test_toggle_reaction_different_type_changes(client, db):
    at = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    pid = _make_post(client, db, at)
    rt = _register_and_login(client, db, "reader1", "r1@test.com", "pass", "reader")
    headers = _auth_header(rt)
    client.post(f"/posts/{pid}/react", json={"type": "like"}, headers=headers)
    res = client.post(f"/posts/{pid}/react", json={"type": "love"}, headers=headers)
    assert res.json()["action"] == "changed"
    assert res.json()["reaction"]["type"] == "love"


def test_reaction_without_auth_fails(client, db):
    at = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    pid = _make_post(client, db, at)
    res = client.post(f"/posts/{pid}/react", json={"type": "like"})
    assert res.status_code == 401


def test_reaction_on_nonexistent_post(client, db):
    rt = _register_and_login(client, db, "reader1", "r1@test.com", "pass", "reader")
    res = client.post("/posts/9999/react", json={"type": "like"}, headers=_auth_header(rt))
    assert res.status_code == 404


def test_metrics_endpoint(client, db):
    res = client.get("/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "total_requests" in data
    assert "total_errors" in data
    assert "cache_hits" in data
    assert "avg_response_time_ms" in data
