import os
from fastapi import FastAPI, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models import SessionLocal, init_db, Inventory
from schemas import InventoryResponse
import clients  

app = FastAPI(title="Inventory Service", version="1.0.0")
init_db()

INVENTORY_API_KEY = os.getenv("INVENTORY_API_KEY", "inv-secret-key")

# -------- Helper JSON:API errors --------
def jsonapi_error(status_code: int, detail: str):
    return JSONResponse(
        status_code=status_code,
        content={"errors": [{"status": str(status_code), "detail": detail}]},
        media_type="application/vnd.api+json",
    )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def event(msg: str):
    print(f"[EVENT] {msg}")

def require_inventory_api_key(x_api_key: str | None = Header(default=None)):
    if x_api_key != INVENTORY_API_KEY:
        return jsonapi_error(401, "Invalid API key")

@app.get("/health")
def health():
    return {"status": "ok"}

def ensure_product_exists(product_id: int):
    res = clients.fetch_product_or_404(product_id)
    if res.get("not_found"):
        return jsonapi_error(404, "Product not found in products service")
    return None

# ---------------- Endpoints JSON:API ----------------

@app.post(
    "/inventory",
    response_model=InventoryResponse,
    tags=["inventory"],
    dependencies=[Depends(require_inventory_api_key)],
)
def set_inventory(payload: InventoryResponse, db: Session = Depends(get_db)):
    product_id = payload.data.id
    if product_id is None:
        return jsonapi_error(400, "data.id (product_id) is required")

    err = ensure_product_exists(product_id)
    if err:
        return err

    qty = payload.data.attributes.cantidad
    inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inv:
        inv = Inventory(product_id=product_id, cantidad=qty)
        db.add(inv)
    else:
        inv.cantidad = qty
    db.commit()

    event(f"Inventory set for product {product_id}: cantidad={qty}")
    return {"data": {"id": product_id, "type": "inventories", "attributes": {"cantidad": inv.cantidad}}}

@app.get("/inventory/{product_id}", response_model=InventoryResponse, tags=["inventory"])
def get_inventory(product_id: int, db: Session = Depends(get_db)):
    err = ensure_product_exists(product_id)
    if err:
        return err

    inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    current = inv.cantidad if inv else 0
    return {"data": {"id": product_id, "type": "inventories", "attributes": {"cantidad": current}}}

@app.patch(
    "/inventory/{product_id}/purchase",
    response_model=InventoryResponse,
    tags=["inventory"],
    dependencies=[Depends(require_inventory_api_key)],
)
def purchase(product_id: int, payload: InventoryResponse, db: Session = Depends(get_db)):
    err = ensure_product_exists(product_id)
    if err:
        return err

    to_subtract = payload.data.attributes.cantidad
    if to_subtract <= 0:
        return jsonapi_error(400, "cantidad must be > 0")

    inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inv:
        inv = Inventory(product_id=product_id, cantidad=0)
        db.add(inv)
        db.commit()
        db.refresh(inv)

    if inv.cantidad < to_subtract:
        return jsonapi_error(400, "insufficient stock")

    inv.cantidad -= to_subtract
    db.commit()
    db.refresh(inv)
    event(f"Inventory changed for product {product_id}: new cantidad={inv.cantidad}")
    return {"data": {"id": product_id, "type": "inventories", "attributes": {"cantidad": inv.cantidad}}}
