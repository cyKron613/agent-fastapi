from src.main.core.util.exceptions.common import (
    BizException,
)


class EntityDoesNotExist(BizException):
    """
    Throw an handler when the data does not exist in the database.
    """


class EntityAlreadyExists(BizException):
    """
    Throw an handler when the data already exist in the database.
    """
