import typing
import fastapi
from sqlalchemy.ext.asyncio import (
    AsyncSession as SQLAlchemyAsyncSession,
)
from src.main.core.orm.service.base import (
    BaseService,
)
from src.main.core.orm.session.base import (
    get_async_session,
    get_async_another_session,
)
from src.main.core.orm.repository.base import (
    BaseRepository,
)


def get_async_repository(
    repo_type: typing.Type[BaseRepository],
) -> typing.Callable[[SQLAlchemyAsyncSession], BaseRepository]:
    def _get_repo(
        async_session: SQLAlchemyAsyncSession = fastapi.Depends(
            get_async_session
        ),
        async_another_session: SQLAlchemyAsyncSession | None = fastapi.Depends(
            get_async_another_session
        )
    ) -> BaseRepository:
        if async_another_session:
            return repo_type(
                async_session=async_session,
                async_another_session=async_another_session,
            )
        return repo_type(async_session=async_session)

    return _get_repo


def get_async_service(
    ser_type: typing.Type[BaseService],
    repo_type: typing.Type[BaseRepository],
) -> typing.Callable[[BaseRepository], BaseService]:
    def _get_service(
        repo: BaseRepository = fastapi.Depends(get_async_repository(repo_type)),
    ) -> BaseService:
        return ser_type(repo=repo)

    return _get_service