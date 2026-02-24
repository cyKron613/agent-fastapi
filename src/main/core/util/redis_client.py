import redis
from redis import Redis
from redis.cluster import RedisCluster
from typing import Any, Dict, List, Optional, Union
from src.main.config.manager import settings
from loguru import logger

class RedisClient:
    """Redis客户端工具类，支持集群和单机模式"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            logger.info(f"🔄 正在创建Redis客户端实例")
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            try:
                # 生产环境
                if settings.PROD_REDIS_CLUSTER:
                    # 生产环境 集群模式
                    # 正确的方式是使用host_port列表而不是字典列表
                    redis_nodes = settings.PROD_REDIS_NODES.split(",")
                    logger.info(f"🔌 正在连接生产环境Redis集群: {redis_nodes}")
                    
                    # 使用直接方式创建RedisCluster，不使用startup_nodes参数
                    self.client = RedisCluster(
                        host=redis_nodes[0].strip(),  # 使用第一个节点作为初始连接点
                        port=settings.PROD_REDIS_PORT,
                        password=settings.PROD_REDIS_PASSWORD,
                        decode_responses=True,
                        skip_full_coverage_check=True,
                        socket_timeout=3,  # 3秒连接超时
                        socket_connect_timeout=3,  # 3秒连接超时
                        # 默认会自动发现其他节点
                    )
                    logger.success(f"✅ 生产环境Redis集群连接成功")
                else:
                    # 生产环境 单机模式
                    logger.info(f"🔌 正在连接Redis单机: {settings.PROD_REDIS_HOST}:{settings.PROD_REDIS_PORT}")
                    self.client = Redis(
                        host=settings.PROD_REDIS_HOST,
                        port=settings.PROD_REDIS_PORT,
                        password=settings.PROD_REDIS_PASSWORD,
                        db=settings.PROD_REDIS_DB,
                        decode_responses=True,
                        socket_timeout=3,  # 3秒连接超时
                        socket_connect_timeout=3  # 3秒连接超时
                    )
                    logger.success(f"✅ 生产环境Redis单机连接成功")

                self._initialized = True
            except Exception as e:
                logger.error(f"❌ 生产环境Redis连接失败: {str(e)}")
                logger.info(f"🔌 正在连接测试环境Redis单机: {settings.TEST_REDIS_HOST}:{settings.TEST_REDIS_PORT}")
                self.client = Redis(
                    host=settings.TEST_REDIS_HOST,
                    port=settings.TEST_REDIS_PORT,
                    password=settings.TEST_REDIS_PASSWORD,
                    db=settings.TEST_REDIS_DB,
                    decode_responses=True,
                    socket_timeout=3,  # 3秒连接超时
                    socket_connect_timeout=3  # 3秒连接超时
                )
                logger.success(f"✅ 测试环境Redis单机连接成功")
            except Exception as e:
                logger.error(f"❌ 测试环境Redis单机连接失败: {str(e)}")

    
    def get(self, key: str) -> Any:
        """获取键值"""
        return self.client.get(key)
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """设置键值，可设置过期时间（秒）"""
        return self.client.set(key, value, ex=ex)
    
    def delete(self, key: str) -> int:
        """删除键值"""
        return self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return bool(self.client.exists(key))
    
    def expire(self, key: str, seconds: int) -> bool:
        """设置键的过期时间"""
        return self.client.expire(key, seconds)
    
    def ttl(self, key: str) -> int:
        """获取键的剩余过期时间"""
        return self.client.ttl(key)
    
    def hset(self, name: str, key: str, value: Any) -> int:
        """哈希表中设置字段值"""
        return self.client.hset(name, key, value)
    
    def hget(self, name: str, key: str) -> Any:
        """获取哈希表中字段值"""
        return self.client.hget(name, key)
    
    def hgetall(self, name: str) -> Dict[str, Any]:
        """获取哈希表中所有字段和值"""
        return self.client.hgetall(name)
    
    def hdel(self, name: str, *keys: str) -> int:
        """删除哈希表中一个或多个字段"""
        return self.client.hdel(name, *keys)
    
    def lpush(self, name: str, *values: Any) -> int:
        """将一个或多个值插入到列表头部"""
        return self.client.lpush(name, *values)
    
    def rpush(self, name: str, *values: Any) -> int:
        """将一个或多个值插入到列表尾部"""
        return self.client.rpush(name, *values)
    
    def lrange(self, name: str, start: int, end: int) -> List[Any]:
        """获取列表指定范围内的元素"""
        return self.client.lrange(name, start, end)
    
    def llen(self, name: str) -> int:
        """获取列表长度"""
        return self.client.llen(name)
    
    def sadd(self, name: str, *values: Any) -> int:
        """向集合添加一个或多个成员"""
        return self.client.sadd(name, *values)
    
    def smembers(self, name: str) -> set:
        """返回集合中的所有成员"""
        return self.client.smembers(name)
    
    def srem(self, name: str, *values: Any) -> int:
        """移除集合中一个或多个成员"""
        return self.client.srem(name, *values)
    
    def zadd(self, name: str, mapping: Dict[Any, float]) -> int:
        """向有序集合添加一个或多个成员"""
        return self.client.zadd(name, mapping)
    
    def zrange(self, name: str, start: int, end: int, withscores: bool = False) -> List[Any]:
        """通过索引区间返回有序集合中指定区间内的成员"""
        return self.client.zrange(name, start, end, withscores=withscores)
    
    def flushdb(self) -> bool:
        """清空当前数据库"""
        return self.client.flushdb()