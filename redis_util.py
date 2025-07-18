import redis
import zlib
import pickle
import os

from utils import get_from_env_or_config

# Connect to Redis
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_DB = os.environ.get('REDIS_DB', 0)
REDIS_TTL = get_from_env_or_config('redis', 'ttl') # 12 hours (TTL in seconds)
redis_client = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), db=int(REDIS_DB))

def store_messages_in_redis(key, message, ttl=int(REDIS_TTL)):
    """Compresses a message using gzip and stores it in Redis."""
    redis_key = f"msg_{key}"
    serialized_json = pickle.dumps(message)
    compressed_data = zlib.compress(serialized_json)
    redis_client.setex(redis_key, ttl, compressed_data)

def read_messages_from_redis(key):
    """Retrieves a compressed message from Redis and decompresses it."""
    redis_key = f"msg_{key}"
    compressed_data = redis_client.get(redis_key)
    if compressed_data:
        decompressed_data = zlib.decompress(compressed_data)
        return pickle.loads(decompressed_data)
    else:
        return []  # Handle the case where the key doesn't exis

def clear_message_from_redis(redis_key):
    """
    Clears the stored messages for the given Redis key.
    """
    # Use the existing Redis client
    formatted_key = f"msg_{redis_key}" if not redis_key.startswith("msg_") else redis_key
    redis_client.delete(formatted_key)
    print(f"Cleared Redis key: {formatted_key}")