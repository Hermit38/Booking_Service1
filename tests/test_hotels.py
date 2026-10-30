import pytest
from rest_framework.test import APIClient

from api.models import Hotel


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_create_hotel(client):
    resp = client.post("/hotels", {"name": "Новый", "address": "г. Казань, ул. Ленина, 1"})
    assert resp.status_code == 201
    assert "hotel_id" in resp.json()


@pytest.mark.django_db
def test_create_hotel_duplicate_address(client, hotel):
    resp = client.post("/hotels", {"name": "Другой", "address": hotel.address})
    assert resp.status_code == 400
    assert "error" in resp.json()


@pytest.mark.django_db
def test_list_hotels(client, hotel):
    resp = client.get("/hotels")
    assert resp.status_code == 200
    assert any(h["id"] == hotel.id for h in resp.json())


@pytest.mark.django_db
def test_get_hotel(client, hotel):
    resp = client.get(f"/hotels/{hotel.id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == hotel.id


@pytest.mark.django_db
def test_get_hotel_not_found(client):
    resp = client.get("/hotels/999999")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_delete_hotel(client, hotel):
    resp = client.delete(f"/hotels/{hotel.id}")
    assert resp.status_code == 204
    assert not Hotel.objects.filter(id=hotel.id).exists()