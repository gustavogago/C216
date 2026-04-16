import time
from typing import Any

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from pydantic import BaseModel, Field


class PokemonService:
    BASE_URL = "https://pokeapi.co/api/v2"

    async def list_pokemon(self, limit: int, offset: int) -> dict[str, Any]:
        payload = await self._get("/pokemon", params={"limit": limit, "offset": offset})
        return {"count": payload.get("count", 0), "results": payload.get("results", [])}

    async def get_pokemon_summary(self, pokemon_name: str) -> dict[str, Any]:
        payload = await self._get(f"/pokemon/{pokemon_name}")
        return {
            "id": payload.get("id"),
            "name": payload.get("name"),
            "height": payload.get("height"),
            "weight": payload.get("weight"),
            "base_experience": payload.get("base_experience"),
            "attack": self._extract_stat(payload, "attack"),
            "types": [item["type"]["name"] for item in payload.get("types", [])],
            "abilities": [item["ability"]["name"] for item in payload.get("abilities", [])],
        }

    async def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Falha ao acessar a PokeAPI.",
            ) from exc

        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pokemon nao encontrado na PokeAPI.",
            )

        if response.status_code >= status.HTTP_400_BAD_REQUEST:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"PokeAPI retornou status {response.status_code}.",
            )

        return response.json()

    @staticmethod
    def _extract_stat(payload: dict[str, Any], stat_name: str) -> int:
        for stat in payload.get("stats", []):
            if stat.get("stat", {}).get("name") == stat_name:
                return stat.get("base_stat", 0)
        return 0


class CaptureBase(BaseModel):
    pokemon_name: str = Field(min_length=1)
    trainer: str = Field(min_length=1)
    nickname: str | None = None


class CaptureCreate(CaptureBase):
    pass


class CaptureReplace(CaptureBase):
    pass


class CapturePatch(BaseModel):
    pokemon_name: str | None = Field(default=None, min_length=1)
    trainer: str | None = Field(default=None, min_length=1)
    nickname: str | None = None


class TeamReplace(BaseModel):
    pokemon_names: list[str] = Field(min_length=1, max_length=6)


class TeamPatch(BaseModel):
    add_pokemon: list[str] | None = Field(default=None, max_length=6)
    remove_pokemon: list[str] | None = Field(default=None, max_length=6)


class BattleRequest(BaseModel):
    pokemon_a: str = Field(min_length=1)
    pokemon_b: str = Field(min_length=1)


app = FastAPI(title="Pratica 3 - PokeAPI")


def get_pokemon_service() -> PokemonService:
    return PokemonService()


def normalize_name(name: str) -> str:
    return name.strip().lower()


def reset_state() -> None:
    app.state.captures = {}
    app.state.teams = {}
    app.state.next_capture_id = 1


reset_state()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"{request.method} {request.url.path} - {process_time:.4f}s")
    return response


@app.get("/pokemon")
async def get_pokemon_list(
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    service: PokemonService = Depends(get_pokemon_service),
):
    return await service.list_pokemon(limit=limit, offset=offset)


@app.get("/pokemon/{pokemon_name}")
async def get_pokemon_details(
    pokemon_name: str,
    service: PokemonService = Depends(get_pokemon_service),
):
    return await service.get_pokemon_summary(normalize_name(pokemon_name))


@app.post("/captures", status_code=status.HTTP_201_CREATED)
async def create_capture(
    payload: CaptureCreate,
    service: PokemonService = Depends(get_pokemon_service),
):
    pokemon = await service.get_pokemon_summary(normalize_name(payload.pokemon_name))
    capture_id = app.state.next_capture_id
    app.state.next_capture_id += 1

    capture = {
        "id": capture_id,
        "trainer": payload.trainer.strip(),
        "nickname": payload.nickname,
        "pokemon": pokemon,
    }
    app.state.captures[capture_id] = capture
    return capture


