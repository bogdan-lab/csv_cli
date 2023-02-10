from argparse import Namespace
import datetime

from csv_read_write import FileContent
from csv_defaults import *
from utils_for_tests import merge_args, \
    create_default_file_params, \
    create_default_column_selector, \
    create_default_inplace_argument, \
    create_default_hide_header_argument, \
    convert_argparse_action_to_bool, \
    create_file

import csv_sort


def create_default_sort_args() -> Namespace:
    args = merge_args(create_default_file_params(),
                      create_default_column_selector(),
                      create_default_inplace_argument(),
                      create_default_hide_header_argument())
    args.c_type = DEFAULT_COLUMN_TYPE_LIST
    args.time_fmt = DEFAULT_TIME_FORMAT
    args.reverse = convert_argparse_action_to_bool(
        DEFAULT_SORT_REVERSE_ACTION)
    return args


def test_sort_content_numbers():
    header = "One;Two;Three"
    test_file = FileContent(header, ("5;6;7", "1;2;3", "4;2;0"))
    res_file = csv_sort.sort_content(test_file, col_indexes=[0],
                                     col_types=["number"], delimiter=';',
                                     rev_order=False, time_fmt="")
    assert res_file.header == header
    assert res_file.content == ("1;2;3", "4;2;0", "5;6;7")

    res_file = csv_sort.sort_content(test_file, col_indexes=[2],
                                     col_types=["number"], delimiter=';',
                                     rev_order=True, time_fmt="")
    assert res_file.header == header
    assert res_file.content == ("5;6;7", "1;2;3", "4;2;0")


def test_sort_content_strings():
    header = "One;Two;Three"
    test_file = FileContent(header, ("d,  f  ,g", "a,  b  ,c", "w,x,z"))
    res_file = csv_sort.sort_content(test_file, col_indexes=[1],
                                     col_types=["string"], delimiter=',',
                                     rev_order=False, time_fmt="")
    assert res_file.header == header
    assert res_file.content == ("a,  b  ,c", "d,  f  ,g", "w,x,z")


def test_comparator():
    sorter = csv_sort.RowSorter(col_indexes=[2, 0, 4],
                                col_types=['string', 'number', 'time'],
                                delimiter=",", time_fmt=DEFAULT_TIME_FORMAT)
    res = sorter.comparator("1, 3.14, abcd , 0, 2010-01-01 13:48:32")
    assert len(res) == 3
    assert res[0] == "abcd"
    assert res[1] == 1.0
    assert res[2] == datetime.datetime(year=2010, month=1, day=1, hour=13,
                                       minute=48, second=32)


def test_sort_empty_file(tmp_path):
    fpath = tmp_path / "empty.csv"
    fpath.touch()

    args = create_default_sort_args()
    args.files = [fpath]
    args.c_index = [0]
    args.c_type = ['string']
    args.inplace = True

    csv_sort.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.readlines()
    assert len(data) == 0


def test_header_only_file(tmp_path):
    header = "Header1,Header2,Header3"
    fpath = create_file(tmp_path/"empty.csv", (header,))

    args = create_default_sort_args()
    args.delimiter = ","
    args.files = [fpath]
    args.c_name = ["Header1"]
    args.c_type = ['string']
    args.inplace = True

    csv_sort.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == header


def test_sort_file_by_one_column_1(tmp_path):
    r1 = "1;2;3"
    r2 = "2;3;4"
    r3 = "3;4;5"
    r4 = "4;5;6"
    r5 = "5;6;7"
    fpath = create_file(tmp_path / "test.csv", (r4, r5, r3, r1, r2))

    args = create_default_sort_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.no_header = True
    args.c_index = [0]
    args.c_type = ['number']
    args.inplace = True

    csv_sort.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((r1, r2, r3, r4, r5))


def test_sort_file_by_one_column_2(tmp_path):
    header = 'one;two;three'
    r1 = "1;2;a"
    r2 = "2;3;b"
    r3 = "3;4;c"
    r4 = "4;5;d"
    r5 = "5;6;e"
    fpath = create_file(tmp_path / "test.csv", (header, r4, r5, r3, r1, r2))

    args = create_default_sort_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.c_name = ['three']
    args.c_type = ['string']
    args.inplace = True
    args.reverse = True

    csv_sort.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((header, r5, r4, r3, r2, r1))


def test_sort_file_by_one_column_3(tmp_path):
    '''Sorting by time column'''
    header = 'one;two;three'
    r1 = "2010-01-02 13:45:23;2;a"
    r2 = "1993-11-02 23:05:17;3;b"
    r3 = "2015-07-23 08:01:00;4;c"
    r4 = "2001-05-11 00:00:23;5;d"
    r5 = "2011-04-29 17:01:23;6;e"
    fpath = create_file(tmp_path / "test.csv", (header, r4, r5, r3, r1, r2))

    args = create_default_sort_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.c_name = ['one']
    args.c_type = ['time']
    args.inplace = True

    csv_sort.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((header, r2, r4, r1, r5, r3))


