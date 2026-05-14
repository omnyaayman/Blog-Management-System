from tests.conftest import _register_and_login, _auth_header


def _make_post(client, db, token):
    res = client.post("/posts/", json={"title": "P", "content": "C"}, headers=_auth_header(token))
    return res.json()["id"]


def test_add_comment(client, db):
    at = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    pid = _make_post(client, db, at)
    rt = _register_and_login(client, db, "reader1", "r1@test.com", "pass", "reader")
    res = client.post(f"/posts/{pid}/comments", json={"content": "Nice!"}, headers=_auth_header(rt))
    assert res.status_code == 200
    assert res.json()["content"] == "Nice!"


def test_nested_reply(client, db):
    at = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    pid = _make_post(client, db, at)
    rt = _register_and_login(client, db, "reader1", "r1@test.com", "pass", "reader")
    c = client.post(f"/posts/{pid}/comments", json={"content": "Top"}, headers=_auth_header(rt))
    cid = c.json()["id"]
    reply = client.post(
        f"/posts/{pid}/comments/{cid}/reply",
        json={"content": "Reply"},
        headers=_auth_header(rt),
    )
    assert reply.status_code == 200
    assert reply.json()["parent_id"] == cid


def test_edit_own_comment(client, db):
    at = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    pid = _make_post(client, db, at)
    rt = _register_and_login(client, db, "reader1", "r1@test.com", "pass", "reader")
    c = client.post(f"/posts/{pid}/comments", json={"content": "Old"}, headers=_auth_header(rt))
    cid = c.json()["id"]
    res = client.put(f"/comments/{cid}", json={"content": "New"}, headers=_auth_header(rt))
    assert res.status_code == 200
    assert res.json()["content"] == "New"


def test_delete_own_comment(client, db):
    at = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    pid = _make_post(client, db, at)
    rt = _register_and_login(client, db, "reader1", "r1@test.com", "pass", "reader")
    c = client.post(f"/posts/{pid}/comments", json={"content": "Bye"}, headers=_auth_header(rt))
    cid = c.json()["id"]
    res = client.delete(f"/comments/{cid}", headers=_auth_header(rt))
    assert res.status_code == 200


def test_edit_other_comment_fails(client, db):
    at = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    pid = _make_post(client, db, at)
    r1 = _register_and_login(client, db, "reader1", "r1@test.com", "pass", "reader")
    r2 = _register_and_login(client, db, "reader2", "r2@test.com", "pass", "reader")
    c = client.post(f"/posts/{pid}/comments", json={"content": "Mine"}, headers=_auth_header(r1))
    cid = c.json()["id"]
    res = client.put(f"/comments/{cid}", json={"content": "Hacked"}, headers=_auth_header(r2))
    assert res.status_code == 403


def test_comment_without_auth_fails(client, db):
    at = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    pid = _make_post(client, db, at)
    res = client.post(f"/posts/{pid}/comments", json={"content": "Anon"})
    assert res.status_code == 401
