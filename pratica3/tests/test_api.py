import pathlib
import sys

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from app import app, get_pokemon_service, reset_state


POKEMON_FIXTURES = {
    "pikachu": {
        "id": 25,
        "name": "pikachu",
        "height": 4,
        "weight": 60,
        "base_experience": 112,
        "attack": 55,
        "types": ["electric"],
        "abilities": ["static", "lightning-rod"],
    },
    "charizard": {
        "id": 6,
        "name": "charizard",
        "height": 17,
        "weight": 905,
        "base_experience": 267,
        "attack": 84,
        "types": ["fire", "flying"],
        "abilities": ["blaze", "solar-power"],
    },
    "bulbasaur": {
        "id": 1,
        "name": "bulbasaur",
        "height": 7,
        "weight": 69,
        "base_experience": 64,
        "attack": 49,
        "types": ["grass", "poison"],
        "abilities": ["overgrow", "chlorophyll"],
    },
    "squirtle": {
        "id": 7,
        "name": "squirtle",
        "height": 5,
        "weight": 90,
        "base_experience": 63,
        "attack": 48,
        "types": ["water"],
        "abilities": ["torrent", "rain-dish"],
    },
}


class FakePokemonService:
    async def list_pokemon(self, limit: int, offset: int):
        names = list(POKEMON_FIXTURES.keys())
        sliced_names = names[offset : offset + limit]
        return {
            "count": len(names),
            "results": [
                {
                    "name": name,
                    "url": f"https://pokeapi.co/api/v2/pokemon/{name}/",
                }
                for name in sliced_names
            ],
        }

    async def get_pokemon_summary(self, pokemon_name: str):
        key = pokemon_name.strip().lower()
        if key not in POKEMON_FIXTURES:
            raise HTTPException(status_code=404, detail="Pokemon nao encontrado na PokeAPI.")
        return POKEMON_FIXTURES[key]


def assert_with_log(response, expected_status: int):
    path_url = str(response.request.url).replace("http://testserver", "")
    print(f"[TEST LOG] {response.request.method} {path_url} -> {response.status_code}")
    assert response.status_code == expected_status, response.text


@pytest.fixture(autouse=True)
def setup_and_teardown():
    reset_state()
    app.dependency_overrides[get_pokemon_service] = lambda: FakePokemonService()
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def create_capture(client: TestClient) -> int:
    response = client.post(
        "/captures",
        json={"pokemon_name": "pikachu", "trainer": "ash", "nickname": "raio"},
    )
    assert_with_log(response, 201)
    return response.json()["id"]


def create_team(client: TestClient):
    response = client.put(
        "/teams/ash",
        json={"pokemon_names": ["pikachu", "bulbasaur"]},
    )
    assert_with_log(response, 200)
    return response.json()


def test_get_pokemon_list(client: TestClient):
    response = client.get("/pokemon?limit=2&offset=0")
    assert_with_log(response, 200)
    payload = response.json()
    assert payload["count"] == 4
    assert len(payload["results"]) == 2


def test_get_pokemon_details(client: TestClient):
    response = client.get("/pokemon/pikachu")
    assert_with_log(response, 200)
    payload = response.json()
    assert payload["name"] == "pikachu"
    assert payload["attack"] == 55


def test_post_capture(client: TestClient):
    response = client.post(
        "/captures",
        json={"pokemon_name": "charizard", "trainer": "red", "nickname": "flame"},
    )
    assert_with_log(response, 201)
    payload = response.json()
    assert payload["id"] == 1
    assert payload["pokemon"]["name"] == "charizard"


def test_post_battle_compare(client: TestClient):
    response = client.post(
        "/battles/compare",
        json={"pokemon_a": "charizard", "pokemon_b": "bulbasaur"},
    )
    assert_with_log(response, 200)
    payload = response.json()
    assert payload["winner"] == "charizard"


def test_put_capture(client: TestClient):
    capture_id = create_capture(client)
    response = client.put(
        f"/captures/{capture_id}",
        json={"pokemon_name": "charizard", "trainer": "ash", "nickname": "fogo"},
    )
    assert_with_log(response, 200)
    payload = response.json()
    assert payload["id"] == capture_id
    assert payload["pokemon"]["name"] == "charizard"


def test_put_team(client: TestClient):
    response = client.put("/teams/misty", json={"pokemon_names": ["squirtle", "pikachu"]})
    assert_with_log(response, 200)
    payload = response.json()
    assert payload["trainer"] == "misty"
    assert len(payload["pokemons"]) == 2


def test_delete_capture(client: TestClient):
    capture_id = create_capture(client)
    response = client.delete(f"/captures/{capture_id}")
    assert_with_log(response, 200)
    payload = response.json()
    assert payload["removed_capture"]["id"] == capture_id


def test_delete_team(client: TestClient):
    create_team(client)
    response = client.delete("/teams/ash")
    assert_with_log(response, 200)
    payload = response.json()
    assert payload["removed_team"]["trainer"] == "ash"


def test_patch_capture(client: TestClient):
    capture_id = create_capture(client)
    response = client.patch(f"/captures/{capture_id}", json={"nickname": "trovao"})
    assert_with_log(response, 200)
    payload = response.json()
    assert payload["nickname"] == "trovao"


def test_patch_team(client: TestClient):
    create_team(client)
    response = client.patch(
        "/teams/ash",
        json={"remove_pokemon": ["bulbasaur"], "add_pokemon": ["charizard"]},
    )
    assert_with_log(response, 200)
    payload = response.json()
    pokemon_names = [pokemon["name"] for pokemon in payload["pokemons"]]
    assert pokemon_names == ["pikachu", "charizard"]
