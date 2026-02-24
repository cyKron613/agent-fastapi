from functools import lru_cache
import decouple
from src.main.config.settings.base import BackendBaseSettings
from src.main.config.settings.development import BackendDevSettings
from src.main.config.settings.environment import Environment
from src.main.config.settings.production import BackendProdSettings


class BackendSettingsFactory:
    """
    后台配置工厂类
    """

    def __init__(self, environment: str):
        self.environment = environment

    def __call__(self) -> BackendBaseSettings:
        if self.environment == Environment.DEVELOPMENT.value:
            return BackendDevSettings()
        elif self.environment == Environment.PRODUCTION.value:
            return BackendProdSettings()
        return BackendDevSettings()


@lru_cache()
def get_settings() -> BackendBaseSettings:
    return BackendSettingsFactory(environment=decouple.config("ENVIRONMENT", default="DEV", cast=str))()  # type: ignore


settings: BackendBaseSettings = get_settings()
