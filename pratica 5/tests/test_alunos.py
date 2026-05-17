import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def resetar_alunos():
    client.delete("/api/v1/alunos/")
    yield
    client.delete("/api/v1/alunos/")


def criar_aluno(nome: str, email: str, curso: str):
    return client.post(
        "/api/v1/alunos/",
        json={
            "nome": nome,
            "email": email,
            "curso": curso,
        },
    )


def test_adiciona_tres_alunos_por_curso_e_lista_todos():
    alunos = [
        ("Ana Silva", "ana@email.com", "GES"),
        ("Bruno Lima", "bruno@email.com", "GES"),
        ("Caio Rocha", "caio@email.com", "GES"),
        ("Duda Alves", "duda@email.com", "GEC"),
        ("Edu Costa", "edu@email.com", "GEC"),
        ("Fabi Dias", "fabi@email.com", "GEC"),
    ]

    for nome, email, curso in alunos:
        response = criar_aluno(nome, email, curso)
        assert response.status_code == 200

    response = client.get("/api/v1/alunos/")

    assert response.status_code == 200
    assert len(response.json()) == 6
    assert [aluno["id"] for aluno in response.json()] == [
        "GES1",
        "GES2",
        "GES3",
        "GEC1",
        "GEC2",
        "GEC3",
    ]


def test_buscar_aluno_por_id():
    criar_aluno("Ana Silva", "ana@email.com", "GES")

    response = client.get("/api/v1/alunos/GES1")

    assert response.status_code == 200
    assert response.json()["id"] == "GES1"
    assert response.json()["nome"] == "Ana Silva"
    assert response.json()["email"] == "ana@email.com"


def test_atualizar_dados_do_aluno():
    create = criar_aluno("Ana Silva", "ana@email.com", "GES")
    aluno_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/alunos/{aluno_id}",
        json={
            "nome": "Ana Oliveira",
            "email": "ana.oliveira@email.com",
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == "GES1"
    assert response.json()["nome"] == "Ana Oliveira"
    assert response.json()["email"] == "ana.oliveira@email.com"

    busca = client.get("/api/v1/alunos/GES1")
    assert busca.json()["nome"] == "Ana Oliveira"


def test_atualizar_curso_gera_novo_id_persistido():
    criar_aluno("Aluno GEC", "gec@email.com", "GEC")
    create = criar_aluno("Ana Silva", "ana@email.com", "GES")

    response = client.patch(f"/api/v1/alunos/{create.json()['id']}", json={"curso": "GEC"})

    assert response.status_code == 200
    assert response.json()["curso"] == "GEC"
    assert response.json()["matricula"] == 2
    assert response.json()["id"] == "GEC2"

    antigo = client.get("/api/v1/alunos/GES1")
    novo = client.get("/api/v1/alunos/GEC2")
    assert antigo.status_code == 404
    assert novo.status_code == 200


def test_deletar_aluno_e_nao_reutilizar_id():
    create = criar_aluno("Ana Silva", "ana@email.com", "GES")
    aluno_id = create.json()["id"]

    delete_response = client.delete(f"/api/v1/alunos/{aluno_id}")
    assert delete_response.status_code == 200

    busca = client.get(f"/api/v1/alunos/{aluno_id}")
    assert busca.status_code == 404

    novo = criar_aluno("Bruno Lima", "bruno@email.com", "GES")
    assert novo.status_code == 200
    assert novo.json()["id"] == "GES2"


def test_dados_persistem_entre_requisicoes_e_clients():
    create = criar_aluno("Persistente", "persistente@email.com", "GEC")
    aluno_id = create.json()["id"]

    outro_client = TestClient(app)
    response = outro_client.get(f"/api/v1/alunos/{aluno_id}")

    assert response.status_code == 200
    assert response.json()["nome"] == "Persistente"
    assert response.json()["curso"] == "GEC"


def test_resetar_lista_de_alunos():
    criar_aluno("Ana Silva", "ana@email.com", "GES")
    criar_aluno("Carla Souza", "carla@email.com", "GEC")

    response = client.delete("/api/v1/alunos/")
    lista = client.get("/api/v1/alunos/")
    novo = criar_aluno("Nova Ana", "nova@email.com", "GES")

    assert response.status_code == 200
    assert lista.status_code == 200
    assert lista.json() == []
    assert novo.json()["id"] == "GES1"