from argparse import Namespace
import pytest
from re import error, compile

import csv_regex

from utils_for_tests import merge_args, \
    create_default_file_params, \
    create_default_column_selector, \
    create_default_inplace_argument, \
    create_default_hide_header_argument, \
    convert_argparser_action_to_bool, \
    create_file
from csv_defaults import *


def create_default_regex_args() -> Namespace:
    args = merge_args(create_default_file_params(),
                      create_default_column_selector(),
                      create_default_inplace_argument(),
                      create_default_hide_header_argument())
    args.expression = DEFAULT_REGEX_EXPRESSION
    args.ignore_case = convert_argparser_action_to_bool(
        DEFAULT_REGEX_IGNORE_CASE_ACTION)
    return args


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


def test_empty_file_no_header(tmp_path, capsys) -> None:
    fpath = tmp_path / "empty.csv"
    fpath.touch()

    args = create_default_regex_args()
    args.files = [fpath]
    args.delimiter = ";"
    args.no_header = True
    args.c_index = [0]
    args.expression = ["(.*)"]

    csv_regex.callback_regex(args)
    out = capsys.readouterr().out
    assert out == '\n'


def test_empty_file_with(tmp_path, capsys) -> None:
    header = "one,two,three"
    fpath = create_file(tmp_path / "test.csv", (header,))

    args = create_default_regex_args()
    args.files = [fpath]
    args.delimiter = ","
    args.c_index = [0]
    args.expression = ["(.*)"]

    csv_regex.callback_regex(args)
    out = capsys.readouterr().out
    assert out[:-1] == header


def test_regex_in_out_of_bounds_column(tmp_path) -> None:
    header = "one, two, three"
    r1 = "1, 2, 3"
    r2 = "10, 20, 30"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2))

    args = create_default_regex_args()
    args.files = [fpath]
    args.delimiter = ","
    args.expression = ["(.*)"]
    args.c_index = [3]

    with pytest.raises(ValueError):
        csv_regex.callback_regex(args)


def test_regex_in_column_which_does_not_exist(tmp_path) -> None:
    header = "one, two, three"
    r1 = "1, 2, 3"
    r2 = "10, 20, 30"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2))

    args = create_default_regex_args()
    args.files = [fpath]
    args.delimiter = ","
    args.expression = ["(.*)"]
    args.c_name = ["four"]

    with pytest.raises(ValueError):
        csv_regex.callback_regex(args)


def test_select_from_table_with_single_column(tmp_path, capsys) -> None:
    header = "Header"
    r1 = "one"
    r2 = "two"
    r3 = "three"
    r4 = "four"
    r5 = "five"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4, r5))

    args = create_default_regex_args()
    args.files = [fpath]
    args.delimiter = ","
    args.c_index = [0]
    args.expression = ["e$"]

    csv_regex.callback_regex(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r3, r5))


def test_select_none_of_content(tmp_path, capsys) -> None:
    header = "ONE;TWO"
    r1 = "1;2"
    r2 = "11;22"
    r3 = "111;222"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3))

    args = create_default_regex_args()
    args.files = [fpath]
    args.delimiter = ';'
    args.c_name = ["TWO"]
    args.expression = ["[a-z]+"]

    csv_regex.callback_regex(args)
    out = capsys.readouterr().out
    assert out[:-1] == header


def test_select_all_lines(tmp_path, capsys) -> None:
    r1 = "1;2"
    r2 = "11;22"
    r3 = "111;222"
    fpath = create_file(tmp_path / "test.csv", (r1, r2, r3))

    args = create_default_regex_args()
    args.files = [fpath]
    args.delimiter = ';'
    args.c_index = [1]
    args.expression = ["[1-9]+"]
    args.no_header = True

    csv_regex.callback_regex(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r2, r3))


def test_select_some_of_lines(tmp_path, capsys) -> None:
    header = "String|Date|Number"
    r1 = "one|2001-01-01|123"
    r2 = "two|2002-01-01|456"
    r3 = "his|2003-12-11|39"
    r4 = "four|1995-07-05|8"
    r5 = "DNA|1970-01-01|11"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4, r5))

    args = create_default_regex_args()
    args.files = [fpath]
    args.delimiter = '|'
    args.c_index = [2, 0, 1]
    args.expression = ["^[123]+$", "[a-zA-Z]{3}", "01-01$"]

    csv_regex.callback_regex(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r5))


