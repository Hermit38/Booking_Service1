import pytest

from api.models import Hotel, Room, User


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create(full_name="Тест Тестов", phone="+70001112233")


@pytest.fixture
def hotel(db: None) -> Hotel:
    return Hotel.objects.create(
        name="Тест Отель",
        address="г. Тест, ул. Тестовая, 1",
    )


@pytest.fixture
def room(db: None, hotel: Hotel) -> Room:
    return Room.objects.create(
        hotel=hotel,
        room_number="101",
        description="Standard",
        price="5000.00",
    )