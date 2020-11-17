# MegaQC Installation: Testing

By default, MegaQC installs with configuration to use the Flask development
server and a SQLite database. This allows a very simple pure-Python installation
where you can get up and running almost immediately.

> #### WARNING!
>
> _The flask server is single-threaded, meaning that only one person can load
> a page or a plot at a time. The SQLite database works using flat files on the
> disk and much slower than fully fledged SQL databases. As such, it should
> **not be used in production** and will run slowly during testing._

## 1. Install the MegaQC package

MegaQC is available on both the Python Package Index (PyPI) and conda (bioconda channel).
To install using PyPI, run the following command:

```bash
pip install megaqc
```

To install with conda:

```bash
conda install -c bioconda megaqc
```

## 2. Set up the database

Running this command creates an empty SQLite MegaQC database file in the
installation directory called `megaqc.db`

```bash
megaqc initdb
```

## 3. Load test data

In order to develop new features you need some data to test it with:

```bash
git clone https://github.com/TMiguelT/1000gFastqc
for report in $(find 1000gFastqc -name '*.json')
    do megaqc upload $report
done
```

## 4. Start megaqc

```bash
megaqc run
```

You should now have a fully functional MegaQC test server running,
accessible on your localhost at http://127.0.0.1:5000
