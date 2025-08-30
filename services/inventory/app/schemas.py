from pydantic import BaseModel

class InventoryAttributes(BaseModel):
    cantidad: int

class InventoryData(BaseModel):
    id: int | None = None  # usaremos product_id como id
    type: str = "inventories"
    attributes: InventoryAttributes

class InventoryResponse(BaseModel):
    data: InventoryData