@app.post("/battles/compare")
async def compare_pokemon(
    payload: BattleRequest,
    service: PokemonService = Depends(get_pokemon_service),
):
    pokemon_a = await service.get_pokemon_summary(normalize_name(payload.pokemon_a))
    pokemon_b = await service.get_pokemon_summary(normalize_name(payload.pokemon_b))

    winner = "draw"
    if pokemon_a["attack"] > pokemon_b["attack"]:
        winner = pokemon_a["name"]
    elif pokemon_b["attack"] > pokemon_a["attack"]:
        winner = pokemon_b["name"]

    return {
        "winner": winner,
        "pokemon_a": {"name": pokemon_a["name"], "attack": pokemon_a["attack"]},
        "pokemon_b": {"name": pokemon_b["name"], "attack": pokemon_b["attack"]},
    }


@app.put("/captures/{capture_id}")
async def replace_capture(
    capture_id: int,
    payload: CaptureReplace,
    service: PokemonService = Depends(get_pokemon_service),
):
    if capture_id not in app.state.captures:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Captura nao encontrada.")

    pokemon = await service.get_pokemon_summary(normalize_name(payload.pokemon_name))
    capture = {
        "id": capture_id,
        "trainer": payload.trainer.strip(),
        "nickname": payload.nickname,
        "pokemon": pokemon,
    }
    app.state.captures[capture_id] = capture
    return capture


@app.put("/teams/{trainer_name}")
async def replace_team(
    trainer_name: str,
    payload: TeamReplace,
    service: PokemonService = Depends(get_pokemon_service),
):
    normalized_names = [normalize_name(name) for name in payload.pokemon_names]
    if len(normalized_names) != len(set(normalized_names)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao envie pokemons repetidos na equipe.",
        )

    pokemons = [await service.get_pokemon_summary(name) for name in normalized_names]
    team = {"trainer": trainer_name.strip(), "pokemons": pokemons}
    app.state.teams[normalize_name(trainer_name)] = team
    return team


@app.delete("/captures/{capture_id}")
async def delete_capture(capture_id: int):
    capture = app.state.captures.pop(capture_id, None)
    if capture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Captura nao encontrada.")

    return {"message": "Captura removida com sucesso.", "removed_capture": capture}


@app.delete("/teams/{trainer_name}")
async def delete_team(trainer_name: str):
    team = app.state.teams.pop(normalize_name(trainer_name), None)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipe nao encontrada.")

    return {"message": "Equipe removida com sucesso.", "removed_team": team}


@app.patch("/captures/{capture_id}")
async def patch_capture(
    capture_id: int,
    payload: CapturePatch,
    service: PokemonService = Depends(get_pokemon_service),
):
    capture = app.state.captures.get(capture_id)
    if capture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Captura nao encontrada.")

    updates = payload.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie pelo menos um campo para atualizar.",
        )

    if "pokemon_name" in updates:
        capture["pokemon"] = await service.get_pokemon_summary(normalize_name(updates["pokemon_name"]))
    if "trainer" in updates:
        capture["trainer"] = updates["trainer"].strip()
    if "nickname" in updates:
        capture["nickname"] = updates["nickname"]

    return capture


@app.patch("/teams/{trainer_name}")
async def patch_team(
    trainer_name: str,
    payload: TeamPatch,
    service: PokemonService = Depends(get_pokemon_service),
):
    team = app.state.teams.get(normalize_name(trainer_name))
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipe nao encontrada.")

    if payload.add_pokemon is None and payload.remove_pokemon is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe add_pokemon e/ou remove_pokemon.",
        )

    pokemons = team["pokemons"]

    if payload.remove_pokemon:
        to_remove = {normalize_name(name) for name in payload.remove_pokemon}
        pokemons = [pokemon for pokemon in pokemons if pokemon["name"] not in to_remove]

    if payload.add_pokemon:
        for pokemon_name in payload.add_pokemon:
            normalized_name = normalize_name(pokemon_name)
            if any(pokemon["name"] == normalized_name for pokemon in pokemons):
                continue
            if len(pokemons) >= 6:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Uma equipe pode ter no maximo 6 pokemons.",
                )
            pokemons.append(await service.get_pokemon_summary(normalized_name))

    team["pokemons"] = pokemons
    return team
