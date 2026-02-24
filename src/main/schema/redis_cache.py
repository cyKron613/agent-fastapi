from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union


class RedisCacheKeyVo(BaseModel):
    """Redis缓存键请求模型"""
    key: str = Field(..., description="Redis键名")


class RedisCacheValueVo(BaseModel):
    """Redis缓存值请求模型"""
    key: str = Field(..., description="Redis键名")
    value: Any = Field(..., description="Redis键值")
    expire: Optional[int] = Field(None, description="过期时间(秒)")


class RedisCacheDeletePatternVo(BaseModel):
    """Redis按模式删除键请求模型"""
    pattern: str = Field(..., description="要匹配的键模式，例如：'api_cache:*'")


class RedisHashSetVo(BaseModel):
    """Redis哈希表设置请求模型"""
    name: str = Field(..., description="哈希表名称")
    key: str = Field(..., description="字段名")
    value: Any = Field(..., description="字段值")


class RedisHashGetVo(BaseModel):
    """Redis哈希表获取请求模型"""
    name: str = Field(..., description="哈希表名称")
    key: str = Field(..., description="字段名")


class RedisHashDelVo(BaseModel):
    """Redis哈希表删除请求模型"""
    name: str = Field(..., description="哈希表名称")
    keys: List[str] = Field(..., description="字段名列表")


class RedisListPushVo(BaseModel):
    """Redis列表推入请求模型"""
    name: str = Field(..., description="列表名称")
    values: List[Any] = Field(..., description="值列表")


class RedisListRangeVo(BaseModel):
    """Redis列表范围请求模型"""
    name: str = Field(..., description="列表名称")
    start: int = Field(0, description="起始索引")
    end: int = Field(-1, description="结束索引")


class RedisSetAddVo(BaseModel):
    """Redis集合添加请求模型"""
    name: str = Field(..., description="集合名称")
    values: List[Any] = Field(..., description="值列表")


class RedisSetRemVo(BaseModel):
    """Redis集合移除请求模型"""
    name: str = Field(..., description="集合名称")
    values: List[Any] = Field(..., description="值列表")


class RedisSortedSetAddVo(BaseModel):
    """Redis有序集合添加请求模型"""
    name: str = Field(..., description="有序集合名称")
    mapping: Dict[str, float] = Field(..., description="成员分数映射")


class RedisSortedSetRangeVo(BaseModel):
    """Redis有序集合范围请求模型"""
    name: str = Field(..., description="有序集合名称")
    start: int = Field(0, description="起始索引")
    end: int = Field(-1, description="结束索引")
    withscores: bool = Field(False, description="是否返回分数")


class RedisResponseVo(BaseModel):
    """Redis操作响应模型"""
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="状态信息")
    data: Any = Field(None, description="响应数据") 