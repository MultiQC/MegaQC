Troubleshooting
===============

Installation/setup
--------------------

-  I’m getting a blank page when I open the ``/trends`` or ``/admin`` pages

   -  Make sure you’ve compiled the JavaScript correctly.
   -  Ensure you’ve run ``npm install`` and then ``npm run build`` or ``npm run watch``.

-  I am getting ``sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server: Connection refused Is the server running on host "127.0.0.1" and accepting TCP/IP connections on port 5432?``

   - Please ensure that you have a Postgres database accessible at "127.0.0.1:5432".

Usage
---------

-  When creating a violin plot I get an error.

   - This is a known issue: https://github.com/ewels/MegaQC/issues/31

-  TypeError: '<' not supported between instances of 'NoneType' and 'float' when trying to compare data

  - This is a known issue: https://github.com/ewels/MegaQC/issues/156
  - Please ensure that your reports do not have missing fields
