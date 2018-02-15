gem
=========================

This is an application scaffold for Molo_.

Getting started
---------------
In a separate terminal::

    $ redis-server

To set up enviroment::

    $ virtualenv ve
    $ pip install -e .
    $ ./manage.py migrate
    $ ./manage.py createsuperuser
    $ ./manage.py runserver

You can now connect access the demo site on http://localhost:8000

To get started::

	* log in to : http://localhost:8000/admin
	* click on settings, then choose language
	* add a new language and save it
	* click on settings and choose site settings
	* tick all the ARTICLE TAG SETTINGS (Display tags on front end and enable tag navigation)

.. _Molo: https://molo.readthedocs.org
