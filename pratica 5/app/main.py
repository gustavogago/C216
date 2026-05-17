from fastapi import FastAPI

from app.middlewares.custom_header import add_custom_header
from app.middlewares.logging import log_requests
from app.routes.aluno_routes import router as aluno_router

app = FastAPI(
    title="Gerenciador de Alunos API",
    description="API CRUD de alunos com persistencia em PostgreSQL",
    version="1.0.0",
)

app.middleware("http")(log_requests)
app.middleware("http")(add_custom_header)

app.include_router(aluno_router)


@app.get("/")
def root():
    return {"mensagem": "API de alunos com PostgreSQL funcionando"}