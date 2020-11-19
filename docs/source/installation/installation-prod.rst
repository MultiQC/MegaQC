MegaQC Installation: Production
===============================

1. Install the MegaQC package
-----------------------------

MegaQC is available on both the Python Package Index (PyPI) and conda
(bioconda channel). To install using PyPI, run the following command:

.. code:: bash

   pip install megaqc[prod]

To install with conda:

.. code:: bash

   conda install -c bioconda megaqc

2. Export environment variables
-------------------------------

By default, MegaQC runs in development mode with a sqlite flat file
database (this is to make it as simple as possible to get up and running
for a quick test / demo). To tell MegaQC to use a production server, you
need to set the ``MEGAQC_PRODUCTION`` environment variable to true.

If you are running MegaQC behind a custom domain name (recommended, it’s
nicer than just having a difficult to remember IP address), then you
need to set ``SERVER_NAME`` to the URL of the website.

Add the following lines to your ``.bashrc`` file:

.. code:: bash

   export MEGAQC_PRODUCTION=1
   export SERVER_NAME='http://megaqc.yourdomain.com'

3. Set up the database
----------------------

MegaQC uses the Flask SQLAlchemy plugin, meaning that it can be used
with any SQL database (PostgreSQL, MySQL, SQLite and others).

MegaQC has been developed with PostgreSQL, see below. For instructions.
If you use MegaQC with any other database tools and could contribute to
the documentation, that would be great!

3.1 Using a PostgreSQL database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, install PostgreSQL:
https://wiki.postgresql.org/wiki/Detailed_installation_guides

Then, install the Python package that handles requests:

.. code:: bash

   pip install psycopg2

(``psycopq2-binary`` for psycopq v2.8 and above)

MegaQC can assess whether the database to use is ``postgresql``. If it
is, it will try to connect as ``megaqc_user`` to the database ``megaqc``
on ``localhost:5432``. On failure, MegaQC will attempt to create the
user and the database, and will then export the schema.

In order to make this happen, run :

.. code:: bash

   megaqc initdb

3.2 Using a MySQL database
~~~~~~~~~~~~~~~~~~~~~~~~~~

Although PostgreSQL is highly recommended, MegaQC should work with other
SQL database back ends, such as MySQL.

   Please note that MySQL support is currently untested and unsupported.
   If you use MegaQC with MySQL we’d love to hear about your
   experiences!

First, install MySQL:
https://dev.mysql.com/doc/refman/5.7/en/installing.html

Then install the `Python MySQL connector`_ (alternatively with the `PyPI
package`_).

Now, create a custom MegaQC configuration file somewhere and set the
environment variable ``MEGAQC_CONFIG`` to point to it. For example, in
``~/.bashrc``:

.. code:: bash

   export MEGAQC_CONFIG="/path/to/megaqc_config.yaml"

Then in this file, set the following configuration key pair:

.. code:: yaml

   SQLALCHEMY_DBMS: mysql

This should, hopefully, make everything work. If you have problems,
please `create an issue`_ and we’ll do our best to help.

4. (Optional, but recommended) Creat
------------------------------------

.. _Python MySQL connector: https://dev.mysql.com/downloads/connector/python/2.1.html
.. _PyPI package: https://pypi.python.org/pypi/mysql-connector-python/2.0.4
.. _create an issue: https://github.com/ewels/MegaQC/issues/new