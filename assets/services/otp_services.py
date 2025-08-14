import random
from assets.redis_client import redis_client

# 10 mins
OTP_EXPIRATION_SECONDS = 600


def generate_otp():
    return str(random.randint(100000, 999999))


def store_otp(email):
    otp = generate_otp()
    redis_client.setex(name=f"otp:{email}", time=OTP_EXPIRATION_SECONDS, value=otp)
    return otp


def verify_otp(email, otp):
    stored_otp = redis_client.get(f"otp:{email}")
    if stored_otp and stored_otp == otp:
        redis_client.delete(f"otp:{email}")
        return True
    return False
