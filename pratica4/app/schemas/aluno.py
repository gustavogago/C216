from typing import Literal

from pydantic import BaseModel

Curso = Literal["GES", "GEC"]


class AlunoBase(BaseModel):
    nome: str
    email: str
    curso: Curso


class AlunoCreate(AlunoBase):
    pass


class AlunoUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    curso: Curso | None = None


class Aluno(AlunoBase):
    matricula: int
    id: str
