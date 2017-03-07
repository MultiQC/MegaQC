# MultiQC_DB Installation: Development

If doing development work with MultiQC_DB, we recommend following a
slightly different installation procedure. The instructions below will
set up a lightweight installation with example data and lots of debugging help.

It is not suitable for a production environment. If you want to run
MultiQC_DB for your group, see the [production installation](installation-dev.md)
instructions instead.

### 1) Grab the code
Pull the latest development code from GitHub (modify the URL if using
your own forked version) and install the required packages:

```bash
git clone https://github.com/ewels/MultiQC_DB
cd MultiQC_DB
pip install -r requirements/dev.txt
```

The code on GitHub doesn't include any of the front-end packages, so
you need to fetch them using `npm` and `bower`:

```bash
npm install
bower install
```

### 2) Database setup
MultiQC_DB can work with any SQL database, but for development it's probably
simplest to use SQLite, which uses flat files and doesn't require any
background services.

If using SQLite, you don't need to do any setup, as the MultiQC_DB code
will create everything it needs.

### 3) MultiQC_DB configuration
Next, you need a few environment variables to tell Flask how to run the
server. Add the following to `.bashrc` or `.bash_profile`:

```bash
export MULTIQC_DB_SECRET='[ SOMETHING REALLY SECRET ]'
export FLASK_APP='/path/to/MultiQC_DB/multiqc_db/app.py'
export FLASK_DEBUG=1
```

Finally, initialise and update the MultiQC_DB database:

```bash
flask db init
flask db migrate
flask db upgrade
```

### 4) Running MultiQC
Once everything is installed and configured, you can run the `flask` server
application to launch the MultiQC_DB website. 

```bash
flask run
```

This should give some log messages, including the address where the website
can be viewed in the browser.


## Shell
To open the interactive shell, run:

```bash
flask shell
```

By default, you will have access to the flask `app`.


## Running Tests
To run all tests, run:

```bash
flask test
```

Note that the main GitHub repository will run tests using Travis every time
a commit or Pull Request is submitted. Travis can also be enabled on forked
repositories and should work automatically with the bundled `.travis.yml` file.

## Migrations
Whenever a database migration needs to be made. Run the following commands:

```bash
flask db migrate
```

This will generate a new migration script. Then run:

```bash
flask db upgrade
```

To apply the migration.

For a full migration command reference, run `flask db --help`.
