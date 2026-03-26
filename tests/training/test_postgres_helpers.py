from __future__ import annotations

from pathlib import Path

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
