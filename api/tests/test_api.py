from fastapi.testclient import TestClient

from mixa.server import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_analyze_returns_the_contract_shape():
    res = client.post("/analyze", json={"text": "yaar I am coming kal"})
    assert res.status_code == 200
    body = res.json()
    assert {"tokens", "stats", "meaning", "lid_source"} <= body.keys()
    assert body["tokens"][0] == {
        "text": "yaar",
        "start": 0,
        "end": 4,
        "lang": "hi-ur",
        "conf": body["tokens"][0]["conf"],
        "key": "yr",
        "scripts": {},
    }


def test_analyze_rejects_empty_and_overlong_text():
    assert client.post("/analyze", json={"text": ""}).status_code == 422
    assert client.post("/analyze", json={"text": "a" * 501}).status_code == 422


def test_providers_always_offers_auto():
    body = client.get("/providers").json()
    assert body["default"] == "auto"
    assert body["options"][0]["id"] == "auto"


def test_analyze_rejects_providers_that_are_not_configured():
    res = client.post("/analyze", json={"text": "yaar", "provider": "gpt-9-ultra"})
    assert res.status_code == 422
