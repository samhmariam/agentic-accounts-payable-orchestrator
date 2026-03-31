from __future__ import annotations

import json
import os
from pathlib import Path

from aegisap.security import credentials
from aegisap.training.postgres import apply_migration_file, apply_migration_path


class FakeCursor:
    def __init__(self, statements: list[str]) -> None:
        self.statements = statements

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, statement: str) -> None:
        self.statements.append(statement)


class FakeConnection:
    def __init__(self) -> None:
        self.statements: list[str] = []
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self) -> FakeCursor:
        return FakeCursor(self.statements)

    def commit(self) -> None:
        self.committed = True


def test_apply_migration_file_executes_sql(monkeypatch, tmp_path: Path) -> None:
    sql_file = tmp_path / "migration.sql"
    sql_file.write_text("SELECT 1;", encoding="utf-8")
    fake_connection = FakeConnection()

    monkeypatch.setattr(
        "aegisap.training.postgres.build_connection_factory_from_env",
        lambda: (lambda: fake_connection),
    )

    apply_migration_file(sql_file)

    assert fake_connection.committed is True
    assert fake_connection.statements == ["SELECT 1;"]


def test_apply_migration_path_accepts_single_file(monkeypatch, tmp_path: Path) -> None:
    sql_file = tmp_path / "migration.sql"
    sql_file.write_text("SELECT 2;", encoding="utf-8")
    applied: list[Path] = []

    monkeypatch.setattr(
        "aegisap.training.postgres.apply_migration_file",
        lambda path: applied.append(Path(path)),
    )

    result = apply_migration_path(sql_file)

    assert result == [sql_file]
    assert applied == [sql_file]


def test_apply_migration_file_bootstraps_postgres_env_from_local_day0_state(
    monkeypatch,
    tmp_path: Path,
) -> None:
    state_path = tmp_path / "full.json"
    state_path.write_text(
        json.dumps(
            {
                "environment": {
                    "AZURE_POSTGRES_HOST": "example.postgres.database.azure.com",
                    "AZURE_POSTGRES_PORT": "5432",
                    "AZURE_POSTGRES_DB": "aegisap",
                    "AZURE_POSTGRES_USER": "user@example.com",
                }
            }
        ),
        encoding="utf-8",
    )
    sql_file = tmp_path / "migration.sql"
    sql_file.write_text("SELECT 3;", encoding="utf-8")
    fake_connection = FakeConnection()

    monkeypatch.setenv("AEGISAP_ENVIRONMENT", "local")
    monkeypatch.delenv("AZURE_POSTGRES_HOST", raising=False)
    monkeypatch.delenv("AZURE_POSTGRES_PORT", raising=False)
    monkeypatch.delenv("AZURE_POSTGRES_DB", raising=False)
    monkeypatch.delenv("AZURE_POSTGRES_USER", raising=False)
    monkeypatch.setattr(credentials, "_day0_state_candidates", lambda: [state_path])
    credentials._load_local_day0_environment.cache_clear()
    monkeypatch.setattr(
        "aegisap.training.postgres.get_token_credential",
        lambda: type("FakeCredential", (), {"get_token": lambda self, scope: type("Token", (), {"token": "fake-token"})()})(),
    )
    monkeypatch.setattr("aegisap.training.postgres.psycopg.connect", lambda conninfo: fake_connection)

    apply_migration_file(sql_file)

    assert fake_connection.committed is True
    assert fake_connection.statements == ["SELECT 3;"]
    assert os.environ["AZURE_POSTGRES_HOST"] == "example.postgres.database.azure.com"
    credentials._load_local_day0_environment.cache_clear()
