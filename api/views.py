from django.db import IntegrityError
from rest_framework import status
from rest_framework.request import Request
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

    def get(self, request: Request) -> Response:
        users = User.objects.all().order_by("id")
        return Response(UserSerializer(instance=users, many=True).data)

    def post(self, request: Request) -> Response:
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

    def get(self, request: Request, user_id: int) -> Response:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(instance=user).data)

    def delete(self, request: Request, user_id: int) -> Response:
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

    def get(self, request: Request) -> Response:
        hotels = Hotel.objects.all().order_by("id")
        return Response(HotelSerializer(instance=hotels, many=True).data)

    def post(self, request: Request) -> Response:
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

    def get(self, request: Request, hotel_id: int) -> Response:
        try:
            hotel = Hotel.objects.get(id=hotel_id)
        except Hotel.DoesNotExist:
            return Response({"error": "Hotel not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(HotelSerializer(instance=hotel).data)

    def delete(self, request: Request, hotel_id: int) -> Response:
        try:
            hotel = Hotel.objects.get(id=hotel_id)
        except Hotel.DoesNotExist:
            return Response({"error": "Hotel not found"}, status=status.HTTP_404_NOT_FOUND)
        hotel.delete()  # CASCADE: rooms -> bookings
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================
# ROOMS
# ============================================================


class RoomListCreateView(APIView):
    """GET /rooms?hotel_id=&sort=price|created_at&order=asc|desc; POST /rooms."""

    def get(self, request: Request) -> Response:
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
        return Response(RoomSerializer(instance=qs, many=True).data)

    def post(self, request: Request) -> Response:
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

    def get(self, request: Request, room_id: int) -> Response:
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(RoomSerializer(instance=room).data)

    def delete(self, request: Request, room_id: int) -> Response:
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

    def get(self, request: Request) -> Response:
        qs = Booking.objects.all()

        room_id = request.query_params.get("room_id")
        user_id = request.query_params.get("user_id")
        if room_id:
            qs = qs.filter(room_id=room_id)
        if user_id:
            qs = qs.filter(user_id=user_id)

        qs = qs.order_by("date_start")
        return Response(BookingSerializer(instance=qs, many=True).data)

    def post(self, request: Request) -> Response:
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

    def get(self, request: Request, booking_id: int) -> Response:
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(BookingSerializer(instance=booking).data)

    def delete(self, request: Request, booking_id: int) -> Response:
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
