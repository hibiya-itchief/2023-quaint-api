from typing import Union

import redis

from app.config import settings


def redis_get_if_possible(key:str)->Union[str,None]:
    try:
        redis_conn = redis.Redis(host=settings.redis_host, port=6379, db=0,decode_responses=True)
        cache_result=redis_conn.get(key)
        if cache_result:
            return cache_result
    except:
        pass
    return None
def redis_set_if_possible(key:str,value:str,ex:int):
    try:
        redis_conn = redis.Redis(host=settings.redis_host, port=6379, db=0,decode_responses=True)
        result=redis_conn.set(key,value,ex)
        if result==0:
            return 0
    except:
        pass
    return 1

