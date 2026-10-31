from datetime import date

from rest_framework import serializers

from .models import Booking, Hotel, Room, User

# ------------------------------------------------------------
# Чтение (ответы API)
# ------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "full_name", "phone", "created_at"]


class HotelSerializer(serializers.ModelSerializer[Hotel]):  # Исправлено: [Hotel]
    class Meta:
        model = Hotel
        fields = ["id", "name", "address", "description", "created_at"]


class RoomSerializer(serializers.ModelSerializer[Room]):  # Исправлено: [Room]
    class Meta:
        model = Room
        fields = ["id", "hotel", "room_number", "description", "price", "created_at"]


class BookingSerializer(serializers.ModelSerializer[Booking]):  # Исправлено: [Booking]
    class Meta:
        model = Booking
        fields = ["id", "user", "room", "date_start", "date_end", "created_at"]


# ------------------------------------------------------------
# Создание (вход API, с валидацией)
# ------------------------------------------------------------

class UserCreateSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["full_name", "phone"]


class HotelCreateSerializer(serializers.ModelSerializer[Hotel]):  # Исправлено: [Hotel]
    class Meta:
        model = Hotel
        fields = ["name", "address", "description"]


class RoomCreateSerializer(serializers.ModelSerializer[Room]):  # Исправлено: [Room]
    class Meta:
        model = Room
        fields = ["hotel", "room_number", "description", "price"]


class BookingCreateSerializer(serializers.ModelSerializer[Booking]):  # Исправлено: [Booking]
    class Meta:
        model = Booking
        fields = ["user", "room", "date_start", "date_end"]

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        raw_start = attrs["date_start"]
        raw_end = attrs["date_end"]
        raw_room = attrs["room"]

        # Проверяем типы для mypy в рантайме без импорта модуля typing
        assert isinstance(raw_start, date)
        assert isinstance(raw_end, date)
        assert isinstance(raw_room, Room)

        # Теперь mypy знает точные типы и разрешает сравнение
        if raw_end < raw_start:
            raise serializers.ValidationError(
                {"date_end": "date_end должен быть больше date_start"}
            )
        
        # проверка пересечения: [start, end) — date_end не занимает ночь
        overlapping = Booking.objects.filter(
            room=raw_room,              # Исправлено: передаем проверенный Room
            date_start__lt=raw_end,     # начало существующей < конец новой
            date_end__gt=raw_start,     # конец существующей > начало новой
        )
        if overlapping.exists():
            raise serializers.ValidationError(
                {"error": "Room is not available for these dates"}
            )
        
        return attrs
