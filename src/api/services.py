import logging  # 🆕 Импортируем модуль логирования
from datetime import date

from rest_framework.exceptions import ValidationError

from .models import Booking, Hotel, Room, User

# 🆕 Инициализируем логгер для текущего модуля
logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    def create_user(full_name: str, phone: str) -> User:
        user = User.objects.create(full_name=full_name, phone=phone)
        logger.info(f"User created successfully: ID {user.id} (Name: {user.full_name})")  # 🆕 Лог
        return user

    @staticmethod
    def delete_user(user_id: int) -> None:
        user = User.objects.get(id=user_id)
        user.delete()
        logger.info(f"User deleted successfully: ID {user_id}")  # 🆕 Лог


class HotelService:
    @staticmethod
    def create_hotel(name: str, address: str, description: str = "") -> Hotel:
        hotel = Hotel.objects.create(name=name, address=address, description=description)
        logger.info(f"Hotel created successfully: ID {hotel.id} (Name: {hotel.name})")  # 🆕 Лог
        return hotel

    @staticmethod
    def delete_hotel(hotel_id: int) -> None:
        hotel = Hotel.objects.get(id=hotel_id)
        hotel.delete()
        logger.info(f"Hotel deleted successfully: ID {hotel_id}")  # 🆕 Лог


class RoomService:
    @staticmethod
    def create_room(hotel_id: int, room_number: str, description: str, price: float) -> Room:
        room = Room.objects.create(
            hotel_id=hotel_id, room_number=room_number, description=description, price=price
        )
        logger.info(
            f"Room created successfully: ID {room.id} (Hotel: {hotel_id}, Number: {room_number})"
        )  # 🆕 Лог
        return room

    @staticmethod
    def delete_room(room_id: int) -> None:
        room = Room.objects.get(id=room_id)
        room.delete()
        logger.info(f"Room deleted successfully: ID {room_id}")  # 🆕 Лог


class BookingService:
    @staticmethod
    def create_booking(user_id: int, room_id: int, date_start: date, date_end: date) -> Booking:
        if date_end < date_start:
            # 🆕 Логируем попытку создания с некорректными датами
            logger.warning(
                f"Booking failed: date_end ({date_end}) "
                f"is before date_start ({date_start}) for user {user_id}"
            )
            raise ValidationError({"date_end": "date_end должен быть больше date_start"})

        overlapping = Booking.objects.filter(
            room_id=room_id,
            date_start__lt=date_end,
            date_end__gt=date_start,
        )
        if overlapping.exists():
            # 🆕 Логируем конфликт бронирования
            logger.warning(
                f"Booking failed: Room {room_id} "
                f"is already occupied for dates {date_start} - {date_end}"
            )
            raise ValidationError({"error": "Room is not available for these dates"})

        booking = Booking.objects.create(
            user_id=user_id, room_id=room_id, date_start=date_start, date_end=date_end
        )
        # 🆕 Бизнес-лог успешного бронирования
        logger.info(
            f"Booking created successfully: ID {booking.id} "
            f"(User: {user_id}, Room: {room_id}, Dates: {date_start} to {date_end})"
        )
        return booking

    @staticmethod
    def delete_booking(booking_id: int) -> None:
        booking = Booking.objects.get(id=booking_id)
        booking.delete()
        logger.info(f"Booking deleted successfully: ID {booking_id}")  # 🆕 Лог
