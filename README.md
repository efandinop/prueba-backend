# Prueba Técnica Backend – Productos & Inventario

Dos microservicios **Products** y **Inventory** (FastAPI + SQLite) que se comunican por HTTP usando **JSON:API**. Contenerizados con **Docker** y orquestados con **Docker Compose**.

---

## 🚀 Quick start
Requisitos: Docker Desktop (WSL2 en Windows).

```bash
docker compose up --build
# Products:  http://localhost:8000/docs
# Inventory: http://localhost:8001/docs
```

---

## 🔐 Configuración (.env)
Variables de entorno que puedes configurar en un archivo `.env` en la raíz:

```
PRODUCTS_API_KEY=prod-secret-key
INVENTORY_API_KEY=inv-secret-key
PRODUCTS_BASE_URL=http://products:8000
INVENTORY_BASE_URL=http://inventory:8001
HTTP_TIMEOUT_SECONDS=3
HTTP_MAX_RETRIES=2
```

---

## 🧩 Servicios y endpoints

### Products (http://localhost:8000)
- **CRUD JSON:API**
  - `POST /products`
  - `GET /products?limit=&offset=`
  - `GET /products/{id}`
  - `PATCH /products/{id}`
  - `DELETE /products/{id}`
- **Interno protegido**:  
  `GET /internal/products/{id}` (requiere header `x-api-key: prod-secret-key`).

### Inventory (http://localhost:8001)
- `POST /inventory` → setear stock (**requiere `x-api-key: inv-secret-key`**).  
- `GET /inventory/{product_id}` → consultar stock.  
- `PATCH /inventory/{product_id}/purchase` → descontar stock (**requiere `x-api-key`**).  
- Emite **eventos en consola** al cambiar inventario.  
- Valida existencia de producto llamando a **Products** con timeout + reintentos.

---

## 🧪 Tests

Correr tests unitarios e integración:

```bash
# Products
docker compose run --rm products pytest -q tests

# Inventory
docker compose run --rm inventory pytest -q tests
```

---

## 🛠️ Decisiones técnicas
- **FastAPI** → rapidez de desarrollo y documentación automática (`/docs`).
- **SQLite** → cero fricción, portable para la prueba técnica.
- **JSON:API-like** → respuestas `data {id, type, attributes}` y errores `errors[]`.
- **API Key** → endpoints internos y de escritura protegidos con header `x-api-key`.
- **Timeout & retries** → Inventory reintenta si Products no responde.

---

## 🗺️ Diagrama

```
+-----------+      HTTP (JSON:API)      +------------+
| Products  | <------------------------> | Inventory  |
| CRUD      |  /internal/products/{id}   | Stock      |
+-----------+      x-api-key             +------------+
     ^                                        |
     |                                        | Console Events
   SQLite                                   SQLite
```

---

## 📦 Estructura del proyecto

```
services/
  products/
    Dockerfile
    app/
      main.py
      models.py
      schemas.py
      requirements.txt
      tests/
        test_products_unit.py
        test_products_integration.py
        conftest.py
  inventory/
    Dockerfile
    app/
      main.py
      models.py
      schemas.py
      clients.py
      requirements.txt
      tests/
        test_inventory_unit.py
        test_inventory_integration.py
        conftest.py
docker-compose.yml
.env
```

---

## 📂 .gitignore (raíz)

```
__pycache__/
*.pyc
*.pyo
*.db
.env
.vscode/
.idea/
.DS_Store
```

---

## ⚙️ CI/CD con GitHub Actions (opcional)

Archivo: `.github/workflows/ci.yml`

```yaml
name: CI
on:
  push:
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [products, inventory]
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Build ${{ matrix.service }}
        run: docker build -t demo/${{ matrix.service }} ./services/${{ matrix.service }}
      - name: Run tests ${{ matrix.service }}
        run: docker run --rm demo/${{ matrix.service }} pytest -q tests
```

---

## 📦 Postman Collection (opcional)

Archivo: `postman_collection.json`

```json
{
  "info": { "name": "Prueba Backend - Products & Inventory", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json" },
  "item": [
    {
      "name": "Products - Create",
      "request": {
        "method": "POST",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "url": { "raw": "http://localhost:8000/products", "host": ["http://localhost:8000"], "path": ["products"] },
        "body": { "mode": "raw", "raw": "{\"data\":{\"type\":\"products\",\"attributes\":{\"nombre\":\"Laptop\",\"precio\":1200.5}}}" }
      }
    },
    {
      "name": "Inventory - Set stock",
      "request": {
        "method": "POST",
        "header": [
          { "key": "Content-Type", "value": "application/json" },
          { "key": "x-api-key", "value": "inv-secret-key" }
        ],
        "url": { "raw": "http://localhost:8001/inventory", "host": ["http://localhost:8001"], "path": ["inventory"] },
        "body": { "mode": "raw", "raw": "{\"data\":{\"id\":1,\"type\":\"inventories\",\"attributes\":{\"cantidad\":10}}}" }
      }
    }
  ]
}
```

---

## ✅ Checklist de entrega
- [x] `docker compose up --build` levanta ambos servicios.  
- [x] `/docs` accesibles y explican endpoints.  
- [x] Products CRUD OK.  
- [x] Inventory valida producto, setea/lee/descuenta y loguea evento.  
- [x] Auth por `x-api-key` en endpoints sensibles.  
- [x] Timeouts y reintentos (Inventory→Products) activos.  
- [x] Tests de ambos servicios **pasan**.  
- [x] README claro 
