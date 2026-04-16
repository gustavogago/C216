# Pratica 3 - API com PokeAPI

API em FastAPI com:

- `2x GET`
- `2x POST`
- `2x PUT`
- `2x DELETE`
- `2x PATCH`
- middleware de log de tempo de requisicao
- testes de API com log imprimivel

## Rotas implementadas

### GET
- `GET /pokemon`
- `GET /pokemon/{pokemon_name}`

### POST
- `POST /captures`
- `POST /battles/compare`

### PUT
- `PUT /captures/{capture_id}`
- `PUT /teams/{trainer_name}`

### DELETE
- `DELETE /captures/{capture_id}`
- `DELETE /teams/{trainer_name}`

### PATCH
- `PATCH /captures/{capture_id}`
- `PATCH /teams/{trainer_name}`

## Executar com Docker

No diretorio `pratica3`:

```bash
docker build -t pratica3-api .
docker run --rm -p 8000:8000 pratica3-api
```

API em: `http://localhost:8000`
Swagger: `http://localhost:8000/docs`

## Testes de API com log imprimivel

### PowerShell

```powershell
docker run --rm pratica3-api pytest -q -s -p no:cacheprovider tests | Tee-Object -FilePath test-log.txt
```

Ou localmente (sem Docker), apos instalar dependencias:

```powershell
.\run_api_tests.ps1
```

### Bash

```bash
docker run --rm pratica3-api sh -c "pytest -q -s -p no:cacheprovider tests | tee test-log.txt"
```

Ou localmente (sem Docker):

```bash
sh run_api_tests.sh
```
