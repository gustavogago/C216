# app/middlewares/logging.py
from fastapi import Request
import time

async def log_requests(request: Request, call_next):
    inicio = time.time()

    print(f"➡️ {request.method} {request.url}")

    response = await call_next(request)

    duracao = time.time() - inicio
    print(f"⬅️ {response.status_code} - {duracao:.4f}s")

    return response