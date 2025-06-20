from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Reads environment variables from the environment. If a variable is not found, the default
    value is used as defined here.

    WARNING: These are defaults, only used locally and overwritten in production. If you want to
    change anything here, you should also change .env.example
    """

    USING_ENV_FILE: int = 0

    # Backend interface (server) settings
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8080

    # DB handler settings
    DB_HANDLER_HOST: str = "db_handler"
    DB_HANDLER_PORT: int = 8080

    DB_SERVICE_URL: str = f"http://{DB_HANDLER_HOST}:{DB_HANDLER_PORT}"

    # Engine settings
    ENGINE_HOST: str = "execution_engine"
    ENGINE_PORT: int = 8080

    ENGINE_URL: str = f"http://{ENGINE_HOST}:{ENGINE_PORT}"

    NETWORK_TIMEOUT: int = 5

    # JWT
    # These values are overwritten at deployment; this is not a security vulnerability
    JWT_SECRET_KEY: str = "0123456789abcdef"
    JWT_ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_MINUTES: int = 10080


settings = Settings()

if settings.USING_ENV_FILE:
    # We want to force localhost if running locally
    # Without this; SERVER_HOST resolves to 'server', which won't run locally
    settings.SERVER_HOST = "127.0.0.1"  # pylint: disable=C0103
