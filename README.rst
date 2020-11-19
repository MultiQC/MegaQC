|MegaQC|

A web application to collect and visualise data from multiple MultiQC reports.
-------------------------------------------------------------------------------

|Docker| |Build Status| |Gitter|

Current Status: *“Pretty unstable”*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As of mid-October 2017, MegaQC has all basic functionality. We’ve made
the repo public, but please bear in mind that it is still under heavy
development and changes are being made on a daily basis. It’s safe to
assume that the database structure is still at risk and that you
shouldn’t yet trust it to be stable. However, we’d love your help in
testing, bug finding and development!

--------------

MegaQC is a web application that you can install and run on your own
network. It collects and visualises data parsed by MultiQC across
multiple runs.

Once MegaQC is installed and running, simply configure MultiQC to
automatically save data to the website every time it runs (find
instructions in the running MegaQC website). Users of your group or
facility can then replicate MultiQC plots and explore different data
fields. Data distributions, timelines and comparisons can all be
explored.

The MegaQC homepage looks something like this:

.. figure:: https://raw.githubusercontent.com/ewels/MegaQC/master/docs/images/megaqc_homepage.png
   :alt: MegaQC homepage

   MegaQC homepage

If you’re not sure what MultiQC is yet, check out the main `MultiQC
website`_ and `GitHub repo`_ first.

Installation
------------

MegaQC has been written in Python using the `Flask`_ web framework.
MegaQC is designed to be very simple to get up and running for basic
testing and evaluation, yet super easy to configure for a high
performance production installation.

Testing MegaQC
~~~~~~~~~~~~~~

By default, MegaQC installs with configuration to use the Flask
development server and a SQLite database. This allows a very simple
pure-Python installation where you can get up and running almost
immediately.

**MegaQC is much slower in this testing mode than with a proper
production installation, so don’t be too quick to judge it as being
slow!**

.. raw:: html

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

.. code:: bash

   pip install --upgrade --force-reinstall git+https://github.com/ewels/MegaQC.git

Once installed, run the server with the following command:

\`\ ``megaqc run``

.. _MultiQC website: http://multiqc.info
.. _GitHub repo: https://github.com/ewels/MultiQC
.. _Flask: http://flask.pocoo.org

.. |MegaQC| image:: https://raw.githubusercontent.com/ewels/MegaQC/master/megaqc/static/img/MegaQC_logo.png
.. |Docker| image:: https://img.shields.io/docker/automated/ewels/megaqc.svg?style=flat-square
   :target: https://hub.docker.com/r/ewels/megaqc/
.. |Build Status| image:: https://travis-ci.org/ewels/MegaQC.svg?branch=master
   :target: https://travis-ci.org/ewels/MegaQC
.. |Gitter| image:: https://img.shields.io/badge/gitter-%20join%20chat%20%E2%86%92-4fb99a.svg?style=flat-square
   :target: https://gitter.im/ewels/MegaQC