"""Functional, negative and performance tests for the /posts REST API."""
import pytest

REQUIRED_FIELDS = {"id", "userId", "title", "body"}


# ---------- GET /posts ----------
def test_list_posts_returns_200_and_json(base_url, session):
    r = session.get(f"{base_url}/posts")
    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("application/json")
    assert isinstance(r.json(), list)


def test_every_post_has_required_fields(base_url, session):
    posts = session.get(f"{base_url}/posts").json()
    assert posts, "expected at least one post"
    for post in posts:
        assert REQUIRED_FIELDS <= post.keys()


def test_filter_posts_by_user(base_url, session):
    posts = session.get(f"{base_url}/posts", params={"userId": 1}).json()
    assert posts
    assert all(p["userId"] == 1 for p in posts)


# ---------- GET /posts/<id> ----------
@pytest.mark.parametrize("post_id", [1, 2, 3])
def test_get_single_post(base_url, session, post_id):
    r = session.get(f"{base_url}/posts/{post_id}")
    assert r.status_code == 200
    assert r.json()["id"] == post_id


@pytest.mark.parametrize("bad_id", [9999, 0])
def test_get_missing_post_returns_404(base_url, session, bad_id):
    r = session.get(f"{base_url}/posts/{bad_id}")
    assert r.status_code == 404
    assert "error" in r.json()


# ---------- POST /posts ----------
def test_create_post_returns_201_and_new_id(base_url, session):
    payload = {"userId": 1, "title": "new title", "body": "new body"}
    r = session.post(f"{base_url}/posts", json=payload)
    assert r.status_code == 201
    created = r.json()
    assert created["title"] == payload["title"]
    assert created["body"] == payload["body"]
    assert "id" in created


def test_created_post_can_be_fetched(base_url, session):
    created = session.post(f"{base_url}/posts",
                           json={"title": "persist me", "body": "check"}).json()
    r = session.get(f"{base_url}/posts/{created['id']}")
    assert r.status_code == 200
    assert r.json()["title"] == "persist me"


@pytest.mark.parametrize("payload", [{}, {"title": "no body"}, {"body": "no title"}])
def test_create_post_with_missing_fields_returns_400(base_url, session, payload):
    r = session.post(f"{base_url}/posts", json=payload)
    assert r.status_code == 400


# ---------- DELETE /posts/<id> ----------
def test_delete_post_then_get_returns_404(base_url, session):
    created = session.post(f"{base_url}/posts",
                           json={"title": "delete me", "body": "x"}).json()
    assert session.delete(f"{base_url}/posts/{created['id']}").status_code == 200
    assert session.get(f"{base_url}/posts/{created['id']}").status_code == 404


def test_delete_missing_post_returns_404(base_url, session):
    assert session.delete(f"{base_url}/posts/9999").status_code == 404


# ---------- Basic performance check ----------
def test_list_posts_responds_within_one_second(base_url, session):
    r = session.get(f"{base_url}/posts")
    assert r.elapsed.total_seconds() < 1.0
