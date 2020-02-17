"""
Utilities to help with content negotiation.
"""
import csv
from io import StringIO


def flatten_dicts(dictionary, delim=".", _path=None):
    """
    Flattens a nested JSON dictionary into a flat dictionary, but does NOT
    flatten any lists in the structure.

    :param dictionary: Dictionary to flatten
    :param delim: The delimiter for nested fields
    """
    flattened = {}
    prefix = _path + delim if _path else ""
    for key, value in dictionary.items():
        if isinstance(value, dict):
            flattened.update(flatten_dicts(value, _path=prefix + key))

        else:
            flattened[prefix + key] = value

    return flattened


def json_to_csv(json, **writer_opts):
    # CSVs with one item are treated as lists of 1 element
    if not isinstance(json, list):
        json = [json]

    # Calculate the fieldnames
    fields = set()
    for row in json:
        flattened = flatten_dicts(row, delim="\t")
        # flattened = flatten_preserve_lists(row, max_depth=2)
        fields.update(flattened.keys())

    # Write the CSV
    with StringIO() as fp:
        writer = csv.DictWriter(fp, fieldnames=fields, **writer_opts)
        writer.writeheader()
        for row in json:
            flattened = flatten_dicts(row, delim="\t")
            writer.writerow(flattened)

        return fp.getvalue()
