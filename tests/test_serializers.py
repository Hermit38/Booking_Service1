import pytest
from api.models import Booking
from api.serializers import BookingCreateSerializer


@pytest.mark.django_db
def test_serializer_date_end_before_start(user, room):
    s = BookingCreateSerializer(data={
        "user": user.id, "room": room.id,
        "date_start": "2026-05-05", "date_end": "2026-05-01",
    })
    assert s.is_valid() is False
    assert "date_end" in s.errors


@pytest.mark.django_db
def test_serializer_overlap(user, room):
    Booking.objects.create(user=user, room=room, date_start="2026-06-20", date_end="2026-06-25")
    s = BookingCreateSerializer(data={
        "user": user.id, "room": room.id,
        "date_start": "2026-06-23", "date_end": "2026-06-27",
    })
    assert s.is_valid() is False
    assert "error" in s.errors