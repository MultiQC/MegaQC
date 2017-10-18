# ![MegaQC](https://raw.githubusercontent.com/ewels/MegaQC/master/logo/MegaQC_logo.png)

### A web application to collect and visualise data from multiple MultiQC reports.

[![Docker](https://img.shields.io/docker/automated/ewels/megaqc.svg?style=flat-square)](https://hub.docker.com/r/ewels/megaqc/)
[![Build Status](https://img.shields.io/travis/ewels/megaqc.svg?style=flat-square)](https://travis-ci.org/ewels/megaqc)

[![Gitter](https://img.shields.io/badge/gitter-%20join%20chat%20%E2%86%92-4fb99a.svg?style=flat-square)](https://gitter.im/ewels/MultiQC)

-----

MegaQC is a Flask web application that lets you easily set up a MegaQC
website for your group or facility.

Once running, simply configure MultiQC configured to automatically save data to the
website every time it runs. This is saved to a database and can be explored on the
MegaQC website, allowing visualisation of long-term trends.

## Installation
MegaQC has been written in such a way that it is hopefully very simple to get
up and running for basic testing, yet easy to configure for a high performance
production installation.


### Testing MegaQC
By default, MegaQC installs with configuration to use the Flask development
server and a SQLite database. This allows a very simple pure-Python installation
where you can get up and running almost immediately.

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

### MegaQC in production
Once happy with MegaQC, you can should run it in production will a multi-threaded
server application and high performance database. MegaQC is designed to be simply
run with Postgres SQL and Gunicorn server, though it is written with SQL-Alchemy
so should work with most SQL database types.

MegaQC comes with instructions for how to install and setup Gunicorn+Apache with
Postgres SQL. It also comes with a Docker container, though note that all data will
be lost if the docker container is stopped.

Please see the [docs](docs/) for full instructions for each method.


## Contributions & Support

Contributions and suggestions for new features are welcome, as are bug reports!
Please create a new [issue](https://github.com/ewels/MegaQC/issues) for any
of these, including example reports where possible.

There is a chat room for the package hosted on Gitter where you can discuss
things with the package author and other developers:
https://gitter.im/ewels/MultiQC

If in doubt, feel free to get in touch with the author directly:
[@ewels](https://github.com/ewels) (phil.ewels@scilifelab.se)

### Contributors
Project lead and main author: [@ewels](https://github.com/ewels)
Primary backend developer and database guru: [@Galithil](https://github.com/Galithil)

<!--
Code contributions from:
[@one](https://github.com/one),
[@two](https://github.com/two),
-->
