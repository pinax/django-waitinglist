.. _installation:

============
Installation
============

* To install django-waitinglist (no releases have been yet)::

    pip install django-waitinglist

* Add ``waitinglist`` to your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        # ...
        "waitinglist",
        # ...
    )

* See the list of :ref:`settings` to modify the default behavior of
  django-waitinglist and make adjustments for your website.

* Add ``waitinglist.urls`` to your URLs definition::

    urlpatterns = patterns("",
        ...
        url(r"^waitinglist/", include("waitinglist.urls")),
        ...
    )

* To grant a user access the waitinglist management views, first
  ensure you've synced the database to create the
  ``waitinglist.manage_cohorts`` permission::

   from django.contrib.auth.models import User, Permission

   user = User.objects.get(username="finnegan")
   permission = Permission.objects.get(codename="manage_cohorts")
   user.user_permissions.add(permission)

.. _dependencies:

Dependencies
============

``django.contrib.auth``
-----------------------

This is bundled with Django. It is enabled by default with all new Django
projects, but if you're adding django-waitinglist to an existing project you
need to make sure ``django.contrib.auth`` is installed.

django-appconf_
---------------

We use django-appconf for app settings. It is listed in ``install_requires``
and will be installed when pip installs.

django-user-accounts_
---------------------

We use this app to handle all the sign up aspects. django-waitinglist is
integrated to some hooks provided by this app.

.. _django-appconf: https://github.com/jezdez/django-appconf
.. _django-user-accounts: https://github.com/pinax/django-user-accounts
