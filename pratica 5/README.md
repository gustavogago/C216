# Pratica 5 - API de Alunos com PostgreSQL

Esta pratica adapta a API de alunos da `pratica4` para usar persistencia real com PostgreSQL, mantendo a organizacao em camadas com FastAPI.

## Requisitos atendidos

- API de alunos usando PostgreSQL via `asyncpg`.
- Testes automatizados de API com `TestClient`.
- Testes com adicao de 3 alunos por curso, listagem, busca por ID, atualizacao, remocao e persistencia.
- Evidencias dos testes na pasta `img/`.

## Estrutura principal

```text
app/
  db/
    connection.py
    init.sql
  routes/
    aluno_routes.py
  schemas/
    aluno.py
  services/
    aluno_service.py
  main.py
tests/
  test_alunos.py
img/
```

## Endpoints

```text
GET    /api/v1/alunos/
POST   /api/v1/alunos/
GET    /api/v1/alunos/{aluno_id}
PATCH  /api/v1/alunos/{aluno_id}
DELETE /api/v1/alunos/{aluno_id}
DELETE /api/v1/alunos/
```

## Regras de matricula e ID

- Cursos aceitos: `GES` e `GEC`.
- Cada curso possui sua propria sequencia de matriculas.
- O ID e formado por curso + matricula, como `GES1` ou `GEC3`.
- IDs nao sao reutilizados apos remocao.
- Ao trocar o curso de um aluno, uma nova matricula e um novo ID sao gerados para o novo curso.

## Executar com Docker Compose

```bash
docker compose up --build
```

A API fica disponivel em:

```text
http://localhost:8000
```

## Rodar os testes

```bash
docker compose run --rm tests
```

Para reiniciar o banco do zero:

```bash
docker compose down -v
```

## Banco de dados

O PostgreSQL roda no compose com o banco `alunos_db`. A aplicacao usa a variavel `DATABASE_URL`:

```text
postgresql://postgres:postgres@db:5432/alunos_db
```

Fora do Docker, o fallback aponta para:

```text
postgresql://postgres:postgres@localhost:5433/alunos_db
```