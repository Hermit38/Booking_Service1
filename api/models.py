from django.db import models


class User(models.Model):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["phone"], name="users_phone_idx"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["full_name", "phone"], name="users_name_phone_uniq"),
        ]


class Hotel(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hotels"
        indexes = [
            models.Index(fields=["name"], name="hotels_name_idx"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["address"], name="hotels_address_uniq"),
        ]


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="rooms")
    room_number = models.CharField(max_length=20)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rooms"
        indexes = [
            models.Index(fields=["hotel", "price"], name="rooms_hotel_price_idx"),
            models.Index(fields=["hotel", "created_at"], name="rooms_hotel_created_at_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["hotel", "room_number"],
                name="rooms_hotel_number_uniq",
            ),
        ]


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="bookings")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    date_start = models.DateField()
    date_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bookings"
        indexes = [
            models.Index(fields=["room", "date_start"], name="bookings_room_start_idx"),
            models.Index(fields=["user", "date_start"], name="bookings_user_start_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(date_end__gte=models.F("date_start")),
                name="bookings_dates_check",
            ),
            models.UniqueConstraint(
                fields=["user", "room", "date_start", "date_end"],
                name="bookings_user_room_dates_uniq",
            ),
        ]