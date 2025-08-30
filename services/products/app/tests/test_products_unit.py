from fastapi.testclient import TestClient
from main import app
from models import SessionLocal, Product, Base, engine

client = TestClient(app)

def setup_module(module):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_create_product():
    payload = {
        "data": {"type": "products", "attributes": {"nombre": "Mouse", "precio": 25.5}}
    }
    r = client.post("/products", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["data"]["attributes"]["nombre"] == "Mouse"
    assert body["data"]["attributes"]["precio"] == 25.5

def test_update_product():
    p = {"data": {"type": "products", "attributes": {"nombre": "KB", "precio": 10}}}
    rid = client.post("/products", json=p).json()["data"]["id"]
    newp = {"data": {"type": "products", "attributes": {"nombre": "KB Pro", "precio": 20}}}
    r = client.patch(f"/products/{rid}", json=newp)
    assert r.status_code == 200
    assert r.json()["data"]["attributes"]["nombre"] == "KB Pro"
