
from cachelib import FileSystemCache
import os
import uuid

# cache the cache yo
__cache = None


def __get_cache():
    """
    Simple wrapper around SimpleCache
    This should make it easy to swap out cache implementations later if needed
    :return: cache object
    """
    global __cache

    if not os.path.exists('/tmp/bootstrapper/cache'):
        os.makedirs('/tmp/bootstrapper/cache')

    if __cache is not None:
        return __cache

    try:
        __cache = FileSystemCache(cache_dir='/tmp/bootstrapper/cache/', threshold=256, default_timeout=300, mode=0o600)
        return __cache
    except OSError:
        raise


def set(obj):
    """
    sets an object in the cache for 300 seconds
    :param obj: hashable object
    :return: key used to later retrieve the object or None on error
    """
    key = str(uuid.uuid4())
    c = __get_cache()
    if c.set(key, obj):
        return key
    else:
        return None


def get(key):
    """
    Retrieves the object using the given key
    :param key: key that was returned from the set operation
    :return: object in question or None on error or not found
    """
    c = __get_cache()
    return c.get(key)
