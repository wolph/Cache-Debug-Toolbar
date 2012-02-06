# work around modules with the same name
from __future__ import absolute_import

from datetime import datetime
from debug_toolbar.panels import DebugPanel
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from os.path import dirname, realpath
import django
import logging
import SocketServer
import traceback
import threading
import functools
import cPickle as pickle
import pprint

logger = logging.getLogger(__name__)


class Calls:

    def __init__(self):
        self.reset()

    def reset(self):
        self._calls = []

    def append(self, call):
        self._calls.append(call)

    def calls(self):
        return self._calls

    def size(self):
        return len(self._calls)

    def last(self):
        return self._calls[-1]

instance = threading.local()


def _get_calls():
    if not hasattr(instance, 'calls'):
        instance.calls = Calls()
    return instance.calls

# based on the function with the same name in ddt's sql, i'd rather just use
# it than copy it, but i can't import it without things blowing up
django_path = realpath(dirname(django.__file__))
socketserver_path = realpath(dirname(SocketServer.__file__))


def tidy_stacktrace(strace):
    trace = []
    toolbar_settings = getattr(settings, 'DEBUG_TOOLBAR_CONFIG', {})
    for s in strace[:-1]:
        s_path = realpath(s[0])
        if toolbar_settings.get('HIDE_DJANGO_SQL', True) \
            and django_path in s_path and not 'django/contrib' in s_path:
            continue
        if socketserver_path in s_path:
            continue
        trace.append((s[0], s[1], s[2], s[3]))
    return trace


def repr_value(ret):
    try:
        if isinstance(ret, dict):
            rkeys = ret.keys()
            if '__pickle__' in rkeys:
                rkeys.remove('__pickle__')
                rkeys += pickle.loads(ret['__pickle__']).keys()

            ret = rkeys
        elif isinstance(ret, (list, tuple)) and len(ret) == 1:
            ret, = ret
        else:
            ret = ret
    except:
        try:
            ret = 'Unable to parse: %r' % ret
        except:
            ret = 'Unable to parse'
    
    ret = pprint.pformat(ret, indent=False, width=100)
    ret = ' '.join(ret.split())

    if ret[100:]:
        return ret[:97] + '...'
    else:
        return ret[:100]


def record(func):
    @functools.wraps(func)
    def recorder(*args, **kwargs):
        stacktrace = tidy_stacktrace(traceback.extract_stack())
        call = {'function': func.__name__, 'args': None,
                'stacktrace': stacktrace}
        _get_calls().append(call)
        call['args'] = repr_value(args[1:])
        ret = None
        try:
            # the clock starts now
            call['start'] = datetime.now()
            ret = func(*args, **kwargs)
        finally:
            # the clock stops now
            dur = datetime.now() - call['start']
            call['duration'] = ((dur.seconds * 1000)
                + (dur.microseconds / 1000.0))
            if func.__name__.startswith('get'):
                if ret is None:
                    call['miss'] = 1
                else:
                    call['hit'] = 1

        call['ret'] = repr_value(ret)
        return ret
    return recorder


class BasePanel(DebugPanel):
    name = 'Cache'
    has_content = True

    def process_request(self, request):
        _get_calls().reset()

    def nav_title(self):
        return _('Cache')

    def nav_subtitle(self):
        duration = 0
        calls = _get_calls().calls()
        for call in calls:
            duration += call['duration']
        n = len(calls)
        if (n > 0):
            return "%d calls, %0.2fms" % (n, duration)
        else:
            return "0 calls"

    def title(self):
        return _('Cache Calls')

    def url(self):
        return ''

    def content(self):
        calls = instance.calls.calls()
        stats = dict(
            calls=0,
            duration=0,
            hits=0,
            misses=0,
        )
        commands = dict()

        try:
            for call in calls:
                stats['calls'] += 1
                stats['duration'] += call['duration']
                stats['hits'] += call.get('hit', 0)
                stats['misses'] += call.get('miss', 0)
                function = call['function']

                # defaultdict would have been nice, but it kills the django
                # templates system
                commands[function] = commands.get(function, 0) + 1

            if stats['misses'] and stats['hits']:
                stats['hitratio'] = 100. / stats['hits'] / stats['misses']
            elif stats['misses']:
                stats['hitratio'] = 0
            else:
                stats['hitratio'] = 100.

            context = self.context.copy()
            context.update({
                'calls': calls,
                'stats': stats,
                'commands': commands,
            })

            return render_to_string('cache_toolbar/panels/cache.html',
                    context)
        except Exception:
            traceback.print_exc()

