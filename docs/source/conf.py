import os
import sys

import megaqc

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, basedir)


# -- Project information -----------------------------------------------------

project = "MegaQC"
copyright = "2020, MegaQC Team"
author = "MegaQC Team"

version = megaqc.version

release = megaqc.version


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.mathjax",
    "sphinx.ext.linkcode",  # link to github, see linkcode_resolve() below
    "sphinxcontrib.napoleon",
    "sphinx_click",
    "sphinxcontrib.autohttp.flask",
    "sphinxcontrib.autohttp.flaskqref",
]

# Replace the usual index.rst with a custom index.html file
master_doc = "docs/contents"
html_additional_pages = {"index": "index.html"}

templates_path = ["_templates"]

# To prevent duplicate label warnings every *.rst file with multiple labels
# needs to be added to the exclude patterns.
# Reference: https://stackoverflow.com/questions/16262163/sphinxs-include-directive-and-duplicate-label-warnings
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "docs/dev/backend.rst",
    "docs/dev/frontend.rst",
    "docs/installation/installation_dev.rst",
    "docs/installation/installation_docker.rst",
    "docs/installation/installation_prod.rst",
    "docs/installation/migrations.rst",
    "docs/usage/usage_admin.rst",
    "docs/usage/usage_setup.rst",
]

html_theme = "sphinx_rtd_theme"

html_static_path = ["_static"]
html_css_files = [
    "megaqc_style.css",
]

# Resolve function for the linkcode extension.
def linkcode_resolve(domain, info):
    def find_source():
        # try to find the file and line number:
        obj = sys.modules[info["module"]]
        for part in info["fullname"].split("."):
            obj = getattr(obj, part)
        import inspect
        import os

        fn = inspect.getsourcefile(obj)
        fn = os.path.relpath(fn, start=os.path.dirname(megaqc.__file__))
        source, lineno = inspect.getsourcelines(obj)
        return fn, lineno, lineno + len(source) - 1

    if domain != "py" or not info["module"]:
        return None
    try:
        filename = "megaqc/%s#L%d-L%d" % find_source()
    except Exception:
        filename = info["module"].replace(".", "/") + ".py"
    tag = "master"
    # TODO use this after the first release: tag = 'master' if 'dev' in release else ('v' + release)

    return "https://github.com/ewels/megaqc/blob/%s/%s" % (tag, filename)
