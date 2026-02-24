import typing
import uuid

from sqlalchemy.orm import DeclarativeBase


def generate_uuid():
    return str(uuid.uuid4())


class DBTable(DeclarativeBase):
    pass


BaseModel: typing.Type[DeclarativeBase] = DBTable
