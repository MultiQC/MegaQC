Migrations (for developers)
===========================

You need to generate a new migration whenever the database schema (ie
any models class) changes. To generate a migration:

.. code:: bash

   cd megaqc
   export FLASK_APP=wsgi.py
   flask db upgrade # Update to the latest migration
   flask db migrate