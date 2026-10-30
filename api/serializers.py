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
        if attrs["date_end"] < attrs["date_start"]:
            raise serializers.ValidationError(
                {"date_end": "date_end должен быть больше date_start"}
            )
        return attrs