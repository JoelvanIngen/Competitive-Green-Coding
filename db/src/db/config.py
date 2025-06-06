from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # DB handler settings
    DB_HANDLER_HOST: str = "0.0.0.0"
    DB_HANDLER_PORT: int = 8080

    # Postgres settings
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "test_db"
    POSTGRES_USER: str = "test_user"
    POSTGRES_PASSWORD: str = "test_password"

    USING_ENV_FILE: int = 0


settings = Settings()

if settings.USING_ENV_FILE == 1:
    # We want to force localhost if running locally
    # Without this; DB_HANDLER_HOST resolves to 'db', which won't run locally
    settings.DB_HANDLER_HOST = "127.0.0.1"
