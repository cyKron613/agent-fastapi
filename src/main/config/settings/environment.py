import enum


class Environment(str, enum.Enum):
    """
    后台环境枚举
    """

    PRODUCTION: str = "PROD"  # type: ignore
    DEVELOPMENT: str = "DEV"  # type: ignore
