from typing import List

from app.schemas.aluno import Aluno, AlunoCreate, AlunoUpdate, Curso


class AlunoService:
    def __init__(self):
        self._alunos: list[Aluno] = []
        self._matriculas_por_curso: dict[str, int] = {
            "GES": 0,
            "GEC": 0,
        }

    def listar(self) -> List[Aluno]:
        return self._alunos

    def buscar_por_id(self, aluno_id: str) -> Aluno | None:
        for aluno in self._alunos:
            if aluno.id == aluno_id:
                return aluno
        return None

    def criar(self, aluno_data: AlunoCreate) -> Aluno:
        matricula = self._gerar_matricula(aluno_data.curso)
        novo_aluno = Aluno(
            id=self._gerar_id(aluno_data.curso, matricula),
            matricula=matricula,
            nome=aluno_data.nome,
            email=aluno_data.email,
            curso=aluno_data.curso,
        )
        self._alunos.append(novo_aluno)
        return novo_aluno

    def atualizar(self, aluno_id: str, aluno_data: AlunoUpdate) -> Aluno | None:
        aluno = self.buscar_por_id(aluno_id)
        if not aluno:
            return None

        if hasattr(aluno_data, "model_dump"):
            dados = aluno_data.model_dump(exclude_unset=True)
        else:
            dados = aluno_data.dict(exclude_unset=True)

        novo_curso = dados.get("curso")
        if novo_curso and novo_curso != aluno.curso:
            matricula = self._gerar_matricula(novo_curso)
            aluno.curso = novo_curso
            aluno.matricula = matricula
            aluno.id = self._gerar_id(novo_curso, matricula)

        if "nome" in dados:
            aluno.nome = dados["nome"]

        if "email" in dados:
            aluno.email = dados["email"]

        return aluno

    def deletar(self, aluno_id: str) -> bool:
        aluno = self.buscar_por_id(aluno_id)
        if aluno:
            self._alunos.remove(aluno)
            return True
        return False

    def resetar(self) -> None:
        self._alunos.clear()
        self._matriculas_por_curso = {
            "GES": 0,
            "GEC": 0,
        }

    def _gerar_matricula(self, curso: Curso) -> int:
        self._matriculas_por_curso[curso] += 1
        return self._matriculas_por_curso[curso]

    @staticmethod
    def _gerar_id(curso: Curso, matricula: int) -> str:
        return f"{curso}{matricula}"
