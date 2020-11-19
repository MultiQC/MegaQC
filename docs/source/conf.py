import os
import sys

import megaqc

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, basedir)


# -- Project information -----------------------------------------------------

project = "MegaQC"
copyright = "2020, MegaQC Team"
author = "MegaQC Team"

version = "megaqc.__version__"

release = "megaqc.__version__"


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

templates_path = ["_templates"]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"

html_static_path = ["_static"]

# Resolve function for the linkcode extension.
def linkcode_resolve(domain, info):
    def find_source():
        # try to find the file and line number, based on code from numpy:
        # https://github.com/numpy/numpy/blob/master/doc/source/conf.py#L286
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
    # tag = 'master' if 'dev' in release else ('v' + release)

    return "https://github.com/ewels/megaqc/blob/%s/%s" % (tag, filename)
