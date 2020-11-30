Migrations
==========

Introduction
------------

Migrations are updates to a database schema. This is relevant if, for
example, you set up a MegaQC database (using ``initdb``), and then a new
version of MegaQC is released that needs new tables or columns.

When to migrate
---------------

Every time a new version of MegaQC is released, you should ensure your
database is up to date. You don’t need to run the migrations the first
time you install MegaQC, because the ``megaqc initdb`` command replaces
the need for migrations.

How to migrate
--------------

To migrate, run the following commands:

.. code:: bash

   cd megaqc
   export FLASK_APP=wsgi.py
   flask db upgrade

Note: when you run these migrations, you **must** have the same
environment as you use to run MegaQC normally, which means the same
value of ``FLASK_DEBUG`` and ``MEGAQC_PRODUCTION`` environment
variables. Otherwise it will migrate the wrong database
(or a non-existing one).

Stamping your database
----------------------

The complete migration history has only recently been added. This means
that, if you were using MegaQC in the past when migrations were not
included in the repo, your database won’t know what version you’re currently at.

To fix this, first you need to work out which migration your database is
up to. Browse through the files in ``megaqc/migrations/versions``,
starting from the oldest date (at the top of each file), until you find
a change that wasn’t present in your database. At this point, note the
``revision`` value at the top of the file, (e.g. ``revision = "007c354223ec"``).

Next, run the following command, replacing ``<revision ID>`` with the
revision you noted above:

.. code:: bash

   flask db stamp <revision ID>
