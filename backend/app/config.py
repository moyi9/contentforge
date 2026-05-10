from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ContentForge"
    database_url: str = "sqlite:///./data/contentforge.db"
    chroma_persist_dir: str = "./data/chroma"
    chroma_collection_name: str = "contentforge_knowledge"
    obsidian_vault_path: str | None = None
    git_sync_interval: int = 300
    llm_model: str = "gpt-4o"
    llm_api_key: str | None = None
    llm_base_url: str | None = None
    unsplash_access_key: str | None = None
    mcp_server_port: int = 8765
    api_token: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
