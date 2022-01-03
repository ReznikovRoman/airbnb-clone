import redis
from redis.sentinel import Sentinel

from django.conf import settings


redis_instance = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    charset=settings.DEFAULT_CHARSET,
    decode_responses=settings.REDIS_DECODE_RESPONSES,
)
if not settings.DEBUG:
    sentinel = Sentinel(
        sentinels=settings.REDIS_CLUSTER_SENTINELS,
        socket_timeout=0.1,
        ssl=True,
        ssl_ca_certs=settings.REDIS_SSL_CERT_DOCKER_PATH,
    )
    redis_instance: redis.Redis = sentinel.master_for(
        service_name=settings.REDIS_CLUSTER_NAME,
        password=settings.REDIS_CLUSTER_PASSWORD,
        decode_responses=settings.REDIS_DECODE_RESPONSES,
    )
