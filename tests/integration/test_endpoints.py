import json
import os
from datetime import date, timedelta
import urllib.error
import urllib.request

BASE_URL = os.getenv("INTEGRATION_BASE_URL", "http://localhost:8000")


def make_request(method: str, path: str, payload: dict[str, str] | None = None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(request) as response:
            body = response.read().decode()
            return response.status, body
    except urllib.error.HTTPError as error:
        body = error.read().decode()
        return error.code, body


def past_date_for(month: int, day: int) -> date:
    current_year = date.today().year
    for year in range(current_year - 1, current_year - 9, -1):
        try:
            return date(year, month, day)
        except ValueError:
            continue
    raise AssertionError("Could not build a past date for the requested month/day")


def test_integration_put_and_get_known_birthday_message() -> None:
    target = date.today() + timedelta(days=1)
    birth_date = past_date_for(target.month, target.day)

    status_code, _ = make_request(
        "PUT",
        "/hello/IntegrationAlice",
        {"dateOfBirth": birth_date.isoformat()},
    )
    assert status_code == 204

    status_code, body = make_request("GET", "/hello/IntegrationAlice")
    assert status_code == 200
    data = json.loads(body)
    assert data["message"] == "Hello, IntegrationAlice! Your birthday is in 1 day(s)"


def test_integration_put_update_changes_stored_birthday() -> None:
    first_target = date.today() + timedelta(days=2)
    second_target = date.today() + timedelta(days=1)

    first_birth_date = past_date_for(first_target.month, first_target.day)
    second_birth_date = past_date_for(second_target.month, second_target.day)

    status_code, _ = make_request(
        "PUT",
        "/hello/IntegrationUpdateUser",
        {"dateOfBirth": first_birth_date.isoformat()},
    )
    assert status_code == 204

    status_code, body = make_request("GET", "/hello/IntegrationUpdateUser")
    assert status_code == 200
    assert json.loads(body)["message"] == (
        "Hello, IntegrationUpdateUser! Your birthday is in 2 day(s)"
    )

    status_code, _ = make_request(
        "PUT",
        "/hello/IntegrationUpdateUser",
        {"dateOfBirth": second_birth_date.isoformat()},
    )
    assert status_code == 204

    status_code, body = make_request("GET", "/hello/IntegrationUpdateUser")
    assert status_code == 200
    assert json.loads(body)["message"] == (
        "Hello, IntegrationUpdateUser! Your birthday is in 1 day(s)"
    )


def test_integration_get_happy_birthday_message() -> None:
    today = date.today()
    birth_date = past_date_for(today.month, today.day)

    status_code, _ = make_request(
        "PUT",
        "/hello/IntegrationBirthdayUser",
        {"dateOfBirth": birth_date.isoformat()},
    )
    assert status_code == 204

    status_code, body = make_request("GET", "/hello/IntegrationBirthdayUser")
    assert status_code == 200
    assert json.loads(body)["message"] == (
        "Hello, IntegrationBirthdayUser! Happy birthday!"
    )


def test_integration_get_not_found() -> None:
    status_code, _ = make_request("GET", "/hello/NoSuchUser")
    assert status_code == 404


def test_integration_invalid_username_on_put() -> None:
    status_code, _ = make_request(
        "PUT",
        "/hello/invalid_user",
        {"dateOfBirth": "1990-01-01"},
    )
    assert status_code == 400


def test_integration_invalid_username_on_get() -> None:
    status_code, _ = make_request("GET", "/hello/invalid_user")
    assert status_code == 400


def test_integration_invalid_future_date() -> None:
    status_code, _ = make_request(
        "PUT",
        "/hello/Alice",
        {"dateOfBirth": "2999-01-01"},
    )
    assert status_code == 422


def test_integration_today_date_is_rejected() -> None:
    status_code, _ = make_request(
        "PUT",
        "/hello/Alice",
        {"dateOfBirth": date.today().isoformat()},
    )
    assert status_code == 422


def test_integration_malformed_date_is_rejected() -> None:
    status_code, _ = make_request(
        "PUT",
        "/hello/Alice",
        {"dateOfBirth": "01-01-1990"},
    )
    assert status_code == 422


def test_integration_missing_date_of_birth_is_rejected() -> None:
    status_code, _ = make_request("PUT", "/hello/Alice", {})
    assert status_code == 422
