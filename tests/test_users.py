import pytest
from rest_framework.test import APIClient

from api.models import User


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_create_user(client):
    resp = client.post("/users", {"full_name": "Иван Иванов", "phone": "+79990000010"})
    assert resp.status_code == 201
    assert "user_id" in resp.json()
    assert User.objects.filter(id=resp.json()["user_id"]).exists()


@pytest.mark.django_db
def test_create_user_duplicate(client, user):
    resp = client.post("/users", {"full_name": user.full_name, "phone": user.phone})
    assert resp.status_code == 400
    assert "error" in resp.json()


@pytest.mark.django_db
def test_list_users(client, user):
    resp = client.get("/users")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(u["id"] == user.id for u in data)


@pytest.mark.django_db
def test_get_user(client, user):
    resp = client.get(f"/users/{user.id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == user.id


@pytest.mark.django_db
def test_get_user_not_found(client):
    resp = client.get("/users/999999")
    assert resp.status_code == 404
    assert "error" in resp.json()


@pytest.mark.django_db
def test_delete_user(client, user):
    resp = client.delete(f"/users/{user.id}")
    assert resp.status_code == 204
    assert not User.objects.filter(id=user.id).exists()