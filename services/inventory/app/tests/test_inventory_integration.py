from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
from models import Base, engine

client = TestClient(app)
API_KEY = {"x-api-key": "inv-secret-key"}

def setup_module(module):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@patch("clients.fetch_product_or_404", return_value={"data": {"id": 2}})
def test_full_flow(mock_fetch):
    r = client.post("/inventory", headers=API_KEY,
                    json={"data":{"id":2,"type":"inventories","attributes":{"cantidad":8}}})
    assert r.status_code == 200

    r2 = client.get("/inventory/2")
    assert r2.status_code == 200
    assert r2.json()["data"]["attributes"]["cantidad"] == 8
