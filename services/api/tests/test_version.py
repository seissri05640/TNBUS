from http import HTTPStatus


def test_version_endpoint_returns_metadata(client) -> None:
    response = client.get("/version")

    assert response.status_code == HTTPStatus.OK
    payload = response.json()
    assert payload["name"] == "Traffic Services API"
    assert payload["version"] == "0.1.0"