def test_sort_file_by_one_column_4(tmp_path):
    '''Sorting by time column with different format'''
    header = 'one;two;three'
    r1 = "2010_01_02;2;a"
    r2 = "1993_11_02;3;b"
    r3 = "2015_07_23;4;c"
    r4 = "2001_05_11;5;d"
    r5 = "2011_04_29;6;e"
    fpath = create_file(tmp_path / "test.csv", (header, r4, r5, r3, r1, r2))

    args = create_default_sort_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.c_name = ['one']
    args.c_type = ['time']
    args.inplace = True
    args.reverse = True
    args.time_fmt = "%Y_%m_%d"

    csv_sort.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((header, r3, r5, r1, r4, r2))


def test_sort_file_without_modification(tmp_path):
    '''Order of rows should be the only thing that is modified'''
    header = '    one;   two   ;three  \t '
    r1 = "   1;  1  ;1   "
    r2 = "   2;  2  ;2   "
    r3 = "   3;  3  ;3   "
    r4 = "   4;  4  ;4   "
    r5 = "   5;  5  ;5   "
    r6 = "   6;  6  ;6   "
    fpath = create_file(tmp_path / "test.csv",
                        (header, r1, r2, r3, r4, r5, r6))

    args = create_default_sort_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.c_name = ['one']
    args.c_type = ['number']
    args.inplace = True
    args.time_fmt = "%Y_%m_%d"

    csv_sort.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((header, r1, r2, r3, r4, r5, r6))
    # sort according to the second column
    args.c_name = ["two"]
    csv_sort.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((header, r1, r2, r3, r4, r5, r6))
    # sort according to the last column
    args.c_name = ["three"]
    csv_sort.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((header, r1, r2, r3, r4, r5, r6))


def test_sort_according_to_several_columns(tmp_path):
    header = 'one;two;three'
    r1 = "1;2;a"
    r2 = "1;3;b"
    r3 = "3;4;c"
    r4 = "2;5;d"
    r5 = "2;6;e"
    fpath = create_file(tmp_path / "test.csv", (header, r4, r5, r3, r1, r2))

    args = create_default_sort_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.c_name = ['one', 'three']
    args.c_type = ['number', 'string']
    args.inplace = True
    args.reverse = True

    csv_sort.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((header, r3, r5, r4, r2, r1))


def test_check_arguments_sort():
    '''If no types were passed we want to automatically assume
    that all column types are numeric'''

    args = create_default_sort_args()
    args.c_index = [1]

    csv_sort.check_arguments(args)
    assert len(args.c_type) == len(args.c_index)
    assert all(el == csv_sort.ColumnType.NUMBER.value for el in args.c_type)

    args.c_index = [5, 4, 3]
    args.c_type = []
    csv_sort.check_arguments(args)
    assert len(args.c_type) == len(args.c_index)
    assert all(el == csv_sort.ColumnType.NUMBER.value for el in args.c_type)

    args.c_index = None
    args.c_name = ["one"]
    args.c_type = None
    csv_sort.check_arguments(args)
    assert len(args.c_type) == len(args.c_name)
    assert all(el == csv_sort.ColumnType.NUMBER.value for el in args.c_type)

    args.c_name = ["one", "two"]
    args.c_type = []
    csv_sort.check_arguments(args)
    assert len(args.c_type) == len(args.c_name)
    assert all(el == csv_sort.ColumnType.NUMBER.value for el in args.c_type)


def test_sort_according_to_the_column_with_nan(tmp_path):
    r1 = "4.5;one"
    r2 = "nan;first"
    r3 = "-1.0;two"
    r4 = "7.9;big"
    r5 = "nan;last"
    fpath = create_file(tmp_path / "test.csv", (r1, r2, r3, r4, r5))

    args = create_default_sort_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.no_header = True
    args.c_index = [0]
    args.c_type = ["number"]
    args.inplace = True
    csv_sort.callback_sort(args)

    with open(fpath, 'r') as fin:
        data = fin.read()

    assert data == '\n'.join((r3, r1, r4, r2, r5))


def test_sort_when_conversion_fails_1(tmp_path):
    r1 = "5; a"
    r2 = "-; b"
    r3 = "; d"
    r4 = "0; v"
    r5 = "nan; and"
    r6 = "definitely not a number; num"
    fpath = create_file(tmp_path / "test.csv", (r1, r2, r3, r4, r5, r6))

    args = create_default_sort_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.no_header = True
    args.c_index = [0]
    args.c_type = ["number"]
    args.inplace = True

    csv_sort.callback_sort(args)

    with open(fpath, 'r') as fin:
        data = fin.read()

    assert data == '\n'.join((r4, r1, r2, r3, r5, r6))


