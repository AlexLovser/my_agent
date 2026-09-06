from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    model_name: str = Field("gemma-4-31b-it")
    chat_gpt_key: str = Field()


settings = Settings()
