from typing import Any

from app.db.connection import get_connection
from app.schemas.aluno import AlunoCreate, AlunoUpdate, Curso


class AlunoService:
    async def listar(self):
        conn = await get_connection()
        try:
            rows = await conn.fetch(
                """
                SELECT id, matricula, nome, email, curso
                FROM alunos
                ORDER BY curso DESC, matricula
                """
            )
            return [dict(row) for row in rows]
        finally:
            await conn.close()

    async def buscar_por_id(self, aluno_id: str):
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                SELECT id, matricula, nome, email, curso
                FROM alunos
                WHERE id=$1
                """,
                aluno_id,
            )
            return dict(row) if row else None
        finally:
            await conn.close()

    async def criar(self, aluno_data: AlunoCreate):
        conn = await get_connection()
        try:
            async with conn.transaction():
                matricula = await self._gerar_matricula(conn, aluno_data.curso)
                aluno_id = self._gerar_id(aluno_data.curso, matricula)
                row = await conn.fetchrow(
                    """
                    INSERT INTO alunos (id, matricula, nome, email, curso)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id, matricula, nome, email, curso
                    """,
                    aluno_id,
                    matricula,
                    aluno_data.nome,
                    aluno_data.email,
                    aluno_data.curso,
                )
                return dict(row)
        finally:
            await conn.close()

    async def atualizar(self, aluno_id: str, aluno_data: AlunoUpdate):
        conn = await get_connection()
        try:
            async with conn.transaction():
                atual = await conn.fetchrow(
                    """
                    SELECT id, matricula, nome, email, curso
                    FROM alunos
                    WHERE id=$1
                    """,
                    aluno_id,
                )
                if not atual:
                    return None

                dados = self._dados_atualizacao(aluno_data)
                curso = dados.get("curso", atual["curso"])
                nome = dados.get("nome", atual["nome"])
                email = dados.get("email", atual["email"])

                if curso != atual["curso"]:
                    matricula = await self._gerar_matricula(conn, curso)
                    novo_id = self._gerar_id(curso, matricula)
                else:
                    matricula = atual["matricula"]
                    novo_id = atual["id"]

                row = await conn.fetchrow(
                    """
                    UPDATE alunos
                    SET id=$1, matricula=$2, nome=$3, email=$4, curso=$5
                    WHERE id=$6
                    RETURNING id, matricula, nome, email, curso
                    """,
                    novo_id,
                    matricula,
                    nome,
                    email,
                    curso,
                    aluno_id,
                )
                return dict(row)
        finally:
            await conn.close()

    async def deletar(self, aluno_id: str) -> bool:
        conn = await get_connection()
        try:
            result = await conn.execute("DELETE FROM alunos WHERE id=$1", aluno_id)
            return result == "DELETE 1"
        finally:
            await conn.close()

    async def resetar(self) -> None:
        conn = await get_connection()
        try:
            async with conn.transaction():
                await conn.execute("TRUNCATE TABLE alunos")
                await conn.execute(
                    """
                    UPDATE matricula_counters
                    SET proxima_matricula=1
                    WHERE curso IN ('GES', 'GEC')
                    """
                )
        finally:
            await conn.close()

    @staticmethod
    def _dados_atualizacao(aluno_data: AlunoUpdate) -> dict[str, Any]:
        if hasattr(aluno_data, "model_dump"):
            return aluno_data.model_dump(exclude_unset=True)
        return aluno_data.dict(exclude_unset=True)

    @staticmethod
    async def _gerar_matricula(conn, curso: Curso) -> int:
        row = await conn.fetchrow(
            """
            UPDATE matricula_counters
            SET proxima_matricula = proxima_matricula + 1
            WHERE curso=$1
            RETURNING proxima_matricula - 1 AS matricula
            """,
            curso,
        )
        if not row:
            raise ValueError(f"Curso invalido: {curso}")
        return int(row["matricula"])

    @staticmethod
    def _gerar_id(curso: Curso, matricula: int) -> str:
        return f"{curso}{matricula}"