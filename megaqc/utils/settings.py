#!/usr/bin/env python
"""
MegaQC config module.
"""

from __future__ import print_function

import collections
import inspect
import io
import logging
import os
import subprocess

import pkg_resources

import megaqc
import yaml

logger = logging.getLogger(__name__)

# Get the MegaQC version
version = pkg_resources.get_distribution("megaqc").version
short_version = pkg_resources.get_distribution("megaqc").version
script_path = os.path.dirname(os.path.realpath(__file__))
git_hash = None
git_hash_short = None
try:
    git_hash = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=script_path,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    git_hash_short = git_hash[:7]
    version = "{} ({})".format(version, git_hash_short)
except:
    pass

# Constants
MEGAQC_DIR = os.path.dirname(os.path.realpath(inspect.getfile(megaqc)))

##### MegaQC script defaults
# Default MegaQC config
searchp_fn = os.path.join(MEGAQC_DIR, "utils", "config_defaults.yaml")
with io.open(searchp_fn) as f:
    configs = yaml.load(f)
    for c, v in list(configs.items()):
        globals()[c] = v

##### Functions to load user config files. These are called by the main MegaQC script.
# Note that config files are loaded in a specific order and values can overwrite each other.
def mqc_load_userconfig(paths=()):
    """
    Overwrite config defaults with user config files.
    """

    # Load and parse installation config file if we find it
    mqc_load_config(os.path.join(os.path.dirname(MEGAQC_DIR), "megaqc_config.yaml"))

    # Load and parse a user config file if we find it
    mqc_load_config(os.path.expanduser("~/.megaqc_config.yaml"))

    # Load and parse a config file path set in an ENV variable if we find it
    if os.environ.get("MEGAQC_CONFIG_PATH") is not None:
        mqc_load_config(os.environ.get("MEGAQC_CONFIG_PATH"))

    # Load and parse a config file in this working directory if we find it
    mqc_load_config("megaqc_config.yaml")

    # Custom command line config
    for p in paths:
        mqc_load_config(p)


def mqc_load_config(yaml_config):
    """
    Load and parse a config file if we find it.
    """
    if os.path.isfile(yaml_config):
        try:
            with io.open(yaml_config) as f:
                new_config = yaml.load(f)
                logger.debug("Loading config settings from: {}".format(yaml_config))
                mqc_add_config(new_config, yaml_config)
        except (IOError, AttributeError) as e:
            logger.debug("Config error: {}".format(e))
        except yaml.scanner.ScannerError as e:
            logger.error("Error parsing config YAML: {}".format(e))
    else:
        logger.debug("No MegaQC config found: {}".format(yaml_config))


def mqc_cl_config(cl_config):
    for clc_str in cl_config:
        try:
            parsed_clc = yaml.load(clc_str)
            # something:var fails as it needs a space. Fix this (a common mistake)
            if isinstance(parsed_clc, str) and ":" in clc_str:
                clc_str = ": ".join(clc_str.split(":"))
                parsed_clc = yaml.load(clc_str)
            assert isinstance(parsed_clc, dict)
        except yaml.scanner.ScannerError as e:
            logger.error(
                "Could not parse command line config: {}\n{}".format(clc_str, e)
            )
        except AssertionError:
            logger.error("Could not parse command line config: {}".format(clc_str))
        else:
            logger.debug("Found command line config: {}".format(parsed_clc))
            mqc_add_config(parsed_clc)


def mqc_add_config(conf, conf_path=None):
    """
    Add to the global config with given MegaQC config dict.
    """
    global fn_clean_exts, fn_clean_trim
    for c, v in list(conf.items()):
        logger.debug("New config '{}': {}".format(c, v))
        update_dict(globals(), {c: v})


def update_dict(d, u):
    """
    Recursively updates nested dict d from nested dict u.
    """
    for key, val in list(u.items()):
        if isinstance(val, collections.Mapping):
            d[key] = update_dict(d.get(key, {}), val)
        else:
            d[key] = u[key]
    return d
