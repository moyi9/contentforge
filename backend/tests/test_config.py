from app.config import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.app_name == "ContentForge"
    assert settings.database_url == "sqlite:///./data/contentforge.db"
    assert settings.chroma_persist_dir == "./data/chroma"
    assert settings.chroma_collection_name == "contentforge_knowledge"
    assert settings.obsidian_vault_path is None
    assert settings.git_sync_interval == 300
    assert settings.llm_model == "gpt-4o"
    assert settings.llm_api_key is None
    assert settings.llm_base_url is None
    assert settings.unsplash_access_key is None
    assert settings.mcp_server_port == 8765


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    monkeypatch.setenv("CHROMA_PERSIST_DIR", "./test_chroma")
    settings = Settings()
    assert settings.database_url == "sqlite:///./test.db"
    assert settings.chroma_persist_dir == "./test_chroma"
