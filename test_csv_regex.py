from argparse import Namespace
import pytest
from re import error

import csv_regex

from utils_for_tests import merge_args, \
    create_default_file_params, \
    create_default_column_selector, \
    create_file
from csv_defaults import *


def create_default_regex_args() -> Namespace:
    args = merge_args(create_default_file_params(),
                      create_default_column_selector())
    args.expression = DEFAULT_REGEX_EXPRESSION
    return args


def test_check_invalid_expressions() -> None:
    # single regex and it is the wrong one
    with pytest.raises(error):
        csv_regex.check_for_invalid_regex(["[a,b"])
    # two regex and both are wrong
    with pytest.raises(error):
        csv_regex.check_for_invalid_regex(["[a, b", "c, d]"])
    # two regex and only one of them is wrong
    with pytest.raises(error):
        csv_regex.check_for_invalid_regex(["[a-z]", "c(d"])


def test_check_arguments() -> None:
    # No default search is preferred
    args = create_default_regex_args()
    with pytest.raises(ValueError):
        csv_regex.check_arguments(args)
    # empty regex are forbidden
    args.expression = [""]
    args.c_index = [0]
    with pytest.raises(ValueError):
        csv_regex.check_arguments(args)
    args.expression = ["[a-z]", ""]
    args.c_index = [0, 1]
    with pytest.raises(ValueError):
        csv_regex.check_arguments(args)
