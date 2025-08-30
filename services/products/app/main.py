import os
from fastapi import FastAPI, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from models import SessionLocal, init_db, Product
from schemas import ProductData, ProductResponse
from fastapi.responses import JSONResponse

app = FastAPI(title="Products Service", version="1.0.0")

init_db()

PRODUCTS_API_KEY = os.getenv("PRODUCTS_API_KEY", "prod-secret-key")

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

def require_products_api_key(x_api_key: str | None = Header(default=None)):
    if x_api_key != PRODUCTS_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.get("/health")
def health():
    return {"status": "ok"}



@app.post("/products", response_model=ProductResponse)
def create_product(payload: ProductResponse, db: Session = Depends(get_db)):
    product_attrs = payload.data.attributes
    db_product = Product(nombre=product_attrs.nombre, precio=product_attrs.precio)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return {"data": {"id": db_product.id, "type": "products", "attributes": product_attrs}}

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"data": {"id": product.id, "type": "products", "attributes": {"nombre": product.nombre, "precio": product.precio}}}

@app.get("/products")
def list_products(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    products = db.query(Product).offset(offset).limit(limit).all()
    data = [
        {"id": p.id, "type": "products", "attributes": {"nombre": p.nombre, "precio": p.precio}}
        for p in products
    ]
    return {"data": data}

@app.patch("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, payload: ProductResponse, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    attrs = payload.data.attributes
    product.nombre = attrs.nombre
    product.precio = attrs.precio
    db.commit()
    db.refresh(product)
    return {"data": {"id": product.id, "type": "products", "attributes": {"nombre": product.nombre, "precio": product.precio}}}

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"meta": {"message": "Product deleted"}}

@app.get("/internal/products/{product_id}", dependencies=[Depends(require_products_api_key)])
def internal_get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"data": {"id": product.id, "type": "products", "attributes": {"nombre": product.nombre, "precio": product.precio}}}
