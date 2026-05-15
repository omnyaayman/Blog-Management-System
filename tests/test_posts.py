from tests.conftest import _register_and_login, _auth_header


def test_create_post_as_author(client, db):
    token = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    res = client.post("/posts/", json={"title": "Hello", "content": "World"}, headers=_auth_header(token))
    assert res.status_code == 200
    assert res.json()["title"] == "Hello"


def test_create_post_as_reader_fails(client, db):
    token = _register_and_login(client, db, "reader1", "r1@test.com", "pass", "reader")
    res = client.post("/posts/", json={"title": "X", "content": "Y"}, headers=_auth_header(token))
    assert res.status_code == 403


def test_list_posts(client, db):
    token = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    client.post("/posts/", json={"title": "P1", "content": "C1"}, headers=_auth_header(token))
    res = client.get("/posts/")
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_get_single_post(client, db):
    token = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    create = client.post("/posts/", json={"title": "S", "content": "C"}, headers=_auth_header(token))
    pid = create.json()["id"]
    res = client.get(f"/posts/{pid}")
    assert res.status_code == 200
    assert res.json()["title"] == "S"


def test_update_own_post(client, db):
    token = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    create = client.post("/posts/", json={"title": "Old", "content": "C"}, headers=_auth_header(token))
    pid = create.json()["id"]
    res = client.put(f"/posts/{pid}", json={"title": "New"}, headers=_auth_header(token))
    assert res.status_code == 200
    assert res.json()["title"] == "New"


def test_update_other_post_fails(client, db):
    t1 = _register_and_login(client, db, "a1", "a1@test.com", "pass", "author")
    t2 = _register_and_login(client, db, "a2", "a2@test.com", "pass", "author")
    create = client.post("/posts/", json={"title": "X", "content": "Y"}, headers=_auth_header(t1))
    pid = create.json()["id"]
    res = client.put(f"/posts/{pid}", json={"title": "Z"}, headers=_auth_header(t2))
    assert res.status_code == 403


def test_delete_own_post(client, db):
    token = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    create = client.post("/posts/", json={"title": "Del", "content": "C"}, headers=_auth_header(token))
    pid = create.json()["id"]
    res = client.delete(f"/posts/{pid}", headers=_auth_header(token))
    assert res.status_code == 200


def test_view_count_increments(client, db):
    token = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    create = client.post("/posts/", json={"title": "V", "content": "C"}, headers=_auth_header(token))
    pid = create.json()["id"]
    client.get(f"/posts/{pid}")
    client.get(f"/posts/{pid}")
    res = client.get(f"/posts/{pid}")
    assert res.json()["view_count"] >= 3


def test_post_stats(client, db):
    token = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    create = client.post("/posts/", json={"title": "S", "content": "C"}, headers=_auth_header(token))
    pid = create.json()["id"]
    res = client.get(f"/posts/{pid}/stats")
    assert res.status_code == 200
    assert "comment_count" in res.json()
    assert "reactions" in res.json()


def test_my_posts(client, db):
    token = _register_and_login(client, db, "author1", "a1@test.com", "pass", "author")
    client.post("/posts/", json={"title": "Mine", "content": "C"}, headers=_auth_header(token))
    res = client.get("/my/posts", headers=_auth_header(token))
    assert res.status_code == 200
    assert len(res.json()) >= 1
