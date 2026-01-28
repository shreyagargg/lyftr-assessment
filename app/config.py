from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str
    env: str
    database_url: str
    webhook_secret: str  
    log_level: str = "INFO"

    class Config:
        env_file = ".env"



settings = Settings()
