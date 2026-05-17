import os

import asyncpg

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/alunos_db",
)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS matricula_counters (
    curso TEXT PRIMARY KEY CHECK (curso IN ('GES', 'GEC')),
    proxima_matricula INTEGER NOT NULL DEFAULT 1
);

INSERT INTO matricula_counters (curso, proxima_matricula)
VALUES ('GES', 1), ('GEC', 1)
ON CONFLICT (curso) DO NOTHING;

CREATE TABLE IF NOT EXISTS alunos (
    id TEXT PRIMARY KEY,
    matricula INTEGER NOT NULL,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    curso TEXT NOT NULL CHECK (curso IN ('GES', 'GEC')),
    UNIQUE (curso, matricula)
);
"""


async def get_connection():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(SCHEMA_SQL)
    return conn