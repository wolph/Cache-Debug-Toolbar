# work around modules with the same name
from __future__ import absolute_import

from cache_toolbar.panels import BasePanel, record
import logging

DEBUG = False


try:
    import pylibmc
    import _pylibmc

    # duplicating the client code sucks so hard, but it's necessary since the
    # original uses super and we'd need to inherit from it and then replace it
    # resulting in a class that inherits from itself :(see
    # http://fuhm.net/super-harmful/ anyway, see the bottom of this class for
    # the methods we're installing tracking on
    class TrackingPylibmcClient(_pylibmc.client):

        def __init__(self, servers, binary=False):
            '''Initialize a memcached client instance.

            This connects to the servers in *servers*, which will default to
            being TCP servers. If it looks like a filesystem path, a UNIX
            socket. If prefixed with `udp:`, a UDP connection.

            If *binary* is True, the binary memcached protocol is used.
            '''
            self.binary = binary
            self.addresses = list(servers)
            addr_tups = []
            for server in servers:
                addr = server
                port = 11211
                if server.startswith('udp:'):
                    stype = _pylibmc.server_type_udp
                    addr = addr[4:]
                    if ':' in server:
                        (addr, port) = addr.split(':', 1)
                        port = int(port)
                elif ':' in server:
                    stype = _pylibmc.server_type_tcp
                    (addr, port) = server.split(':', 1)
                    port = int(port)
                elif '/' in server:
                    stype = _pylibmc.server_type_unix
                    port = 0
                else:
                    stype = _pylibmc.server_type_tcp
                addr_tups.append((stype, addr, port))
            _pylibmc.client.__init__(self, servers=addr_tups, binary=binary)

        def __repr__(self):
            return '%s(%r, binary=%r)' % (self.__class__.__name__,
                                          self.addresses, self.binary)

        def __str__(self):
            addrs = ', '.join(map(str, self.addresses))
            return '<%s for %s, binary=%r>' % (self.__class__.__name__,
                                               addrs, self.binary)

        @property
        def behaviours(self):
            raise AttributeError('nobody uses british spellings')

        # methods we're adding tracking to

        @record
        def get(self, *args, **kwargs):
            return _pylibmc.client.get(self, *args, **kwargs)

        @record
        def get_multi(self, *args, **kwargs):
            return _pylibmc.client.get_multi(self, *args, **kwargs)

        @record
        def set(self, *args, **kwargs):
            return _pylibmc.client.set(self, *args, **kwargs)

        @record
        def set_multi(self, *args, **kwargs):
            return _pylibmc.client.set_multi(self, *args, **kwargs)

        @record
        def add(self, *args, **kwargs):
            return _pylibmc.client.add(self, *args, **kwargs)

        @record
        def replace(self, *args, **kwargs):
            return _pylibmc.client.replace(self, *args, **kwargs)

        @record
        def append(self, *args, **kwargs):
            return _pylibmc.client.append(self, *args, **kwargs)

        @record
        def prepend(self, *args, **kwargs):
            return _pylibmc.client.prepend(self, *args, **kwargs)

        @record
        def incr(self, *args, **kwargs):
            return _pylibmc.client.incr(self, *args, **kwargs)

        @record
        def decr(self, *args, **kwargs):
            return _pylibmc.client.decr(self, *args, **kwargs)

        @record
        def delete(self, *args, **kwargs):
            return _pylibmc.client.delete(self, *args, **kwargs)

        @record
        def delete_multi(self, *args, **kwargs):
            # NOTE delete_multi is implemented by iterative over args calling
            # delete for each one. i could probably hide that here, but i
            # actually think it's best to show it since each one will be a
            # seperate network round-trip.
            return _pylibmc.client.delete_multi(self, *args, **kwargs)

        @record
        def flush_all(self, *args, **kwargs):
            return _pylibmc.client.flush_all(self, *args, **kwargs)

    # NOTE issubclass is true of both are the same class
    if not issubclass(pylibmc.Client, TrackingPylibmcClient):
        logging.debug('installing pylibmc.Client with tracking')
        pylibmc.Client = TrackingPylibmcClient

except:
    if DEBUG:
        logging.exception('unable to install pylibmc.Client with tracking')
    else:
        logging.debug('unable to install pylibmc.Client with tracking')


class PylibmcPanel(BasePanel):
    pass

