import httpx
import time

client = httpx.AsyncClient(timeout=15.0)