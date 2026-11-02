from rest_framework import status
from rest_framework.generics import get_object_or_404  # <-- Добавили утилиту
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
        user = serializer.save()
        return Response({"user_id": user.id}, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    """GET /users/{id} — один; DELETE /users/{id} — удалить."""

    def get(self, request: Request, user_id: int) -> Response:
        # Ищет объект. Если не находит — выбрасывает ошибку 404,
        # которую ваш custom_exception_handler превратит в {"error": "User not found"}
        user = get_object_or_404(User, id=user_id)
        return Response(UserSerializer(instance=user).data)

    def delete(self, request: Request, user_id: int) -> Response:
        user = get_object_or_404(User, id=user_id)
        user.delete()
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
        hotel = serializer.save()
        return Response({"hotel_id": hotel.id}, status=status.HTTP_201_CREATED)


class HotelDetailView(APIView):
    """GET /hotels/{id} — один; DELETE /hotels/{id} — удалить (CASCADE)."""

    def get(self, request: Request, hotel_id: int) -> Response:
        hotel = get_object_or_404(Hotel, id=hotel_id)
        return Response(HotelSerializer(instance=hotel).data)

    def delete(self, request: Request, hotel_id: int) -> Response:
        hotel = get_object_or_404(Hotel, id=hotel_id)
        hotel.delete()
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
        room = serializer.save()
        return Response({"room_id": room.id}, status=status.HTTP_201_CREATED)


class RoomDetailView(APIView):
    """GET /rooms/{id}; DELETE /rooms/{id} (CASCADE: bookings)."""

    def get(self, request: Request, room_id: int) -> Response:
        room = get_object_or_404(Room, id=room_id)
        return Response(RoomSerializer(instance=room).data)

    def delete(self, request: Request, room_id: int) -> Response:
        room = get_object_or_404(Room, id=room_id)
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
        booking = serializer.save()
        return Response({"booking_id": booking.id}, status=status.HTTP_201_CREATED)


class BookingDetailView(APIView):
    """GET /bookings/{id}; DELETE /bookings/{id}."""

    def get(self, request: Request, booking_id: int) -> Response:
        booking = get_object_or_404(Booking, id=booking_id)
        return Response(BookingSerializer(instance=booking).data)

    def delete(self, request: Request, booking_id: int) -> Response:
        booking = get_object_or_404(Booking, id=booking_id)
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
