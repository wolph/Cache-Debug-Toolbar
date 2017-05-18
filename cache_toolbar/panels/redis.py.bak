# work around modules with the same name
from __future__ import absolute_import

from cache_toolbar import panels
import logging
import datetime

DEBUG = False
logger = logging.getLogger(__name__)

READ_METHODS = (
    'LLEN',
    'LRANGE',
    'LINDEX',
    'LPOP',
    'RPOP',
    'RPOPLPUSH',
    'SCARD',
    'SINTER',
    'SUNION',
    'SDIFF',
    'SMEMBERS',
    'SRANDMEMBER',
    'ZRANK',
    'ZREVRANK',
    'ZRANGE',
    'ZREVRANGE',
    'ZRANGEBYSCORE',
    'ZCARD',
    'ZSCORE',
    'HLEN',
    'HKEYS',
    'HVALS',
    'HGETALL',
    'LASTSAVE',
)

try:
    import redis

    class TrackingRedis(redis.Redis):
        def execute_command(self, func_name, *args, **kwargs):
            stacktrace = panels.tidy_stacktrace(
                panels.traceback.extract_stack())

            call = {
                'function': func_name.lower(),
                'args': panels.repr_value(args),
                'stacktrace': stacktrace,
            }

            ret = None
            try:
                # the clock starts now
                call['start'] = datetime.datetime.now()
                ret = origRedis.execute_command(self, func_name,
                                                *args, **kwargs)

            finally:
                # the clock stops now
                call['stop'] = datetime.datetime.now()
                d = call['stop'] - call['start']
                call['duration'] = d.seconds * 1e3 + d.microseconds * 1e-3

                if func_name in READ_METHODS:
                    if ret:
                        call['hit'] = 1
                    else:
                        call['miss'] = 1

            call['ret'] = panels.repr_value(ret)

            panels._get_calls().append(call)
            return ret

    origRedis = None
    # NOTE issubclass is true if both are the same class
    if not issubclass(redis.Redis, TrackingRedis):
        logger.debug('installing redis.client.Redis with tracking')
        origRedis = redis.Redis
        redis.Redis = TrackingRedis

except:
    if DEBUG:
        logger.exception('unable to install redis.client.Redis with tracking')
    else:
        logger.debug('unable to install redis.client.Redis with tracking')


class RedisPanel(panels.BasePanel):
    pass
