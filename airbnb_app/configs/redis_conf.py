import redis

from django.conf import settings


redis_instance = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    charset=settings.DEFAULT_CHARSET,
    decode_responses=settings.REDIS_DECODE_RESPONSES,
)
