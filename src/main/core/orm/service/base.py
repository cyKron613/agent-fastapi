from typing import TypeVar, Generic

from src.main.core.orm.repository.base import (
    BaseRepository,
)

T = TypeVar("T", bound=BaseRepository)


class BaseService(Generic[T]):
    """
    基础服务层
    """

    def __init__(self, repo: T):
        self.repo = repo
