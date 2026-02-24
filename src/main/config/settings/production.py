from src.main.config.settings.base import BackendBaseSettings
from src.main.config.settings.environment import Environment


class BackendProdSettings(BackendBaseSettings):
    """
    后台生产环境配置
    """

    DESCRIPTION: str = "Production Environment."
    ENVIRONMENT: Environment = Environment.PRODUCTION
    
    POSTGRES_SCHEMA: str = "sdc_adm"
    POSTGRES_SCHEMA_ANOTHER: str = "sdc_adm"
