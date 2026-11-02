from datetime import date

from .models import Booking, Room


class RoomRepository:
    @staticmethod
    def get_filtered_rooms(hotel_id: str | None, sort_field: str, order: str) -> list[Room]:
        qs = Room.objects.all()
        if hotel_id:
            qs = qs.filter(hotel_id=hotel_id)
        ordering = sort_field if order == "asc" else f"-{sort_field}"
        return list(qs.order_by(ordering))


class BookingRepository:
    @staticmethod
    def has_overlapping_bookings(room: Room, date_start: date, date_end: date) -> bool:
        return Booking.objects.filter(
            room=room,
            date_start__lt=date_end,
            date_end__gt=date_start,
        ).exists()
