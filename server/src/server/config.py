from pydantic_settings import BaseSettings


class Settings(BaseSettings):
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


settings = Settings()

if settings.USING_ENV_FILE:
    # We want to force localhost if running locally
    # Without this; SERVER_HOST resolves to 'server', which won't run locally
    settings.SERVER_HOST = "127.0.0.1"  # pylint: disable=C0103
