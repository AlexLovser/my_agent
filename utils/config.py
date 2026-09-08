from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    model_name: str = Field("gpt-4o-mini")
    openai_api_key: str = Field()


settings = Settings()
