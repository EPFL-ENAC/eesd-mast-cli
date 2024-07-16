import json
import re
import sys
import pandas as pd
from numbers import Number
from math import isnan

#
# Print functions
#

def print_output(res, format, pretty = True):
    """Print the output"""
    if format == "csv":
        pd.DataFrame(res).to_csv(sys.stdout, index=False, sep=",", quotechar='"')
    elif format == "tsv":
        pd.DataFrame(res).to_csv(sys.stdout, index=False, sep="\t", quotechar='"')
    else:
        print_json(res, pretty)

def print_json(res, pretty = True):
    """Print the JSON response"""
    if pretty:
        print(json.dumps(res, sort_keys=True, indent=4))
    else:
        print(json.dumps(res))

#
# Excel cell values cleanup functions
#

def value_cleanup(x):
    """Clean a value of unknown type"""
    rval = x
    if isinstance(x, Number) and isnan(x):
        rval = None
    if isinstance(x, str):
        rval = x.strip()
        if rval == "-":
            rval = None
    return str(rval) if rval is not None else None

def number_cleanup(x):
    """Clean a number value"""
    rval = x
    if not isinstance(x, Number) or isnan(x):
        rval = None
    return rval

def array_formatter(x):
    """Format an array value: split string value when necessary, ensure singletons are in a list"""
    if isinstance(x, Number) and isnan(x):
        return None
    if isinstance(x, str):
        x = x.strip()
        x = re.split(r"\n|/", x)
    return x if isinstance(x, list) else [x]

def yesno_cleanup(x):
    """Clean a yes/no value to boolean"""
    return x != None and x != "No"

def string_cleanup(x):
    """Clean a string value"""
    return x if isinstance(x, str) else None