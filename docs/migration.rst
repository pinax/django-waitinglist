.. _migration:

====================
Migration from Pinax
====================

django-waitinglist is based on ``pinax.apps.waitinglist`` and adds cohorts
support developed internally at Eldarion.

This document will outline the changes needed to migrate from Pinax to using
this app in your Django project. If you are new to django-waitinglist then
this guide will not be useful to you.

Database changes
================

::

    # @@@ todo

URL changes
===========

@@@ todo

View changes
============

All views have been converted to class-based views. This is a big departure
from the traditional function-based, but has the benefit of being much more
flexible.

@@@ todo: table of changes

Settings changes
================

@@@ todo

General changes
===============

django-waitinglist requires Django 1.4. This means we can take advantage of
many of the new features offered by Django. This app implements all of the
best practices of Django 1.4. If there is something missing you should let us
know!
