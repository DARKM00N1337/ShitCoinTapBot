from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    SLEEP_BETWEEN_TAP: list[int] = [10, 25]
    CLICKS_FOR_SLEEP: list[int] = [100, 150]
    LONG_SLEEP_BETWEEN_TAP: list[int] = [6000, 7000]
    SLEEP_BY_MIN_ENERGY_IN_RANGE: list[int] = [300, 350]
    SHOW_BALANCE_EVERY_TAPS: int = 20

    USE_PROXY_FROM_FILE: bool = False


settings = Settings()
