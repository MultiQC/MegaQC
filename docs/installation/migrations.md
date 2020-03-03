# Migrations

Migrations are updates to a database schema. This is relevant if, for example, you
set up a MegaQC database (using `initdb`), and then a new version of MegaQC is released
that needs new tables or columns.

Every time a new version of MegaQC is released, you should ensure your database is
up to date. Do so using the following commands:

```bash
cd megaqc
export FLASK_APP=wsgi.py
flask db upgrade
```

Note: when you run these migrations, you **must** have the same environment as you use
to run MegaQC normally, which means the same value of `FLASK_DEBUG` and
`MEGAQC_PRODUCTION` environment variables. Otherwise it will migrate the wrong database
(or a non-existing one).
