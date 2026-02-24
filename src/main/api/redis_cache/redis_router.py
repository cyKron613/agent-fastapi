import fastapi
from fastapi import Body, Depends
from src.main.service.redis_cache.redis_service import RedisService
from src.main.schema.redis_cache import (
    RedisCacheKeyVo, RedisCacheValueVo, 
    RedisHashSetVo, RedisHashGetVo, RedisHashDelVo,
    RedisListPushVo, RedisListRangeVo,
    RedisSetAddVo, RedisSetRemVo,
    RedisSortedSetAddVo, RedisSortedSetRangeVo,
    RedisResponseVo, RedisCacheDeletePatternVo
)

router = fastapi.APIRouter(prefix="/v1/redis", tags=["Redis缓存"])


@router.post(
    path="/get",
    name="redis_get",
    status_code=fastapi.status.HTTP_200_OK,
    summary="获取Redis键值",
    description="根据键名获取Redis中的值",
    response_model=RedisResponseVo
)
async def get_redis_value(
    inputs: RedisCacheKeyVo = Body(
        ...,
        example={
            "key": "test_key"
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """获取Redis键值"""
    return await service.get_value(inputs)


@router.post(
    path="/set",
    name="redis_set",
    status_code=fastapi.status.HTTP_200_OK,
    summary="设置Redis键值",
    description="设置Redis中的键值，可设置过期时间",
    response_model=RedisResponseVo
)
async def set_redis_value(
    inputs: RedisCacheValueVo = Body(
        ...,
        example={
            "key": "test_key",
            "value": "test_value",
            "expire": 3600
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """设置Redis键值"""
    return await service.set_value(inputs)


@router.post(
    path="/delete",
    name="redis_delete",
    status_code=fastapi.status.HTTP_200_OK,
    summary="删除Redis键",
    description="删除Redis中的键",
    response_model=RedisResponseVo
)
async def delete_redis_key(
    inputs: RedisCacheKeyVo = Body(
        ...,
        example={
            "key": "test_key"
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """删除Redis键"""
    return await service.delete_key(inputs)


@router.post(
    path="/exists",
    name="redis_exists",
    status_code=fastapi.status.HTTP_200_OK,
    summary="检查Redis键是否存在",
    description="检查Redis中的键是否存在",
    response_model=RedisResponseVo
)
async def exists_redis_key(
    inputs: RedisCacheKeyVo = Body(
        ...,
        example={
            "key": "test_key"
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """检查Redis键是否存在"""
    return await service.exists_key(inputs)


@router.post(
    path="/hash/set",
    name="redis_hash_set",
    status_code=fastapi.status.HTTP_200_OK,
    summary="设置Redis哈希表字段",
    description="设置Redis哈希表中字段的值",
    response_model=RedisResponseVo
)
async def set_redis_hash(
    inputs: RedisHashSetVo = Body(
        ...,
        example={
            "name": "test_hash",
            "key": "field1",
            "value": "value1"
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """设置Redis哈希表字段"""
    return await service.set_hash(inputs)


@router.post(
    path="/hash/get",
    name="redis_hash_get",
    status_code=fastapi.status.HTTP_200_OK,
    summary="获取Redis哈希表字段",
    description="获取Redis哈希表中字段的值",
    response_model=RedisResponseVo
)
async def get_redis_hash(
    inputs: RedisHashGetVo = Body(
        ...,
        example={
            "name": "test_hash",
            "key": "field1"
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """获取Redis哈希表字段"""
    return await service.get_hash(inputs)


@router.post(
    path="/hash/getall",
    name="redis_hash_getall",
    status_code=fastapi.status.HTTP_200_OK,
    summary="获取Redis哈希表所有字段",
    description="获取Redis哈希表中所有字段和值",
    response_model=RedisResponseVo
)
async def get_all_redis_hash(
    inputs: RedisCacheKeyVo = Body(
        ...,
        example={
            "key": "test_hash"
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """获取Redis哈希表所有字段"""
    return await service.get_all_hash(inputs)


@router.post(
    path="/hash/delete",
    name="redis_hash_delete",
    status_code=fastapi.status.HTTP_200_OK,
    summary="删除Redis哈希表字段",
    description="删除Redis哈希表中的一个或多个字段",
    response_model=RedisResponseVo
)
async def delete_redis_hash(
    inputs: RedisHashDelVo = Body(
        ...,
        example={
            "name": "test_hash",
            "keys": ["field1", "field2"]
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """删除Redis哈希表字段"""
    return await service.delete_hash(inputs)


@router.post(
    path="/list/lpush",
    name="redis_list_lpush",
    status_code=fastapi.status.HTTP_200_OK,
    summary="向Redis列表头部添加元素",
    description="向Redis列表头部添加一个或多个元素",
    response_model=RedisResponseVo
)
async def left_push_redis_list(
    inputs: RedisListPushVo = Body(
        ...,
        example={
            "name": "test_list",
            "values": ["value1", "value2"]
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """向Redis列表头部添加元素"""
    return await service.left_push_list(inputs)


@router.post(
    path="/list/rpush",
    name="redis_list_rpush",
    status_code=fastapi.status.HTTP_200_OK,
    summary="向Redis列表尾部添加元素",
    description="向Redis列表尾部添加一个或多个元素",
    response_model=RedisResponseVo
)
async def right_push_redis_list(
    inputs: RedisListPushVo = Body(
        ...,
        example={
            "name": "test_list",
            "values": ["value1", "value2"]
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """向Redis列表尾部添加元素"""
    return await service.right_push_list(inputs)


@router.post(
    path="/list/range",
    name="redis_list_range",
    status_code=fastapi.status.HTTP_200_OK,
    summary="获取Redis列表指定范围内的元素",
    description="获取Redis列表指定范围内的元素",
    response_model=RedisResponseVo
)
async def get_redis_list_range(
    inputs: RedisListRangeVo = Body(
        ...,
        example={
            "name": "test_list",
            "start": 0,
            "end": -1
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """获取Redis列表指定范围内的元素"""
    return await service.get_list_range(inputs)


@router.post(
    path="/list/length",
    name="redis_list_length",
    status_code=fastapi.status.HTTP_200_OK,
    summary="获取Redis列表长度",
    description="获取Redis列表的长度",
    response_model=RedisResponseVo
)
async def get_redis_list_length(
    inputs: RedisCacheKeyVo = Body(
        ...,
        example={
            "key": "test_list"
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """获取Redis列表长度"""
    return await service.get_list_length(inputs)


@router.post(
    path="/set/add",
    name="redis_set_add",
    status_code=fastapi.status.HTTP_200_OK,
    summary="向Redis集合添加成员",
    description="向Redis集合添加一个或多个成员",
    response_model=RedisResponseVo
)
async def add_redis_set_members(
    inputs: RedisSetAddVo = Body(
        ...,
        example={
            "name": "test_set",
            "values": ["member1", "member2"]
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """向Redis集合添加成员"""
    return await service.add_set_members(inputs)


@router.post(
    path="/set/members",
    name="redis_set_members",
    status_code=fastapi.status.HTTP_200_OK,
    summary="获取Redis集合所有成员",
    description="获取Redis集合中的所有成员",
    response_model=RedisResponseVo
)
async def get_redis_set_members(
    inputs: RedisCacheKeyVo = Body(
        ...,
        example={
            "key": "test_set"
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """获取Redis集合所有成员"""
    return await service.get_set_members(inputs)


@router.post(
    path="/set/remove",
    name="redis_set_remove",
    status_code=fastapi.status.HTTP_200_OK,
    summary="从Redis集合移除成员",
    description="从Redis集合中移除一个或多个成员",
    response_model=RedisResponseVo
)
async def remove_redis_set_members(
    inputs: RedisSetRemVo = Body(
        ...,
        example={
            "name": "test_set",
            "values": ["member1", "member2"]
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """从Redis集合移除成员"""
    return await service.remove_set_members(inputs)


@router.post(
    path="/zset/add",
    name="redis_zset_add",
    status_code=fastapi.status.HTTP_200_OK,
    summary="向Redis有序集合添加成员",
    description="向Redis有序集合添加一个或多个成员，每个成员关联一个分数",
    response_model=RedisResponseVo
)
async def add_redis_sorted_set(
    inputs: RedisSortedSetAddVo = Body(
        ...,
        example={
            "name": "test_zset",
            "mapping": {
                "member1": 1.0,
                "member2": 2.0
            }
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """向Redis有序集合添加成员"""
    return await service.add_sorted_set(inputs)


@router.post(
    path="/zset/range",
    name="redis_zset_range",
    status_code=fastapi.status.HTTP_200_OK,
    summary="获取Redis有序集合指定范围内的成员",
    description="通过索引区间返回Redis有序集合中指定区间内的成员",
    response_model=RedisResponseVo
)
async def get_redis_sorted_set_range(
    inputs: RedisSortedSetRangeVo = Body(
        ...,
        example={
            "name": "test_zset",
            "start": 0,
            "end": -1,
            "withscores": True
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """获取Redis有序集合指定范围内的成员"""
    return await service.get_sorted_set_range(inputs)


@router.post(
    path="/delete_pattern",
    name="redis_delete_pattern",
    status_code=fastapi.status.HTTP_200_OK,
    summary="删除Redis按模式匹配的键",
    description="删除Redis中所有匹配指定模式的键，例如：'api_cache:*'",
    response_model=RedisResponseVo
)
async def delete_redis_pattern(
    inputs: RedisCacheDeletePatternVo = Body(
        ...,
        example={
            "pattern": "api_cache:*"
        }
    ),
    service: RedisService = Depends(RedisService),
):
    """删除Redis按模式匹配的键"""
    return await service.delete_pattern(inputs)


@router.post(
    path="/clear_api_cache",
    name="redis_clear_api_cache",
    status_code=fastapi.status.HTTP_200_OK,
    summary="清空API缓存",
    description="删除所有以'api_cache:'开头的API缓存键",
    response_model=RedisResponseVo
)
async def clear_api_cache(
    service: RedisService = Depends(RedisService),
):
    """清空所有API缓存"""
    return await service.clear_api_cache() 