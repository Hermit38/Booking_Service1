from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from api.models import Booking, Hotel, Room


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_create_booking(client, user, room):
    resp = client.post("/bookings", {
        "user": user.id, "room": room.id,
        "date_start": "2026-05-01", "date_end": "2026-05-05",
    })
    assert resp.status_code == 201
    assert "booking_id" in resp.json()


@pytest.mark.django_db
def test_create_booking_date_end_before_start(client, user, room):
    resp = client.post("/bookings", {
        "user": user.id, "room": room.id,
        "date_start": "2026-05-05", "date_end": "2026-05-01",
    })
    assert resp.status_code == 400
    assert "error" in resp.json()


@pytest.mark.django_db
def test_create_booking_invalid_date(client, user, room):
    resp = client.post("/bookings", {
        "user": user.id, "room": room.id,
        "date_start": "2026-13-45", "date_end": "2026-05-05",
    })
    assert resp.status_code == 400
    assert "error" in resp.json()


@pytest.mark.django_db
def test_create_booking_nonexistent_room(client, user):
    resp = client.post("/bookings", {
        "user": user.id, "room": 999999,
        "date_start": "2026-05-01", "date_end": "2026-05-05",
    })
    assert resp.status_code == 400
    assert "error" in resp.json()


@pytest.mark.django_db
def test_create_booking_overlap(client, user, room):
    # существующая [2026-06-20, 2026-06-25]
    Booking.objects.create(
        user=user, room=room,
        date_start="2026-06-20", date_end="2026-06-25",
    )
    # пересекается [2026-06-23, 2026-06-27] → 400
    resp = client.post("/bookings", {
        "user": user.id, "room": room.id,
        "date_start": "2026-06-23", "date_end": "2026-06-27",
    })
    assert resp.status_code == 400
    assert "error" in resp.json()


@pytest.mark.django_db
def test_create_booking_no_overlap_after(client, user, room):
    Booking.objects.create(user=user, room=room, date_start="2026-06-20", date_end="2026-06-25")
    # после выезда [2026-06-26, 2026-06-28] → 201
    resp = client.post("/bookings", {
        "user": user.id, "room": room.id,
        "date_start": "2026-06-26", "date_end": "2026-06-28",
    })
    assert resp.status_code == 201


@pytest.mark.django_db
def test_create_booking_checkin_on_checkout_day(client, user, room):
    Booking.objects.create(user=user, room=room, date_start="2026-06-20", date_end="2026-06-25")
    # заезд в день выезда [2026-06-25, 2026-06-27] → 201 (вариант `<`)
    resp = client.post("/bookings", {
        "user": user.id, "room": room.id,
        "date_start": "2026-06-25", "date_end": "2026-06-27",
    })
    assert resp.status_code == 201


@pytest.mark.django_db
def test_list_bookings_by_room(client, user, room):
    Booking.objects.create(user=user, room=room, date_start="2026-05-10", date_end="2026-05-12")
    Booking.objects.create(user=user, room=room, date_start="2026-05-01", date_end="2026-05-03")
    resp = client.get(f"/bookings?room_id={room.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    # сортировка по date_start: 05-01, 05-10
    assert data[0]["date_start"] == "2026-05-01"
    assert data[1]["date_start"] == "2026-05-10"


@pytest.mark.django_db
def test_list_bookings_by_user(client, user, room):
    hotel2 = Hotel.objects.create(name="Другой", address="г. X, ул. Y, 2")
    room2 = Room.objects.create(hotel=hotel2, room_number="201", description="B", price="3000.00")
    Booking.objects.create(user=user, room=room, date_start="2026-05-01", date_end="2026-05-03")
    Booking.objects.create(user=user, room=room2, date_start="2026-06-01", date_end="2026-06-03")
    resp = client.get(f"/bookings?user_id={user.id}")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.django_db
def test_get_booking(client, user, room):
    b = Booking.objects.create(user=user, room=room, date_start="2026-05-01", date_end="2026-05-03")
    resp = client.get(f"/bookings/{b.id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == b.id


@pytest.mark.django_db
def test_delete_booking(client, user, room):
    b = Booking.objects.create(user=user, room=room, date_start="2026-05-01", date_end="2026-05-03")
    resp = client.delete(f"/bookings/{b.id}")
    assert resp.status_code == 204
    assert not Booking.objects.filter(id=b.id).exists()