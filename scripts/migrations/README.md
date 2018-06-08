# Migrations

In this stage of MegaQC's development, breaking changes are likely to be made.
Scripts in here are used to make your existing installs work with the new code.

## PR #60

Pull request #60 changed database schemas and how table IDs are generated.

* `varchar2text.sql` - run using psql to update table definitions in postgres
* `resync_pg_seqs.sh` - run directly (you may have to adjust the user and database
    name) to ensure the primary key sequences match the values in the table.
    If you are getting errors saying new records cannot be inserted with `$table_id = 1`,
    then this should sort it out.
