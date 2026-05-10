import os
from app.config import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.app_name == "ContentForge"
    assert settings.database_url == "sqlite:///./data/contentforge.db"
    assert settings.chroma_persist_dir == "./data/chroma"
    assert settings.obsidian_vault_path is None


def test_settings_from_env():
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["CHROMA_PERSIST_DIR"] = "./test_chroma"
    settings = Settings()
    assert settings.database_url == "sqlite:///./test.db"
    assert settings.chroma_persist_dir == "./test_chroma"
