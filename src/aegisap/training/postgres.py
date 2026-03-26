from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

import psycopg

from aegisap.day5.persistence.durable_state_store import DurableStateStore

POSTGRES_SCOPE = "https://ossrdbms-aad.database.windows.net/.default"


def build_connection_factory_from_env() -> Callable[[], psycopg.Connection]:
    dsn = os.getenv("AEGISAP_POSTGRES_DSN", "").strip()
    if dsn:
        return lambda: psycopg.connect(dsn)

    required = {
        "AZURE_POSTGRES_HOST": os.getenv("AZURE_POSTGRES_HOST", "").strip(),
        "AZURE_POSTGRES_PORT": os.getenv("AZURE_POSTGRES_PORT", "").strip(),
        "AZURE_POSTGRES_DB": os.getenv("AZURE_POSTGRES_DB", "").strip(),
        "AZURE_POSTGRES_USER": os.getenv("AZURE_POSTGRES_USER", "").strip(),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        joined = ", ".join(sorted(missing))
        raise RuntimeError(f"Missing PostgreSQL connection settings: {joined}")

    from azure.identity import DefaultAzureCredential

    def connect() -> psycopg.Connection:
        try:
            credential = DefaultAzureCredential(exclude_interactive_browser_credential=True)
        except ValueError:
            credential = DefaultAzureCredential(
                exclude_environment_credential=True,
                exclude_interactive_browser_credential=True,
            )
        token = credential.get_token(POSTGRES_SCOPE).token
        conninfo = (
            f"host={required['AZURE_POSTGRES_HOST']} "
            f"port={required['AZURE_POSTGRES_PORT']} "
            f"dbname={required['AZURE_POSTGRES_DB']} "
            f"user={required['AZURE_POSTGRES_USER']} "
            f"password={token} sslmode=require"
        )
        return psycopg.connect(conninfo)

    return connect


def build_store_from_env() -> DurableStateStore:
    return DurableStateStore(connect_factory=build_connection_factory_from_env())


def apply_migration_file(path: str | Path) -> None:
    sql = Path(path).read_text(encoding="utf-8")
    with build_connection_factory_from_env()() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()


def apply_migration_path(path: str | Path) -> list[Path]:
    migration_path = Path(path)
    applied: list[Path] = []
    if migration_path.is_dir():
        for sql_file in sorted(migration_path.glob("*.sql")):
            apply_migration_file(sql_file)
            applied.append(sql_file)
        return applied

    apply_migration_file(migration_path)
    return [migration_path]