def test_select_some_of_line_with_ignored_column(tmp_path, capsys) -> None:
    header = "String|Date|Number"
    r1 = "one|2001-01-01|123"
    r2 = "two|2002-01-01|456"
    r3 = "three|2003-12-11|39"
    r4 = "four|1995-07-05|8"
    r5 = "five|1970-01-01|11"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4, r5))

    args = create_default_regex_args()
    args.files = [fpath]
    args.delimiter = "|"
    args.c_name = ["Number", "String"]
    args.expression = ["^1", "e$"]

    csv_regex.callback_regex(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r5))


def test_check_inplace_flag(tmp_path) -> None:
    header = "String;Date"
    r1 = "Q1; 2001-01-01"
    r2 = "Q2; 2001-04-01"
    r3 = "Q3; 2001-07-01"
    r4 = "Q4; 2001-10-01"
    r5 = "Q1; 2002-01-01"
    r6 = "Q2; 2002-04-01"
    r7 = "Q3; 2002-07-01"
    r8 = "Q4; 2002-10-01"
    fpath = create_file(tmp_path/"test.csv",
                        (header, r1, r2, r3, r4, r5, r6, r7, r8))

    args = create_default_regex_args()
    args.files = [fpath]
    args.delimiter = ';'
    args.c_index = [0]
    args.expression = ["(Q1|Q3)"]
    args.inplace = True

    csv_regex.callback_regex(args)
    with open(fpath) as f_input:
        lines = list(el.strip() for el in f_input.readlines())
        assert lines == [header, r1, r3, r5, r7]


def test_hide_header_flag(tmp_path, capsys) -> None:
    # with header
    header = "String;Date"
    r1 = "Q1; 2001-01-01"
    r2 = "Q2; 2001-04-01"
    r3 = "Q3; 2001-07-01"
    r4 = "Q4; 2001-10-01"
    r5 = "Q1; 2002-01-01"
    r6 = "Q2; 2002-04-01"
    r7 = "Q3; 2002-07-01"
    r8 = "Q4; 2002-10-01"
    fpath = create_file(tmp_path / "test.csv",
                        (header, r1, r2, r3, r4, r5, r6, r7, r8))

    args = create_default_regex_args()
    args.files = [fpath]
    args.delimiter = ';'
    args.c_index = [0]
    args.expression = ["4"]
    args.hide_header = True

    csv_regex.callback_regex(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r4, r8))

    # if table modified inplace header is not deleted
    args.inplace = True
    args.expression = ["3"]
    csv_regex.callback_regex(args)
    with open(fpath) as f_input:
        lines = list(el.strip() for el in f_input)
        assert lines == [header, r3, r7]

    # no header
    fpath = create_file(tmp_path / "test.csv",
                        (r1, r2, r3, r4, r5, r6, r7, r8))
    args.no_header = True
    args.inplace = False
    args.expression = ["2"]
    csv_regex.callback_regex(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r2, r6))


def test_regex_selection_with_ignorecase_flag(tmp_path, capsys) -> None:
    r1 = "one, two, three"
    r2 = "twelve, fourteen, sixteen"
    r3 = "eleven, twenty, forty five"
    r4 = "TWENTY ONE, SEVENTEEN, ELEVEN"
    r5 = "thirty five, ten, one hundred"
    r6 = "FiFtY OnE, twenty five, thirty"
    fpath = create_file(tmp_path / "test.csv", (r1, r2, r3, r4, r5, r6))

    args = create_default_regex_args()
    args.files = [fpath]
    args.delimiter = ','
    args.c_index = [0]
    args.expression = ["one"]
    args.ignore_case = True
    args.no_header = True

    csv_regex.callback_regex(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r4, r6))


def test_raise_error_for_invalid_regex(tmp_path) -> None:
    r1 = "1;2"
    r2 = "11;22"
    r3 = "111;222"
    fpath = create_file(tmp_path / "test.csv", (r1, r2, r3))

    args = create_default_regex_args()
    args.files = [fpath]
    args.delimiter = ';'
    # single regex and it is incorrect
    args.c_index = [0]
    args.expression = ["[ab"]
    with pytest.raises(error):
        csv_regex.callback_regex(args)
    # both are incorrect
    args.c_index = [0, 1]
    args.expression = ["[a, b", "c, d]"]
    with pytest.raises(error):
        csv_regex.callback_regex(args)
    # two regex and only one of them is wrong
    args.expression = ["[a-z]", "c(d"]
    with pytest.raises(error):
        csv_regex.callback_regex(args)
    # empty string is incorrect regex too
    args.expression = [""]
    args.c_index = [0]
    with pytest.raises(ValueError):
        csv_regex.callback_regex(args)
