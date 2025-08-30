from pydantic import BaseModel

# JSON:API data object
class ProductAttributes(BaseModel):
    nombre: str
    precio: float

class ProductData(BaseModel):
    id: int | None = None
    type: str = "products"
    attributes: ProductAttributes

    class Config:
        orm_mode = True

class ProductResponse(BaseModel):
    data: ProductData
