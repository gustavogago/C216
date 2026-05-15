import time

from fastapi import Request


async def log_requests(request: Request, call_next):
    inicio = time.time()

    print(f"REQUEST {request.method} {request.url}")

    response = await call_next(request)

    duracao = time.time() - inicio
    print(f"RESPONSE {response.status_code} - {duracao:.4f}s")

    return response
