======================
Cache Debug Toolbar
======================

The Cache Debug Toolbar is an add-on for Django Debug Toolbar for tracking
cache usage. It currently supports the ``redis``, ``pylibmc`` and ``memcache`` libraries.

This is definitely beta software, but I've found it useful in work and personal
projects. Feedback welcome, patches appreciated. - Ross McFarland

Installation
============

#. Install and configure `Django Debug Toolbar <https://github.com/django-debug-toolbar/django-debug-toolbar>`_.

#. Add the ``cache_toolbar`` app to your ``INSTALLED_APPS``.

#. Import the panel corresponding to the library you're using.

   The following must be imported in your ``settings.py`` file so that it has a
   chance to replace the caching library with one capable of tracking. You'll
   probably want to import it in ``local_settings.py`` (if you use the pattern) or
   at least wrap the import line in ``if DEBUG``:

   For ``redis``::

	import cache_toolbar.panels.redis

   For ``memcache``::

	import cache_toolbar.panels.memcache

   For ``pylibmc``::

	import cache_toolbar.panels.pylibmc

Configuration
=============

#. Add the ``cache`` panel to ``DEBUG_TOOLBAR_PANELS``.

   You'll need to add the panel corresponding to the library you'll be using to
   the list of debug toolbar's panels in the order in which you'd like it to
   appear::

	DEBUG_TOOLBAR_PANELS = (
            ...
	    'memcache_toolbar.panels.BasePanel',
	)
