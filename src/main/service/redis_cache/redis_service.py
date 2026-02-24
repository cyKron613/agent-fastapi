from typing import Any, Dict, List, Optional
from src.main.core.util.redis_client import RedisClient
from src.main.schema.redis_cache import (
    RedisCacheKeyVo, RedisCacheValueVo, 
    RedisHashSetVo, RedisHashGetVo, RedisHashDelVo,
    RedisListPushVo, RedisListRangeVo,
    RedisSetAddVo, RedisSetRemVo,
    RedisSortedSetAddVo, RedisSortedSetRangeVo,
    RedisCacheDeletePatternVo,
    RedisResponseVo
)


class RedisService:
    """Redis服务类"""
    
    def __init__(self):
        self.redis_client = RedisClient()
    
    async def get_value(self, inputs: RedisCacheKeyVo) -> RedisResponseVo:
        """获取Redis键值"""
        try:
            result = self.redis_client.get(inputs.key)
            return RedisResponseVo(
                code=200,
                message="success",
                data=result
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"获取Redis键值失败: {str(e)}",
                data=None
            )
    
    async def set_value(self, inputs: RedisCacheValueVo) -> RedisResponseVo:
        """设置Redis键值"""
        try:
            result = self.redis_client.set(inputs.key, inputs.value, ex=inputs.expire)
            return RedisResponseVo(
                code=200,
                message="success",
                data=result
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"设置Redis键值失败: {str(e)}",
                data=None
            )
    
    async def delete_key(self, inputs: RedisCacheKeyVo) -> RedisResponseVo:
        """删除Redis键"""
        try:
            result = self.redis_client.delete(inputs.key)
            return RedisResponseVo(
                code=200,
                message="success",
                data=result
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"删除Redis键失败: {str(e)}",
                data=None
            )
    
    async def exists_key(self, inputs: RedisCacheKeyVo) -> RedisResponseVo:
        """检查Redis键是否存在"""
        try:
            result = self.redis_client.exists(inputs.key)
            return RedisResponseVo(
                code=200,
                message="success",
                data=result
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"检查Redis键是否存在失败: {str(e)}",
                data=None
            )
    
    async def set_hash(self, inputs: RedisHashSetVo) -> RedisResponseVo:
        """设置哈希表字段值"""
        try:
            result = self.redis_client.hset(inputs.name, inputs.key, inputs.value)
            return RedisResponseVo(
                code=200,
                message="success",
                data=result
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"设置哈希表字段值失败: {str(e)}",
                data=None
            )
    
    async def get_hash(self, inputs: RedisHashGetVo) -> RedisResponseVo:
        """获取哈希表字段值"""
        try:
            result = self.redis_client.hget(inputs.name, inputs.key)
            return RedisResponseVo(
                code=200,
                message="success",
                data=result
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"获取哈希表字段值失败: {str(e)}",
                data=None
            )
    
    async def get_all_hash(self, inputs: RedisCacheKeyVo) -> RedisResponseVo:
        """获取哈希表所有字段和值"""
        try:
            result = self.redis_client.hgetall(inputs.key)
            return RedisResponseVo(
                code=200,
                message="success",
                data=result
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"获取哈希表所有字段和值失败: {str(e)}",
                data=None
            )
    
    async def delete_hash(self, inputs: RedisHashDelVo) -> RedisResponseVo:
        """删除哈希表字段"""
        try:
            result = self.redis_client.hdel(inputs.name, *inputs.keys)
            return RedisResponseVo(
                code=200,
                message="success",
                data=result
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"删除哈希表字段失败: {str(e)}",
                data=None
            )
    
    async def left_push_list(self, inputs: RedisListPushVo) -> RedisResponseVo:
        """向列表头部添加元素"""
        try:
            result = self.redis_client.lpush(inputs.name, *inputs.values)
            return RedisResponseVo(
                code=200,
                message="success",
                data=result
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"向列表头部添加元素失败: {str(e)}",
                data=None
            )
    
    async def right_push_list(self, inputs: RedisListPushVo) -> RedisResponseVo:
        """向列表尾部添加元素"""
        try:
            result = self.redis_client.rpush(inputs.name, *inputs.values)
            return RedisResponseVo(
                code=200,
                message="success",
                data=result
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"向列表尾部添加元素失败: {str(e)}",
                data=None
            )
    
    async def get_list_range(self, inputs: RedisListRangeVo) -> RedisResponseVo:
        """获取列表指定范围内的元素"""
        try:
            result = self.redis_client.lrange(inputs.name, inputs.start, inputs.end)
            return RedisResponseVo(
                code=200,
                message="success",
                data=result
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"获取列表指定范围内的元素失败: {str(e)}",
                data=None
            )
    
    async def get_list_length(self, inputs: RedisCacheKeyVo) -> RedisResponseVo:
        """获取列表长度"""
        try:
            result = self.redis_client.llen(inputs.key)
            return RedisResponseVo(
                code=200,
                message="success",
                data=result
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"获取列表长度失败: {str(e)}",
                data=None
            )
    
    async def add_set_members(self, inputs: RedisSetAddVo) -> RedisResponseVo:
        """向集合添加成员"""
        try:
            result = self.redis_client.sadd(inputs.name, *inputs.values)
            return RedisResponseVo(
                code=200,
                message="success",
                data=result
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"向集合添加成员失败: {str(e)}",
                data=None
            )
    
    async def get_set_members(self, inputs: RedisCacheKeyVo) -> RedisResponseVo:
        """获取集合所有成员"""
        try:
            result = list(self.redis_client.smembers(inputs.key))
            return RedisResponseVo(
                code=200,
                message="success",
                data=result
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"获取集合所有成员失败: {str(e)}",
                data=None
            )
    
    async def remove_set_members(self, inputs: RedisSetRemVo) -> RedisResponseVo:
        """从集合移除成员"""
        try:
            result = self.redis_client.srem(inputs.name, *inputs.values)
            return RedisResponseVo(
                code=200,
                message="success",
                data=result
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"从集合移除成员失败: {str(e)}",
                data=None
            )
    
    async def add_sorted_set(self, inputs: RedisSortedSetAddVo) -> RedisResponseVo:
        """向有序集合添加成员"""
        try:
            mapping = {k: float(v) for k, v in inputs.mapping.items()}
            result = self.redis_client.zadd(inputs.name, mapping)
            return RedisResponseVo(
                code=200,
                message="success",
                data=result
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"向有序集合添加成员失败: {str(e)}",
                data=None
            )
    
    async def get_sorted_set_range(self, inputs: RedisSortedSetRangeVo) -> RedisResponseVo:
        """获取有序集合指定范围内的成员"""
        try:
            result = self.redis_client.zrange(
                inputs.name, 
                inputs.start, 
                inputs.end, 
                withscores=inputs.withscores
            )
            return RedisResponseVo(
                code=200,
                message="success",
                data=result
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"获取有序集合指定范围内的成员失败: {str(e)}",
                data=None
            )
    
    async def delete_pattern(self, inputs: RedisCacheDeletePatternVo) -> RedisResponseVo:
        """删除匹配模式的键"""
        try:
            # 使用scan_iter方法迭代查找所有匹配模式的键
            # scan_iter比keys命令更适合生产环境，不会阻塞Redis
            matching_keys = list(self.redis_client.client.scan_iter(match=inputs.pattern, count=1000))
            
            if not matching_keys:
                return RedisResponseVo(
                    code=200,
                    message="未找到匹配的键",
                    data=0
                )
            
            # 直接使用Redis的unlink命令（或del命令）批量删除，更高效
            deleted_count = self.redis_client.client.unlink(*matching_keys) if hasattr(self.redis_client.client, 'unlink') else self.redis_client.client.delete(*matching_keys)
            
            # 将字节串转换为字符串以便于在响应中显示
            deleted_keys = [key.decode('utf-8') if isinstance(key, bytes) else key for key in matching_keys]
            
            return RedisResponseVo(
                code=200,
                message=f"成功删除 {deleted_count} 个键",
                data={
                    "deleted_count": deleted_count,
                    "deleted_keys": deleted_keys[:100] if len(deleted_keys) > 100 else deleted_keys,  # 仅返回前100个，避免响应过大
                    "total_deleted": len(deleted_keys)
                }
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"删除匹配模式的键失败: {str(e)}",
                data=None
            )
    
    async def clear_api_cache(self) -> RedisResponseVo:
        """清空所有API缓存"""
        try:
            # 使用scan_iter方法迭代查找所有api_cache:前缀的键
            api_cache_pattern = "api_cache:*"
            matching_keys = list(self.redis_client.client.scan_iter(match=api_cache_pattern, count=1000))
            
            if not matching_keys:
                return RedisResponseVo(
                    code=200,
                    message="未找到API缓存键",
                    data=0
                )
            
            # 直接使用Redis的unlink命令（或del命令）批量删除，更高效
            deleted_count = self.redis_client.client.unlink(*matching_keys) if hasattr(self.redis_client.client, 'unlink') else self.redis_client.client.delete(*matching_keys)
            
            return RedisResponseVo(
                code=200,
                message=f"成功清空 {deleted_count} 个API缓存",
                data={
                    "deleted_count": deleted_count,
                    "total_keys": len(matching_keys),
                    "pattern": api_cache_pattern
                }
            )
        except Exception as e:
            return RedisResponseVo(
                code=500,
                message=f"清空API缓存失败: {str(e)}",
                data=None
            ) 