from tests.conftest import _register_and_login, _auth_header, _seed_admin, _get_token


def test_admin_list_users(client, db):
    _seed_admin(db)
    token = _get_token(client, "admin@blog.com", "admin123")
    _register_and_login(client, db, "u1", "u1@test.com", "pass", "reader")
    res = client.get("/admin/users", headers=_auth_header(token))
    assert res.status_code == 200
    assert len(res.json()) >= 2


def test_admin_get_user(client, db):
    _seed_admin(db)
    token = _get_token(client, "admin@blog.com", "admin123")
    r = client.post("/register", json={
        "username": "u1", "email": "u1@test.com", "password": "pass"
    })
    uid = r.json()["id"]
    res = client.get(f"/admin/users/{uid}", headers=_auth_header(token))
    assert res.status_code == 200
    assert res.json()["email"] == "u1@test.com"


def test_admin_change_role(client, db):
    _seed_admin(db)
    token = _get_token(client, "admin@blog.com", "admin123")
    r = client.post("/register", json={
        "username": "u1", "email": "u1@test.com", "password": "pass"
    })
    uid = r.json()["id"]
    res = client.put(f"/admin/users/{uid}/role", json={"role": "author"}, headers=_auth_header(token))
    assert res.status_code == 200


def test_admin_delete_user(client, db):
    _seed_admin(db)
    token = _get_token(client, "admin@blog.com", "admin123")
    r = client.post("/register", json={
        "username": "u1", "email": "u1@test.com", "password": "pass"
    })
    uid = r.json()["id"]
    res = client.delete(f"/admin/users/{uid}", headers=_auth_header(token))
    assert res.status_code == 200


def test_admin_delete_any_post(client, db):
    _seed_admin(db)
    admin_token = _get_token(client, "admin@blog.com", "admin123")
    author_token = _register_and_login(client, db, "a1", "a1@test.com", "pass", "author")
    create = client.post("/posts/", json={"title": "X", "content": "Y"}, headers=_auth_header(author_token))
    pid = create.json()["id"]
    res = client.delete(f"/admin/posts/{pid}", headers=_auth_header(admin_token))
    assert res.status_code == 200


def test_admin_edit_any_post(client, db):
    _seed_admin(db)
    admin_token = _get_token(client, "admin@blog.com", "admin123")
    author_token = _register_and_login(client, db, "a1", "a1@test.com", "pass", "author")
    create = client.post("/posts/", json={"title": "Old", "content": "Y"}, headers=_auth_header(author_token))
    pid = create.json()["id"]
    res = client.put(f"/admin/posts/{pid}", json={"title": "Fixed"}, headers=_auth_header(admin_token))
    assert res.status_code == 200
    assert res.json()["title"] == "Fixed"


def test_admin_stats(client, db):
    _seed_admin(db)
    token = _get_token(client, "admin@blog.com", "admin123")
    res = client.get("/admin/stats", headers=_auth_header(token))
    assert res.status_code == 200
    assert "total_users" in res.json()
    assert "total_posts" in res.json()


def test_non_admin_cannot_access(client, db):
    token = _register_and_login(client, db, "reader1", "r1@test.com", "pass", "reader")
    res = client.get("/admin/users", headers=_auth_header(token))
    assert res.status_code == 403
