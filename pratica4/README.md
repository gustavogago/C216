# Pratica 4 - Gerenciador de Alunos

API CRUD feita com FastAPI usando a base da pratica 4 para gerenciar alunos.

## Requisitos atendidos

- CRUD completo de alunos.
- Rotas versionadas em `/api/v1/alunos/`.
- Atributos de aluno: `nome`, `email`, `curso`, `matricula` e `id`.
- Cursos aceitos: `GES` e `GEC`.
- Matricula gerada automaticamente por curso.
- ID gerado como curso + matricula, por exemplo `GES1`, `GES2`, `GEC1`.
- IDs de alunos deletados nao sao reutilizados.
- Reset da lista de alunos.
- Testes automatizados com TestClient.
- Execucao preparada via Docker e docker-compose.

## Estrutura

```text
app/
  main.py
  middlewares/
    custom_header.py
    logging.py
  routes/
    aluno_routes.py
  schemas/
    aluno.py
  services/
    aluno_service.py
tests/
  test_alunos.py
Dockerfile
docker-compose.yml
requirements.txt
pytest.ini
```

## Rotas

```text
POST   /api/v1/alunos/             cria um aluno
GET    /api/v1/alunos/             lista todos os alunos
GET    /api/v1/alunos/{aluno_id}   busca um aluno por ID
PATCH  /api/v1/alunos/{aluno_id}   atualiza dados de um aluno
DELETE /api/v1/alunos/{aluno_id}   remove um aluno
DELETE /api/v1/alunos/             reseta a lista de alunos
```

## Exemplo de aluno

Entrada:

```json
{
  "nome": "Ana Silva",
  "email": "ana@email.com",
  "curso": "GES"
}
```

Resposta:

```json
{
  "nome": "Ana Silva",
  "email": "ana@email.com",
  "curso": "GES",
  "matricula": 1,
  "id": "GES1"
}
```

## Executar com Docker Compose

```bash
docker compose up --build
```

Executar apenas os testes:

```bash
docker compose run --rm tests
```

## Executar localmente

```bash
uvicorn app.main:app --reload
```

## Testes

```bash
pytest -v
```

Os testes cobrem:

- criacao de alunos com matricula e ID por curso;
- adicao de 3 alunos por curso;
- listagem;
- busca por ID;
- atualizacao de dados;
- mudanca de curso com novo ID;
- remocao sem reutilizar ID;
- reset da lista.
