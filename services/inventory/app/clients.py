import os
import requests
from tenacity import retry, stop_after_attempt, wait_fixed

PRODUCTS_BASE_URL = os.getenv("PRODUCTS_BASE_URL", "http://products:8000")
PRODUCTS_API_KEY = os.getenv("PRODUCTS_API_KEY", "prod-secret-key")
HTTP_TIMEOUT_SECONDS = int(os.getenv("HTTP_TIMEOUT_SECONDS", "3"))
HTTP_MAX_RETRIES = int(os.getenv("HTTP_MAX_RETRIES", "2"))

headers = {
    "x-api-key": PRODUCTS_API_KEY,
    "Accept": "application/json",
}

@retry(stop=stop_after_attempt(HTTP_MAX_RETRIES), wait=wait_fixed(1))
def fetch_product_or_404(product_id: int) -> dict:
    url = f"{PRODUCTS_BASE_URL}/internal/products/{product_id}"
    resp = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT_SECONDS)
    if resp.status_code == 404:

        return {"not_found": True}
    resp.raise_for_status()
    return resp.json()
