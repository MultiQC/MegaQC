|MegaQC|

A web application to collect and visualise data from multiple MultiQC reports.

|Docker| |Build Status| |Gitter| |Documentation| |PyPI|

Current Status: *“Pretty unstable”*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As of mid-October 2017, MegaQC has all basic functionality. We’ve made
the repository public, but please bear in mind that it is still under heavy
development and changes are being made on a daily basis. It’s safe to
assume that the database structure is still at risk and that you
shouldn’t yet trust it to be stable. However, we’d love your help in
testing, bug finding and development!

--------------

MegaQC is a web application that you can install and run on your own
network. It collects and visualises data parsed by MultiQC across multiple runs.
The MegaQC home page looks something like this:

.. figure:: https://raw.githubusercontent.com/ewels/MegaQC/master/docs/source/images/megaqc_homepage.png
   :alt: MegaQC homepage

   Screenshot of the MegaQC home page.

If you are not sure what MultiQC is yet, check out the main `MultiQC
website`_ and `GitHub repository`_ first. Once MegaQC is installed and running,
simply configure MultiQC to automatically save data to the website every time it runs.
Users of your group or facility can then replicate MultiQC plots and explore different data
fields. Data distributions, timelines and comparisons can all be explored.

Please read the `MegaQC Documentation <https://megaqc.info/docs/index.html>`_
to learn how to install, deploy and use MegaQC.

.. _MultiQC website: http://multiqc.info
.. _GitHub repository: https://github.com/ewels/MultiQC

.. |MegaQC| image:: https://raw.githubusercontent.com/ewels/MegaQC/master/megaqc/static/img/MegaQC_logo.png
.. |Docker| image:: https://img.shields.io/docker/automated/ewels/megaqc.svg?style=flat-square
   :target: https://hub.docker.com/r/ewels/megaqc/
.. |Build Status| image:: https://travis-ci.org/ewels/MegaQC.svg?branch=master
   :target: https://travis-ci.org/ewels/MegaQC
.. |Gitter| image:: https://img.shields.io/badge/gitter-%20join%20chat%20%E2%86%92-4fb99a.svg?style=flat-square
   :target: https://gitter.im/ewels/MegaQC
.. |Documentation| image:: https://img.shields.io/badge/Documentation-passing-passing
   :target: https://ewels.github.io/MegaQC/docs/contents.html
.. |PyPI| image:: https://img.shields.io/pypi/v/megaqc?color=passing
   :target: https://pypi.org/project/megaqc/
