import datetime
import typing
import pydantic
from pydantic import ConfigDict
from typing import Any, List
# from pydantic.generics import GenericModel
from pydantic import BaseModel
from src.main.core.util.formatters.datetime_formatter import (
    format_datetime_into_isoformat,
)
from src.main.core.util.formatters.field_formatter import (
    format_dict_key_to_camel_case,
)


class BaseVo(pydantic.BaseModel):
    model_config = ConfigDict(
        model_config={
            "from_attributes": True,
            "validate_assignment": True,
            "populate_by_name": True,
            "json_encoders": {
                datetime.datetime: format_datetime_into_isoformat
            },
            "alias_generator": format_dict_key_to_camel_case,
        }
    )


ResponseType = typing.TypeVar(
    "ResponseType",
    bound=typing.Union[int, str, dict, list, BaseVo, tuple, List, Any, None],
)


class ResponseVo(BaseModel, typing.Generic[ResponseType]):
    code: int = 200
    success: bool = True
    data: typing.Union[ResponseType, None] = None

    def __getitem__(self, item) -> typing.Union[ResponseType, None]:
        return self.data


class ResponseError(ResponseVo[str]):
    status: int
    message: str
    success: bool = False
