from fastapi import FastAPI

from app.routes.aluno_routes import router as aluno_router
from app.middlewares.logging import log_requests
from app.middlewares.custom_header import add_custom_header

app = FastAPI(
    title="Gerenciador de Alunos API",
    description="API CRUD de alunos com FastAPI",
    version="1.0.0",
)

# ==============================
# Registro dos Middlewares
# ==============================
app.middleware("http")(log_requests)
app.middleware("http")(add_custom_header)

# ==============================
# Rotas
# ==============================
app.include_router(aluno_router)

# ==============================
# Health Check
# ==============================
@app.get("/")
def root():
    return {"mensagem": "API de alunos funcionando"}
