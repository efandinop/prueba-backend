from fastapi.testclient import TestClient
from main import app
from models import Base, engine

client = TestClient(app)

def setup_module(module):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_list_and_get_flow():
    # crea
    client.post("/products", json={"data":{"type":"products","attributes":{"nombre":"Lap","precio":1200}}})
    client.post("/products", json={"data":{"type":"products","attributes":{"nombre":"Cel","precio":800}}})

    # lista
    r = client.get("/products?limit=10&offset=0")
    assert r.status_code == 200
    assert len(r.json()["data"]) >= 2

    # get
    first_id = r.json()["data"][0]["id"]
    r2 = client.get(f"/products/{first_id}")
    assert r2.status_code == 200
    assert "attributes" in r2.json()["data"]
