import functools
import json
import re
from collections.abc import Callable
from typing import Any

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from redis.asyncio import ConnectionPool, Redis

from ..exceptions.cache_exceptions import CacheIdentificationInferenceError, InvalidRequestError, MissingClientError

pool: ConnectionPool | None = None
client: Redis | None = None


def _infer_resource_id(kwargs: dict[str, Any], resource_id_type: type | tuple[type, ...]) -> int | str:
    resource_id: int | str | None = None
    for arg_name, arg_value in kwargs.items():
        if isinstance(arg_value, resource_id_type):
            if (resource_id_type is int) and ("id" in arg_name):
                resource_id = arg_value

            elif (resource_id_type is int) and ("id" not in arg_name):
                pass

            elif resource_id_type is str:
                resource_id = arg_value

    if resource_id is None:
        raise CacheIdentificationInferenceError

    return resource_id