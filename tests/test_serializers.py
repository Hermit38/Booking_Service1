import pytest

from api.models import Booking, Hotel, Room
from api.serializers import (
    BookingCreateSerializer,
    HotelCreateSerializer,
    RoomCreateSerializer,
    UserCreateSerializer,
)


# ============================================================
# Booking — невалидные данные (parametrize)
# ============================================================

@pytest.mark.parametrize("data, error_field", [
    # невалидные даты
    ({"date_start": "2026-05-05", "date_end": "2026-05-01"}, "date_end"),
    ({"date_start": "2026-13-45", "date_end": "2026-05-05"}, "date_start"),
    # отсутствие дат
    ({}, "date_start"),
    # несуществующий FK
    ({"date_start": "2026-05-01", "date_end": "2026-05-05", "room": 999999}, "room"),
    ({"date_start": "2026-05-01", "date_end": "2026-05-05", "user": 999999}, "user"),
])
@pytest.mark.django_db
def test_booking_invalid(user, room, data, error_field):
    payload = {"user": user.id, "room": room.id, **data}
    s = BookingCreateSerializer(data=payload)
    assert s.is_valid() is False
    assert error_field in s.errors


@pytest.mark.django_db
def test_booking_date_end_equals_start(user, room):
    # [start, end) — один день (start == end) допустим
    s = BookingCreateSerializer(data={
        "user": user.id, "room": room.id,
        "date_start": "2026-05-05", "date_end": "2026-05-05",
    })
    assert s.is_valid() is True


# ============================================================
# Booking — пересечение (parametrize): существующая [20,25]
# ============================================================

@pytest.mark.parametrize("new_start, new_end, expected_valid", [
    ("2026-06-23", "2026-06-27", False),   # внутри — пересекается
    ("2026-06-19", "2026-06-26", False),   # покрывает — пересекается
    ("2026-06-21", "2026-06-22", False),   # внутри — пересекается
    ("2026-06-10", "2026-06-15", True),    # до — не пересекается
    ("2026-06-26", "2026-06-28", True),    # после — не пересекается
    ("2026-06-25", "2026-06-27", True),    # заезд в день выезда — не пересекается
    ("2026-06-10", "2026-06-20", True),    # выезд в день заезда — не пересекается
])
@pytest.mark.django_db
def test_booking_overlap(user, room, new_start, new_end, expected_valid):
    Booking.objects.create(user=user, room=room, date_start="2026-06-20", date_end="2026-06-25")
    s = BookingCreateSerializer(data={
        "user": user.id, "room": room.id,
        "date_start": new_start, "date_end": new_end,
    })
    assert s.is_valid() is expected_valid


@pytest.mark.django_db
def test_booking_overlap_different_room(user, room):
    other_hotel = Hotel.objects.create(name="Другой", address="г. X, ул. Y, 2")
    other_room = Room.objects.create(
        hotel=other_hotel, room_number="201", description="B", price="3000.00",
    )
    Booking.objects.create(user=user, room=room, date_start="2026-06-20", date_end="2026-06-25")
    s = BookingCreateSerializer(data={
        "user": user.id, "room": other_room.id,
        "date_start": "2026-06-23", "date_end": "2026-06-27",
    })
    assert s.is_valid() is True


# ============================================================
# User
# ============================================================

@pytest.mark.django_db
def test_user_serializer_duplicate(user):
    s = UserCreateSerializer(data={"full_name": user.full_name, "phone": user.phone})
    assert s.is_valid() is False
    assert "non_field_errors" in s.errors


@pytest.mark.django_db
def test_user_serializer_same_phone_different_name(user):
    s = UserCreateSerializer(data={"full_name": "Другое Имя", "phone": user.phone})
    assert s.is_valid() is True


@pytest.mark.django_db
def test_user_serializer_valid(user):
    s = UserCreateSerializer(data={"full_name": "Другой", "phone": "+79990000099"})
    assert s.is_valid() is True


# ============================================================
# Hotel
# ============================================================

@pytest.mark.django_db
def test_hotel_serializer_duplicate_address(hotel):
    s = HotelCreateSerializer(data={"name": "Другой", "address": hotel.address})
    assert s.is_valid() is False
    assert "address" in s.errors


@pytest.mark.django_db
def test_hotel_serializer_valid(hotel):
    s = HotelCreateSerializer(data={"name": "Новый", "address": "г. Казань, ул. Ленина, 1"})
    assert s.is_valid() is True


# ============================================================
# Room
# ============================================================

@pytest.mark.django_db
def test_room_serializer_duplicate_number(room):
    s = RoomCreateSerializer(data={
        "hotel": room.hotel.id, "room_number": room.room_number,
        "description": "Другой", "price": "6000.00",
    })
    assert s.is_valid() is False
    assert "non_field_errors" in s.errors


@pytest.mark.django_db
def test_room_serializer_same_number_different_hotel(room):
    other_hotel = Hotel.objects.create(name="Другой", address="г. X, ул. Y, 2")
    s = RoomCreateSerializer(data={
        "hotel": other_hotel.id, "room_number": room.room_number,
        "description": "Другой", "price": "6000.00",
    })
    assert s.is_valid() is True


@pytest.mark.django_db
def test_room_serializer_valid(hotel):
    s = RoomCreateSerializer(data={
        "hotel": hotel.id, "room_number": "999",
        "description": "New", "price": "1000.00",
    })
    assert s.is_valid() is True