import redis
from django.conf import settings

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

try:
    redis_client.ping()
    print("✅ Redis connected successfully")
except redis.ConnectionError:
    print("❌ Redis connection failed")
