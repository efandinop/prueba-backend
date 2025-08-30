from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
from models import Base, engine

client = TestClient(app)
API_KEY = {"x-api-key": "inv-secret-key"}

def setup_module(module):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@patch("clients.fetch_product_or_404", return_value={"data": {"id": 1}})
def test_set_inventory(mock_fetch):
    r = client.post("/inventory", headers=API_KEY,
                    json={"data":{"id":1,"type":"inventories","attributes":{"cantidad":10}}})
    assert r.status_code == 200
    assert r.json()["data"]["attributes"]["cantidad"] == 10

@patch("clients.fetch_product_or_404", return_value={"data": {"id": 1}})
def test_purchase_ok(mock_fetch):
    client.post("/inventory", headers=API_KEY,
                json={"data":{"id":1,"type":"inventories","attributes":{"cantidad":5}}})
    r = client.patch("/inventory/1/purchase", headers=API_KEY,
                     json={"data":{"id":1,"type":"inventories","attributes":{"cantidad":3}}})
    assert r.status_code == 200
    assert r.json()["data"]["attributes"]["cantidad"] == 2

@patch("clients.fetch_product_or_404", return_value={"not_found": True})
def test_product_not_found(mock_fetch):
    r = client.get("/inventory/999")
    assert r.status_code == 404
