from django.conf import settings

import redis


r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    charset=settings.DEFAULT_CHARSET,
    decode_responses=settings.REDIS_DECODE_RESPONSES,
)
