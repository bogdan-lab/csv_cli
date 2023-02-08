from argparse import Namespace
import pytest
from re import error, compile

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


def test_match_all_regex() -> None:
    data = "hello"
    delimiter = ';'
    regex = [compile("^h.*o$")]
    indexes = [0]
    assert csv_regex.match_all_regex(data, delimiter, regex, indexes)

    data = "Hello"
    delimiter = ';'
    regex = [compile("^h.*o$")]
    indexes = [0]
    assert not csv_regex.match_all_regex(data, delimiter, regex, indexes)

    data = "hello;world"
    delimiter = ';'
    regex = [compile("([helo]+)")]
    indexes = [0]
    assert csv_regex.match_all_regex(data, delimiter, regex, indexes)

    data = "hello;world"
    delimiter = ';'
    regex = [compile("([^world])")]
    indexes = [1]
    assert not csv_regex.match_all_regex(data, delimiter, regex, indexes)

    data = "hello;world"
    delimiter = ';'
    regex = [compile("(hello|world)")]*2
    indexes = [0, 1]
    assert csv_regex.match_all_regex(data, delimiter, regex, indexes)

    # test start string literal inside the column
    data = "python;is;the;theBest"
    delimiter = ';'
    regex = [compile("^i")]
    indexes = [1]
    assert csv_regex.match_all_regex(data, delimiter, regex, indexes)

    data = "python;his;the;theBest"
    delimiter = ';'
    regex = [compile("^i")]
    indexes = [1]
    assert not csv_regex.match_all_regex(data, delimiter, regex, indexes)

    # test end string symbol inside the column
    data = "python;his;the;theBest"
    delimiter = ';'
    regex = [compile("e$")]
    indexes = [2]
    assert csv_regex.match_all_regex(data, delimiter, regex, indexes)

    data = "python;his;that;theBest"
    delimiter = ';'
    regex = [compile("e$")]
    indexes = [2]
    assert not csv_regex.match_all_regex(data, delimiter, regex, indexes)

    # test match in several column separated by not interesting columns
    data = "python;his;that;theBest"
    delimiter = ';'
    regex = [compile("B"), compile("[his]{3}"), ]
    indexes = [3, 1]
    assert csv_regex.match_all_regex(data, delimiter, regex, indexes)

    # One of few columns does not match
    data = "python;his;that;theBest"
    delimiter = ';'
    regex = [compile("B"), compile("[his]{4}"), ]
    indexes = [3, 1]
    assert not csv_regex.match_all_regex(data, delimiter, regex, indexes)
