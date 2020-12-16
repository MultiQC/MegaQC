Documentation
===============

MegaQC uses `Sphinx <https://www.sphinx-doc.org/en/master/>`_ to build the documentation
and `Github Pages <https://pages.github.com/>`_ to host it.

Building the documentation locally
-------------------------------------

The MegaQC documentation requires

1. An installation of MegaQC to fetch the API endpoints and the Click commands.
2. All dependencies specified in the `docs requirements.txt <https://github.com/ewels/MegaQC/blob/master/docs/requirements.txt>`_.
   Install them by invoking: ``pip install -r docs/requirements.txt``. 

After having installed all requirements run ``make api-docs && make html`` in the ``docs`` directory.
The generated ``html`` files are found in the ``docs/_build/html`` subfolder.
Simply open a generated ``html`` file in your favorite browser to read the documentation.

Publishing the documentation
---------------------------------

On pushes to the ``master`` branch the documentation is automatically built and pushed
to the ``gh-pages`` branch. The static html files on this branch are then deployed
to Github Pages and displayed to the outside world.
All of this is done with the `Publish Docs Github Actions workflow <https://github.com/ewels/MegaQC/blob/master/.github/workflows/publish_docs.yaml>`.
