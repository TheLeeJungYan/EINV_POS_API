from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

config = Settings()
print(config.DATABASE_URL)