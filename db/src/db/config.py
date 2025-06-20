from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Reads environment variables from the environment. If a variable is not found, the default
    value is used as defined here.

    WARNING: These are defaults, only used locally and overwritten in production. If you want to
    change anything here, you should also change .env.example
    """

    USING_ENV_FILE: int = 0

    # DB handler settings
    DB_HANDLER_HOST: str = "0.0.0.0"
    DB_HANDLER_PORT: int = 8080

    DB_ENGINE: str = "sqlite"

    DB_HANDLER_STORAGE_PATH: str = "../../storage"

    # Sub-folder structure
    CODE_SUBMISSION_DIR: str = "submissions"
    FRAMEWORK_DIR: str = "frameworks"
    WRAPPER_DIR: str = "wrappers"

    # Postgres settings
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "test_db"
    POSTGRES_USER: str = "test_user"
    POSTGRES_PASSWORD: str = "test_password"

    # JWT
    JWT_SECRET_KEY: str = "0123456789abcdef"
    JWT_ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_MINUTES: int = 10080


settings = Settings()

if settings.USING_ENV_FILE == 1:
    # We want to force localhost if running locally
    # Without this; DB_HANDLER_HOST resolves to 'db', which won't run locally
    settings.DB_HANDLER_HOST = "127.0.0.1"  # pylint: disable=C0103
