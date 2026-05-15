from fastapi.testclient import TestClient
from open_image_to_cad.api.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

def test_text_endpoint():
    res = client.post("/text", json={
        "prompt": "make a plate",
        "adapter": "mock"
    })
    assert res.status_code == 200
    data = res.json()
    assert "run_id" in data
    assert data["status"] == "success"
