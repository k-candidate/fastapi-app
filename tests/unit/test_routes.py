from datetime import date

from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


def test_put_invalid_username():
    response = client.put("/hello/john_doe", json={"dateOfBirth": "2000-01-01"})
    assert response.status_code == 400


def test_get_invalid_username():
    response = client.get("/hello/john_doe")
    assert response.status_code == 400


def test_put_future_date():
    response = client.put("/hello/Alice", json={"dateOfBirth": "2999-01-01"})
    assert response.status_code == 422


def test_put_today_date():
    response = client.put(
        "/hello/Alice",
        json={"dateOfBirth": date.today().isoformat()},
    )
    assert response.status_code == 422


def test_put_malformed_date():
    response = client.put("/hello/Alice", json={"dateOfBirth": "01-01-1990"})
    assert response.status_code == 422


def test_put_missing_date_of_birth():
    response = client.put("/hello/Alice", json={})
    assert response.status_code == 422


def test_put_success(monkeypatch):
    async def fake_upsert(session, username, dob):
        assert username == "Alice"
        assert str(dob) == "1990-01-01"

    monkeypatch.setattr(main.crud, "upsert_user", fake_upsert)
    response = client.put("/hello/Alice", json={"dateOfBirth": "1990-01-01"})
    assert response.status_code == 204
    assert response.content == b""


def test_get_not_found(monkeypatch):
    async def fake_get(session, username):
        return None

    monkeypatch.setattr(main.crud, "get_user", fake_get)
    response = client.get("/hello/Bob")
    assert response.status_code == 404


def test_get_today(monkeypatch):
    class DummyUser:
        date_of_birth = date.today()

    async def fake_get(session, username):
        return DummyUser()

    monkeypatch.setattr(main.crud, "get_user", fake_get)
    response = client.get("/hello/Alice")
    assert response.status_code == 200
    assert response.json()["message"] == "Hello, Alice! Happy birthday!"


def test_get_future_birthday_message(monkeypatch):
    class DummyUser:
        date_of_birth = date(2000, 8, 20)

    async def fake_get(session, username):
        return DummyUser()

    monkeypatch.setattr(main.crud, "get_user", fake_get)
    original = main.date

    class FakeDate(date):
        @classmethod
        def today(cls):
            return cls(2025, 8, 19)

    main.date = FakeDate
    try:
        response = client.get("/hello/Alice")
    finally:
        main.date = original

    assert response.status_code == 200
    assert response.json()["message"] == "Hello, Alice! Your birthday is in 1 day(s)"


def test_calculate_days_to_birthday_for_future_birthday():
    days = main.calculate_days_to_birthday(date(2000, 8, 20), date(2025, 8, 19))
    assert days == 1


def test_calculate_days_to_birthday_for_leap_day():
    days = main.calculate_days_to_birthday(date(2000, 2, 29), date(2025, 2, 28))
    assert days == 1
