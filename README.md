# ![MegaQC](https://raw.githubusercontent.com/ewels/MegaQC/master/megaqc/static/img/MegaQC_logo.png)

### A web application to collect and visualise data from multiple MultiQC reports.

[![Docker](https://img.shields.io/docker/automated/ewels/megaqc.svg?style=flat-square)](https://hub.docker.com/r/ewels/megaqc/)
[![Build Status](https://travis-ci.org/ewels/MegaQC.svg?branch=master)](https://travis-ci.org/ewels/MegaQC)
[![Gitter](https://img.shields.io/badge/gitter-%20join%20chat%20%E2%86%92-4fb99a.svg?style=flat-square)](https://gitter.im/ewels/MegaQC)

---

### Current Status: _"Pretty unstable"_

As of mid-October 2017, MegaQC has all basic functionality. We've made the repo public,
but please bear in mind that it is still under heavy development and changes are being
made on a daily basis. It's safe to assume that the database structure is still at risk
and that you shouldn't yet trust it to be stable. However, we'd love your help in testing,
bug finding and development!

---

MegaQC is a web application that you can install and run on your own network.
It collects and visualises data parsed by MultiQC across multiple runs.

Once MegaQC is installed and running, simply configure MultiQC to automatically
save data to the website every time it runs (find instructions in the running
MegaQC website). Users of your group or facility can then replicate
MultiQC plots and explore different data fields. Data distributions, timelines
and comparisons can all be explored.

The MegaQC homepage looks something like this:

![MegaQC homepage](https://raw.githubusercontent.com/ewels/MegaQC/master/docs/images/megaqc_homepage.png)

If you're not sure what MultiQC is yet, check out the main
[MultiQC website](http://multiqc.info) and [GitHub repo](https://github.com/ewels/MultiQC)
first.

## Installation

MegaQC has been written in Python using the [Flask](http://flask.pocoo.org)
web framework. MegaQC is designed to be very simple to get up and running
for basic testing and evaluation, yet super easy to configure for a high
performance production installation.

### Testing MegaQC

By default, MegaQC installs with configuration to use the Flask development
server and a SQLite database. This allows a very simple pure-Python installation
where you can get up and running almost immediately.

**MegaQC is much slower in this testing mode than with a proper production
installation, so don't be too quick to judge it as being slow!**

<!--
You can install MultiQC from [PyPI](https://pypi.python.org/pypi/megaqc/)
using `pip` as follows:
```bash
pip install megaqc
```

Alternatively, you can install using [Conda](http://anaconda.org/)
from the [bioconda channel](https://bioconda.github.io/):
```bash
conda install -c bioconda megaqc
```
-->

If you would like the development version instead, the command is:

```bash
pip install --upgrade --force-reinstall git+https://github.com/ewels/MegaQC.git
```

Once installed, run the server with the following command:

```
megaqc run
```

> #### WARNING!
>
> _The flask server is single-threaded, meaning that only one person can load
> a page or a plot at a time. The SQLite database works using flat files on the
> disk and much slower than fully fledged SQL databases. As such, it should
> **not be used in production** and will run slowly during testing._

### MegaQC in production

Once happy with MegaQC, you can should run it in production will a multi-threaded
server application and high performance database. MegaQC is designed to be simply
run with Postgres SQL and Gunicorn server, however you're not tied to these -
the site is written with SQL-Alchemy and should work with most SQL database types
and Flask works with most server architectures.

MegaQC comes with instructions for how to run an installation for Gunicorn + Apache with
Postgres SQL. It also comes with a Docker container for super-fast setup (note that
all data will be lost if the docker container is stopped by default).

Please see the [docs](docs/) for full instructions for each method.

## Contributions & Support

Contributions and suggestions for new features are welcome, as are bug reports!
Please create a new [issue](https://github.com/ewels/MegaQC/issues) for any
of these, including example reports where possible.

There is a chat room for the package hosted on Gitter where you can discuss
things with the package author and other developers:
https://gitter.im/ewels/MegaQC

If in doubt, feel free to get in touch with the main author directly:
[@ewels](https://github.com/ewels) (phil.ewels@scilifelab.se)

### Contributors

- Project lead and main author: [@ewels](https://github.com/ewels)
- Primary backend developer and database guru: [@Galithil](https://github.com/Galithil)

See all contributors [on GitHub](https://github.com/ewels/MegaQC/graphs/contributors).
