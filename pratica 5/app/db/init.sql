DROP TABLE IF EXISTS alunos;
DROP TABLE IF EXISTS matricula_counters;

CREATE TABLE matricula_counters (
    curso TEXT PRIMARY KEY CHECK (curso IN ('GES', 'GEC')),
    proxima_matricula INTEGER NOT NULL DEFAULT 1
);

INSERT INTO matricula_counters (curso, proxima_matricula)
VALUES ('GES', 1), ('GEC', 1);

CREATE TABLE alunos (
    id TEXT PRIMARY KEY,
    matricula INTEGER NOT NULL,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    curso TEXT NOT NULL CHECK (curso IN ('GES', 'GEC')),
    UNIQUE (curso, matricula)
);