from fastapi import APIRouter, HTTPException

from app.schemas.aluno import Aluno, AlunoCreate, AlunoUpdate
from app.services.aluno_service import AlunoService


router = APIRouter(prefix="/api/v1/alunos", tags=["alunos"])
service = AlunoService()


@router.get("/", response_model=list[Aluno])
def listar_alunos():
    return service.listar()


@router.post("/", response_model=Aluno)
def criar_aluno(aluno: AlunoCreate):
    return service.criar(aluno)


@router.get("/{aluno_id}", response_model=Aluno)
def buscar_aluno(aluno_id: str):
    aluno = service.buscar_por_id(aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno nao encontrado")
    return aluno


@router.patch("/{aluno_id}", response_model=Aluno)
def atualizar_aluno(aluno_id: str, aluno: AlunoUpdate):
    atualizado = service.atualizar(aluno_id, aluno)
    if not atualizado:
        raise HTTPException(status_code=404, detail="Aluno nao encontrado")
    return atualizado


@router.delete("/{aluno_id}")
def deletar_aluno(aluno_id: str):
    sucesso = service.deletar(aluno_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Aluno nao encontrado")
    return {"mensagem": "Aluno deletado com sucesso"}


@router.delete("/")
def resetar_alunos():
    service.resetar()
    return {"mensagem": "Lista de alunos resetada com sucesso"}
