import os
import time
import urllib.error
import urllib.request

import pytest

BASE_URL = os.getenv("INTEGRATION_BASE_URL", "http://localhost:8000")


def wait_for_service(url: str, timeout: int = 30) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    return
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
        time.sleep(0.5)
    raise RuntimeError(f"Service {url} did not become ready in time")


@pytest.fixture(autouse=True, scope="session")
def ensure_service_is_up() -> None:
    wait_for_service(f"{BASE_URL}/hello/nonexistent")
