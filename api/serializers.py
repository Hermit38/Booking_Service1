from rest_framework import serializers

from .models import Booking, Hotel, Room, User


# ------------------------------------------------------------
# Чтение (ответы API)
# ------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "phone", "created_at"]


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ["id", "name", "address", "description", "created_at"]


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "hotel", "room_number", "description", "price", "created_at"]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["id", "user", "room", "date_start", "date_end", "created_at"]


# ------------------------------------------------------------
# Создание (вход API, с валидацией)
# ------------------------------------------------------------

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["full_name", "phone"]


class HotelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ["name", "address", "description"]


class RoomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["hotel", "room_number", "description", "price"]


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["user", "room", "date_start", "date_end"]

    def validate(self, attrs):
        date_start = attrs["date_start"]
        date_end = attrs["date_end"]

        if date_end < date_start:
            raise serializers.ValidationError(
                {"date_end": "date_end должен быть больше date_start"}
            )
        
        # проверка пересечения: [start, end) — date_end не занимает ночь
        overlapping = Booking.objects.filter(
            room=attrs["room"],
            date_start__lt=date_end,   # начало существующей < конец новой
            date_end__gt=date_start,   # конец существующей > начало новой
        )
        if overlapping.exists():
            raise serializers.ValidationError(
                {"error": "Room is not available for these dates"}
            )
        
        return attrs