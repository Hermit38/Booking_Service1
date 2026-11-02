from datetime import date

from rest_framework.exceptions import ValidationError

from .models import Booking, Hotel, Room, User


class UserService:
    @staticmethod
    def create_user(full_name: str, phone: str) -> User:
        # Здесь в будущем может быть проверка формата телефона или отправка SMS-приветствия
        return User.objects.create(full_name=full_name, phone=phone)

    @staticmethod
    def delete_user(user_id: int) -> None:
        user = User.objects.get(id=user_id)
        user.delete()


class HotelService:
    @staticmethod
    def create_hotel(name: str, address: str, description: str = "") -> Hotel:
        return Hotel.objects.create(name=name, address=address, description=description)

    @staticmethod
    def delete_hotel(hotel_id: int) -> None:
        hotel = Hotel.objects.get(id=hotel_id)
        hotel.delete()


class RoomService:
    @staticmethod
    def create_room(hotel_id: int, room_number: str, description: str, price: float) -> Room:
        # Можно добавить проверку: существует ли отель, перед тем как создавать комнату
        return Room.objects.create(
            hotel_id=hotel_id, room_number=room_number, description=description, price=price
        )

    @staticmethod
    def delete_room(room_id: int) -> None:
        room = Room.objects.get(id=room_id)
        room.delete()


class BookingService:
    @staticmethod
    def create_booking(user_id: int, room_id: int, date_start: date, date_end: date) -> Booking:
        if date_end < date_start:
            raise ValidationError({"date_end": "date_end должен быть больше date_start"})

        overlapping = Booking.objects.filter(
            room_id=room_id,
            date_start__lt=date_end,
            date_end__gt=date_start,
        )
        if overlapping.exists():
            raise ValidationError({"error": "Room is not available for these dates"})

        return Booking.objects.create(
            user_id=user_id, room_id=room_id, date_start=date_start, date_end=date_end
        )

    @staticmethod
    def delete_booking(booking_id: int) -> None:
        booking = Booking.objects.get(id=booking_id)
        booking.delete()
