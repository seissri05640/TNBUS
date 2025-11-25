from http import HTTPStatus


def test_health_endpoint_returns_status(client) -> None:
    response = client.get("/health")

    assert response.status_code == HTTPStatus.OK
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["environment"] == "local"
    assert isinstance(payload["uptime_seconds"], int)
    assert payload["uptime_seconds"] >= 0
