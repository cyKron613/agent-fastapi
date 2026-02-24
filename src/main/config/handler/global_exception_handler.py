from loguru import logger
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi.exceptions import RequestValidationError

from src.main.core.util.exceptions.common import BizException
from src.main.core.util.exceptions.database import EntityDoesNotExist, EntityAlreadyExists
from src.main.core.util.exceptions.param import ParamInvalid
from src.main.core.util.messages.exceptions.common import param_invalid_details, not_found_details, \
    already_exist_details
from src.main.core.schema.base import ResponseError


def register_exception(app: FastAPI):
    """
    全局异常捕获
    :param app:
    :return:
    """

    # 捕获参数 验证错误
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, e: RequestValidationError):
        """
        捕获请求参数 验证错误
        :param request:
        :param e:
        :return:
        """
        logger.debug(f"参数错误URL:{request.url}Headers:{request.headers}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(ResponseError(status=400, data=str(e.args), message="参数不全或参数错误")),
        )

    # model参数 验证错误
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, e: ValidationError):
        """
        捕获请求参数 验证错误
        :param request:
        :param e:
        :return:
        """
        logger.debug(f"model参数错误")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(ResponseError(status=400, data=str(e.errors()), message="model参数错误")),
        )

    # 捕获业务异常
    @app.exception_handler(BizException)
    async def all_exception_handler(request: Request, e: BizException):
        """
        捕获业务异常
        :param request:
        :param e:
        :return:
        """

        response = ResponseError(status=e.code, message=e.message)  # type: ignore
        if isinstance(e, ParamInvalid):
            response.message = param_invalid_details(e.message)

        elif isinstance(e, EntityDoesNotExist):
            response.message = not_found_details(e.message)

        elif isinstance(e, EntityAlreadyExists):
            response.message = already_exist_details(e.message)

        logger.debug(f"业务异常 URL:{request.url} Headers:{request.headers} ")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(response),
        )

    # 捕获断言错误，用于返回错误状态
    @app.exception_handler(AssertionError)
    async def asser_exception_handler(request: Request, e: AssertionError):
        logger.debug(f"断言错误，URL：{request.url}, 此处条件不符合")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(ResponseError(status=400, data=str(e.args), message="参数不全或参数错误")),
        )


