"""Tests de resolve_data_dir() - l'ordre de résolution est un contrat (CLAUDE.md)."""

from pathlib import Path

from app.core import config


def test_env_var_wins(tmp_path, monkeypatch):
    target = tmp_path / "custom"
    monkeypatch.setenv("CVFORGE_DATA", str(target))
    # Même avec un marqueur portable présent, la variable d'env prime.
    monkeypatch.setattr(config, "app_dir", lambda: tmp_path)
    (tmp_path / config.PORTABLE_MARKER).touch()

    assert config.resolve_data_dir() == target
    assert target.is_dir()


def test_portable_marker_uses_local_data_dir(tmp_path, monkeypatch):
    monkeypatch.delenv("CVFORGE_DATA", raising=False)
    monkeypatch.setattr(config, "app_dir", lambda: tmp_path)
    (tmp_path / config.PORTABLE_MARKER).touch()

    assert config.resolve_data_dir() == tmp_path / "data"
    assert (tmp_path / "data").is_dir()


def test_default_is_home_dot_cvforge(tmp_path, monkeypatch):
    monkeypatch.delenv("CVFORGE_DATA", raising=False)
    monkeypatch.setattr(config, "app_dir", lambda: tmp_path)  # pas de marqueur
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "fakehome")

    assert config.resolve_data_dir() == tmp_path / "fakehome" / ".cvforge"


def test_database_url_derives_from_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("CVFORGE_DATA", str(tmp_path))
    url = config.database_url()
    assert url.startswith("sqlite:///")
    assert url.endswith(config.DB_FILENAME)
