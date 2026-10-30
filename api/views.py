from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking, Hotel, Room, User
from .serializers import (
    BookingCreateSerializer,
    BookingSerializer,
    HotelCreateSerializer,
    HotelSerializer,
    RoomCreateSerializer,
    RoomSerializer,
    UserCreateSerializer,
    UserSerializer,
)


# ============================================================
# USERS
# ============================================================

class UserListCreateView(APIView):
    """GET /users — список; POST /users — создать."""

    def get(self, request):
        users = User.objects.all().order_by("id")
        return Response(UserSerializer(users, many=True).data)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
        except IntegrityError:
            return Response(
                {"error": "User with this full_name and phone already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"user_id": user.id}, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    """GET /users/{id} — один; DELETE /users/{id} — удалить."""

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(user).data)

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            user.delete()
        except IntegrityError:
            return Response(
                {"error": "Cannot delete user with bookings (RESTRICT)"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================
# HOTELS
# ============================================================

class HotelListCreateView(APIView):
    """GET /hotels — список; POST /hotels — создать."""

    def get(self, request):
        hotels = Hotel.objects.all().order_by("id")
        return Response(HotelSerializer(hotels, many=True).data)

    def post(self, request):
        serializer = HotelCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            hotel = serializer.save()
        except IntegrityError:
            return Response(
                {"error": "Hotel with this address already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"hotel_id": hotel.id}, status=status.HTTP_201_CREATED)


class HotelDetailView(APIView):
    """GET /hotels/{id} — один; DELETE /hotels/{id} — удалить (CASCADE)."""

    def get(self, request, hotel_id):
        try:
            hotel = Hotel.objects.get(id=hotel_id)
        except Hotel.DoesNotExist:
            return Response({"error": "Hotel not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(HotelSerializer(hotel).data)

    def delete(self, request, hotel_id):
        try:
            hotel = Hotel.objects.get(id=hotel_id)
        except Hotel.DoesNotExist:
            return Response({"error": "Hotel not found"}, status=status.HTTP_404_NOT_FOUND)
        hotel.delete()   # CASCADE: rooms -> bookings
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================
# ROOMS
# ============================================================

class RoomListCreateView(APIView):
    """GET /rooms?hotel_id=&sort=price|created_at&order=asc|desc; POST /rooms."""

    def get(self, request):
        qs = Room.objects.all()

        hotel_id = request.query_params.get("hotel_id")
        if hotel_id:
            qs = qs.filter(hotel_id=hotel_id)

        sort = request.query_params.get("sort", "created_at")
        order = request.query_params.get("order", "asc")

        if sort not in {"price", "created_at"}:
            return Response(
                {"error": "sort must be 'price' or 'created_at'"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if order not in {"asc", "desc"}:
            return Response(
                {"error": "order must be 'asc' or 'desc'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = qs.order_by(sort if order == "asc" else f"-{sort}")
        return Response(RoomSerializer(qs, many=True).data)

    def post(self, request):
        serializer = RoomCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            room = serializer.save()
        except IntegrityError:
            return Response(
                {"error": "Room with this number already exists in this hotel"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"room_id": room.id}, status=status.HTTP_201_CREATED)


class RoomDetailView(APIView):
    """GET /rooms/{id}; DELETE /rooms/{id} (CASCADE: bookings)."""

    def get(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(RoomSerializer(room).data)

    def delete(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================
# BOOKINGS
# ============================================================

class BookingListCreateView(APIView):
    """GET /bookings?room_id=&user_id=; POST /bookings."""

    def get(self, request):
        qs = Booking.objects.all()

        room_id = request.query_params.get("room_id")
        user_id = request.query_params.get("user_id")
        if room_id:
            qs = qs.filter(room_id=room_id)
        if user_id:
            qs = qs.filter(user_id=user_id)

        qs = qs.order_by("date_start")
        return Response(BookingSerializer(qs, many=True).data)

    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            booking = serializer.save()
        except IntegrityError:
            return Response(
                {"error": "Booking already exists for this user/room/dates"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"booking_id": booking.id}, status=status.HTTP_201_CREATED)


class BookingDetailView(APIView):
    """GET /bookings/{id}; DELETE /bookings/{id}."""

    def get(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(BookingSerializer(booking).data)

    def delete(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)