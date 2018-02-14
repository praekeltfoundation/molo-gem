gem
=========================

This is an application scaffold for Molo_.

Getting started
---------------

To set up enviroment::

    $ virtualenv ve
    $ pip install -e .
    $ in a new terminal: redis-server
    $ ./manage.py migrate
    $ ./manage.py createsuperuser
    $ ./manage.py runserver

You can now connect access the demo site on http://localhost:8000

To get started::
	* login to : http://localhost:8000/admin
	* click on settings, then choose language
	* add a new language and save it
	* click settings and choose site settings
	* tick all the ARTICLE TAG SETTINGS (Display tags on front ent and enable tag navigation)

.. _Molo: https://molo.readthedocs.org