def test_sort_when_conversion_fails_2(tmp_path):
    r1 = "2010-01-01; a"
    r2 = "-; b"
    r3 = "; d"
    r4 = "2008-09-12; v"
    r5 = "nan; and"
    r6 = "definitely not a number; num"
    fpath = create_file(tmp_path / "test.csv", (r1, r2, r3, r4, r5, r6))

    args = create_default_sort_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.no_header = True
    args.c_index = [0]
    args.c_type = ["time"]
    args.inplace = True
    args.time_fmt = "%Y-%m-%d"

    csv_sort.callback_sort(args)

    with open(fpath, 'r') as fin:
        data = fin.read()

    assert data == '\n'.join((r4, r1, r2, r3, r5, r6))


def test_sort_by_string_with_empty_strings(tmp_path):
    header = 'one;two;three'
    r1 = "1;2;b"
    r2 = "1;3;-"
    r3 = "3;4;"
    r4 = "2;5;d"
    r5 = "2;6;"
    fpath = create_file(tmp_path/"test.csv", (header, r1, r2, r3, r4, r5))

    args = create_default_sort_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.c_name = ['three']
    args.c_type = ['string']
    args.inplace = True

    csv_sort.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((header, r3, r5, r2, r1, r4))


def test_sort_single_number_column(tmp_path):
    values = (5, 6, 1, 18, 25)
    fpath = create_file(tmp_path / "test.csv", (str(el) for el in values))

    args = create_default_sort_args()
    args.delimiter = ","
    args.files = [fpath]
    args.no_header = True
    args.c_index = [0]
    args.c_type = ["number"]
    args.inplace = True

    csv_sort.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()

    assert data == '\n'.join((str(el) for el in sorted(values)))


def test_sort_single_string_column(tmp_path):
    values = ("one", "two", "abcd", "eleven", "building")
    fpath = create_file(tmp_path / "test.csv", values)

    args = create_default_sort_args()
    args.delimiter = "DELIMITER"
    args.files = [fpath]
    args.no_header = True
    args.c_index = [0]
    args.c_type = ["string"]
    args.inplace = True
    args.reverse = True

    csv_sort.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()

    assert data == '\n'.join(reversed(sorted(values)))


def test_sort_single_time_column(tmp_path):
    values = ("HEADER", "2001-12-15", "1990-03-05", "2010-11-01", "1980-01-01")
    fpath = create_file(tmp_path / "test.csv", values)

    args = create_default_sort_args()
    args.delimiter = "DELIMITER"
    args.files = [fpath]
    args.c_index = [0]
    args.c_type = ["string"]
    args.inplace = True
    args.time_fmt = "%Y-%m-%d"

    csv_sort.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()

    expected = ("HEADER", "1980-01-01", "1990-03-05",
                "2001-12-15", "2010-11-01")
    assert data == '\n'.join(expected)


def test_sort_stability_when_multiple_sort(tmp_path):
    header = "Date;String;Int;Double"
    r1 = "2010-01-04;two;1;5.0"
    r2 = "2011-05-23;one;2;4.5"
    r3 = "2008-03-12;two;-14;3.7"
    r4 = "2016-12-07;one;-4;0.1"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4))

    args = create_default_sort_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.c_name = ["String", "Int"]
    args.c_type = ["string", "number"]
    args.inplace = True
    args.reverse = True
    args.time_fmt = "%Y-%m-%d"

    csv_sort.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()

    assert data == '\n'.join((header, r1, r3, r2, r4))


def test_hide_header_option(tmp_path, capsys) -> None:
    # with header
    header = "One;Two;Three"
    r1 = "1;1;1"
    r2 = "2;2;2"
    r3 = "3;3;3"
    r4 = "4;4;4"
    fpath = create_file(tmp_path / "test.csv", (header, r4, r2, r3, r1))

    args = create_default_sort_args()
    args.files = [fpath]
    args.delimiter = ';'
    args.c_index = [0]
    args.c_type = ['number']
    args.hide_header = True

    csv_sort.callback_sort(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r2, r3, r4))

    # if we modify inplace hide_header is ignored
    args.inplace = True
    csv_sort.callback_sort(args)
    with open(fpath, 'r') as f_input:
        lines = list(el.strip() for el in f_input)
        assert lines == [header, r1, r2, r3, r4]

    # case with no header
    fpath = create_file(tmp_path / "test_2.csv", (r2, r4, r3, r1))
    args.no_header = True
    args.inplace = False
    args.files = [fpath]
    csv_sort.callback_sort(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r2, r3, r4))
