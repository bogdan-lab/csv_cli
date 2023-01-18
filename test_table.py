import table
from argparse import Namespace
import datetime
from pathlib import Path
from typing import Iterable


def create_file(file_path: Path, content: Iterable) -> Path:
    '''Creates file in file_path, fills it iwth a content
    and returns the path to the filled file'''
    file_path.touch()
    with open(file_path, 'w') as fout:
        fout.write('\n'.join(content))
    return file_path


def convert_argparser_action_to_bool(action: str) -> bool:
    return not action == "store_true"


def create_default_file_params() -> Namespace():
    args = Namespace()
    args.delimiter = table.DEFAULT_TABLE_DELIMITER
    args.no_header = convert_argparser_action_to_bool(
        table.DEFAULT_NO_HEADER_ACTION)
    return args


def create_default_column_selector() -> Namespace():
    args = Namespace()
    args.c_name = table.DEFAULT_COLUMN_NAME_LIST
    args.c_index = table.DEFAULT_COLUMN_INDEX_LIST
    return args


def create_default_inplace_argument() -> Namespace:
    args = Namespace()
    args.inplace = convert_argparser_action_to_bool(
        table.DEFAULT_INPLACE_ACTION)
    return args


def merge_args(*seq) -> Namespace:
    total = {}
    for val in seq:
        total.update(vars(val))
    return Namespace(**total)


def create_default_sort_args() -> Namespace:
    args = merge_args(create_default_file_params(),
                      create_default_column_selector(),
                      create_default_inplace_argument())
    args.c_type = table.DEFAULT_COLUMN_TYPE_LIST
    args.time_fmt = table.DEFAULT_TIME_FORMAT
    args.reverse = convert_argparser_action_to_bool(
        table.DEFAULT_SORT_REVERSE_ACTION)
    return args


def create_default_show_args() -> Namespace:
    args = merge_args(create_default_file_params(),
                      create_default_column_selector())
    args.r_head = table.DEFAULT_SHOW_ROW_HEAD_NUMBER
    args.r_tail = table.DEFAULT_SHOW_ROW_TAIL_NUMBER
    args.c_head = table.DEFAULT_SHOW_COL_HEAD_NUMBER
    args.c_tail = table.DEFAULT_SHOW_COL_TAIL_NUMBER
    args.from_row = table.DEFAULT_SHOW_FROM_ROW
    args.to_row = table.DEFAULT_SHOW_TO_ROW
    args.from_col = table.DEFAULT_SHOW_FROM_COL
    args.to_col = table.DEFAULT_SHOW_TO_COL
    args.r_index = table.DEFAULT_SHOW_ROW_INDEX
    args.hide_header = convert_argparser_action_to_bool(
        table.DEFAULT_SHOW_HIDE_HEADER_ACTION)
    args.except_flag = convert_argparser_action_to_bool(
        table.DEFAULT_SHOW_EXCEPT_ACTION)
    return args


def test_get_col_index():
    header = "One;TwO;THREE"
    assert table.get_col_indexes(None, header, ["TWO"], ";") == [1]
    assert table.get_col_indexes(None, header, ["one"], ";") == [0]
    assert table.get_col_indexes(None, header, ["Three"], ";") == [2]
    assert table.get_col_indexes(None, header, ["one", 'three'], ";") == [0, 2]

    header = " \t one, \t two  , three  \t   "
    assert table.get_col_indexes(None, header, ["TWO"], ",") == [1]
    assert table.get_col_indexes(None, header, ["one"], ",") == [0]
    assert table.get_col_indexes(None, header, ["Three"], ",") == [2]
    assert table.get_col_indexes(None, header, ["one", 'three'], ",") == [0, 2]


def test_sort_content_numbers():
    header = "One;Two;Three"
    test_file = table.FileContent(header, ("5;6;7", "1;2;3", "4;2;0"))
    res_file = table.sort_content(test_file, col_indexes=[0],
                                  col_types=["number"], delimiter=';',
                                  rev_order=False, time_fmt="")
    assert res_file.header == header
    assert res_file.content == ("1;2;3", "4;2;0", "5;6;7")

    res_file = table.sort_content(test_file, col_indexes=[2],
                                  col_types=["number"], delimiter=';',
                                  rev_order=True, time_fmt="")
    assert res_file.header == header
    assert res_file.content == ("5;6;7", "1;2;3", "4;2;0")


def test_sort_content_strings():
    header = "One;Two;Three"
    test_file = table.FileContent(header, ("d,  f  ,g", "a,  b  ,c", "w,x,z"))
    res_file = table.sort_content(test_file, col_indexes=[1],
                                  col_types=["string"], delimiter=',',
                                  rev_order=False, time_fmt="")
    assert res_file.header == header
    assert res_file.content == ("a,  b  ,c", "d,  f  ,g", "w,x,z")


def test_convert_to_text():
    test = table.FileContent(None, [])  # empty file
    assert len(table.convert_to_text(test)) == 0
    test = table.FileContent('header', [])  # with header but no content
    assert table.convert_to_text(test) == 'header'
    # no header with content
    test = table.FileContent(None, ['one', 'two', 'three'])
    assert table.convert_to_text(test) == 'one\ntwo\nthree'
    test = table.FileContent('header', ['one'])  # with header and content
    assert table.convert_to_text(test) == 'header\none'


def test_comparator():
    sorter = table.RowSorter(col_indexes=[2, 0, 4],
                             col_types=['string', 'number', 'time'],
                             delimiter=",", time_fmt=table.DEFAULT_TIME_FORMAT)
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

    table.callback_sort(args)
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

    table.callback_sort(args)
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

    table.callback_sort(args)
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

    table.callback_sort(args)
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

    table.callback_sort(args)
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

    table.callback_sort(args)
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

    table.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((header, r1, r2, r3, r4, r5, r6))
    # sort according to the second column
    args.c_name = ["two"]
    table.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((header, r1, r2, r3, r4, r5, r6))
    # sort according to the last column
    args.c_name = ["three"]
    table.callback_sort(args)
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

    table.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((header, r3, r5, r4, r2, r1))


def test_check_arguments_sort():
    '''If no types were passed we want to automatically assume
    that all column types are numeric'''

    args = create_default_sort_args()
    args.c_index = [1]

    table.check_arguments(args)
    assert len(args.c_type) == len(args.c_index)
    assert all(el == table.ColumnType.NUMBER.value for el in args.c_type)

    args.c_index = [5, 4, 3]
    args.c_type = []
    table.check_arguments(args)
    assert len(args.c_type) == len(args.c_index)
    assert all(el == table.ColumnType.NUMBER.value for el in args.c_type)

    args.c_index = None
    args.c_name = ["one"]
    args.c_type = None
    table.check_arguments(args)
    assert len(args.c_type) == len(args.c_name)
    assert all(el == table.ColumnType.NUMBER.value for el in args.c_type)

    args.c_name = ["one", "two"]
    args.c_type = []
    table.check_arguments(args)
    assert len(args.c_type) == len(args.c_name)
    assert all(el == table.ColumnType.NUMBER.value for el in args.c_type)


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
    table.callback_sort(args)

    with open(fpath, 'r') as fin:
        data = fin.read()

    assert data == '\n'.join((r3, r1, r4, r2, r5))


def test_sort_when_convertion_fails_1(tmp_path):
    r1 = "5; a"
    r2 = "-; b"
    r3 = "; d"
    r4 = "0; v"
    r5 = "nan; and"
    r6 = "definetely not a number; num"
    fpath = create_file(tmp_path / "test.csv", (r1, r2, r3, r4, r5, r6))

    args = create_default_sort_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.no_header = True
    args.c_index = [0]
    args.c_type = ["number"]
    args.inplace = True

    table.callback_sort(args)

    with open(fpath, 'r') as fin:
        data = fin.read()

    assert data == '\n'.join((r4, r1, r2, r3, r5, r6))


def test_sort_when_convertion_fails_2(tmp_path):
    r1 = "2010-01-01; a"
    r2 = "-; b"
    r3 = "; d"
    r4 = "2008-09-12; v"
    r5 = "nan; and"
    r6 = "definetely not a number; num"
    fpath = create_file(tmp_path / "test.csv", (r1, r2, r3, r4, r5, r6))

    args = create_default_sort_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.no_header = True
    args.c_index = [0]
    args.c_type = ["time"]
    args.inplace = True
    args.time_fmt = "%Y-%m-%d"

    table.callback_sort(args)

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

    table.callback_sort(args)
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

    table.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()

    assert data == '\n'.join((str(el) for el in sorted(values)))


def test_sort_single_string_column(tmp_path):
    values = ("one", "two", "abcd", "elleven", "buiding")
    fpath = create_file(tmp_path / "test.csv", values)

    args = create_default_sort_args()
    args.delimiter = "DELIMITER"
    args.files = [fpath]
    args.no_header = True
    args.c_index = [0]
    args.c_type = ["string"]
    args.inplace = True
    args.reverse = True

    table.callback_sort(args)
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

    table.callback_sort(args)
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

    table.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()

    assert data == '\n'.join((header, r1, r3, r2, r4))


def test_select_from_row():
    assert table.select_from_row("1;2;3;4;5", ";", [0, 2, 4]) == "1;3;5"
    assert table.select_from_row(
        "1;2;3;4;5", ";", [0, 1, 2, 3, 4]) == "1;2;3;4;5"
    assert table.select_from_row("1;2;3;4;5", ";", [1, 3]) == "2;4"
    assert table.select_from_row("1;2;3;4;5", ";", [1]) == "2"
    assert table.select_from_row("1;2;3;4;5", ",", [0]) == "1;2;3;4;5"
    assert table.select_from_row("1,2,3,4,5", ",", [4]) == "5"
    assert table.select_from_row("onetwoonethree", "one", [
                                 1, 2]) == "twoonethree"
    assert table.select_from_row("1;2;3;4;5", ";", []) == ""


def test_show_single_column_with_header(tmp_path, capsys):
    header = "Date;String;Int;Double"
    r1 = "2010-01-01;one;1;1.3"
    r2 = "2010-07-02;two;2;2.6"
    r3 = "2010-06-03;three;3;3.9"
    r4 = "2010-11-03;four;4;5.9"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4))

    args = create_default_show_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.c_name = ["Date"]

    table.callback_show(args)

    out = capsys.readouterr().out

    exp_header = "Date"
    exp_r1 = "2010-01-01"
    exp_r2 = "2010-07-02"
    exp_r3 = "2010-06-03"
    exp_r4 = "2010-11-03"
    # in captured data we have a new line at the end
    assert out[:-1] == '\n'.join((exp_header, exp_r1, exp_r2, exp_r3, exp_r4))


def test_show_single_column_no_header(tmp_path, capsys):
    r1 = "2010-01-01|one|1|1.3"
    r2 = "2010-07-02|two|2|2.6"
    r3 = "2010-06-03|three|3|3.9"
    r4 = "2010-11-03|four|4|5.9"
    fpath = create_file(tmp_path / "test.csv", (r1, r2, r3, r4))

    args = create_default_show_args()
    args.delimiter = "|"
    args.files = [fpath]
    args.c_index = [3]

    table.callback_show(args)

    out = capsys.readouterr().out

    exp_r1 = "1.3"
    exp_r2 = "2.6"
    exp_r3 = "3.9"
    exp_r4 = "5.9"
    # in captured data we have a new line at the end
    assert out[:-1] == '\n'.join((exp_r1, exp_r2, exp_r3, exp_r4))


def test_show_all_columns_when_none_is_given(tmp_path, capsys):
    r1 = "2010-01-01;one;1;1.3"
    r2 = "2010-07-02;two;2;2.6"
    r3 = "2010-06-03;three;3;3.9"
    r4 = "2010-11-03;four;4;5.9"
    fpath = create_file(tmp_path / "test.csv", (r1, r2, r3, r4))

    args = create_default_show_args()
    args.delimiter = ";"
    args.files = [fpath]

    table.callback_show(args)

    out = capsys.readouterr().out

    # in captured data we have a new line at the end
    assert out[:-1] == '\n'.join((r1, r2, r3, r4))


def test_show_few_columns(tmp_path, capsys):
    header = "Date;String;Int;Double"
    r1 = "2010-01-01;one;1;1.3"
    r2 = "2010-07-02;two;2;2.6"
    r3 = "2010-06-03;three;3;3.9"
    r4 = "2010-11-03;four;4;5.9"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4))

    args = create_default_show_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.c_name = ["Date", "Int"]

    table.callback_show(args)

    out = capsys.readouterr().out

    exp_header = "Date;Int"
    exp_r1 = "2010-01-01;1"
    exp_r2 = "2010-07-02;2"
    exp_r3 = "2010-06-03;3"
    exp_r4 = "2010-11-03;4"
    # in captured data we have a new line at the end
    assert out[:-1] == '\n'.join((exp_header, exp_r1, exp_r2, exp_r3, exp_r4))


def test_show_few_columns_in_different_order(tmp_path, capsys):
    header = "Date;String;Int;Double"
    r1 = "2010-01-01;one;1;1.3"
    r2 = "2010-07-02;two;2;2.6"
    r3 = "2010-06-03;three;3;3.9"
    r4 = "2010-11-03;four;4;5.9"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4))

    args = create_default_show_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.c_name = ["Int", "Date"]

    table.callback_show(args)

    out = capsys.readouterr().out

    exp_header = "Date;Int"
    exp_r1 = "2010-01-01;1"
    exp_r2 = "2010-07-02;2"
    exp_r3 = "2010-06-03;3"
    exp_r4 = "2010-11-03;4"
    # in captured data we have a new line at the end
    assert out[:-1] == '\n'.join((exp_header, exp_r1, exp_r2, exp_r3, exp_r4))


def test_show_few_columns_without_modifying_spaces(tmp_path, capsys):
    header = "Date;String;Int;Double"
    r1 = "   2010-01-01;  one   ;1;1.3"
    r2 = "  2010-07-02;\t\ttwo ;2 ;2.6"
    r3 = " 2010-06-03;    three;3  ;3.9"
    r4 = "2010-11-03;four     ;4   ;5.9"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4))

    args = create_default_show_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.c_index = [0, 1, 2]

    table.callback_show(args)

    out = capsys.readouterr().out

    exp_header = "Date;String;Int"
    exp_r1 = "   2010-01-01;  one   ;1"
    exp_r2 = "  2010-07-02;\t\ttwo ;2 "
    exp_r3 = " 2010-06-03;    three;3  "
    exp_r4 = "2010-11-03;four     ;4   "
    # in captured data we have a new line at the end
    assert out[:-1] == '\n'.join((exp_header, exp_r1, exp_r2, exp_r3, exp_r4))


def test_show_from_empty_file_all(tmp_path, capsys):
    fpath = tmp_path/"test.csv"
    fpath.touch()

    args = create_default_show_args()
    args.delimiter = ";"
    args.files = [fpath]
    args.no_header = True
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out == "\n"

    # Show file with empty header
    args.no_header = False
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out == '\n'


def test_show_from_file_with_header_only(tmp_path, capsys):
    header = "one,two,three,four"
    fpath = create_file(tmp_path / "test.csv", (header,))

    args = create_default_show_args()
    args.delimiter = ","
    args.files = [fpath]
    args.c_index = [0, 2]

    table.callback_show(args)

    out = capsys.readouterr().out
    assert out[:-1] == "one,three"


def test_show_from_single_row_no_header(tmp_path, capsys):
    row = "one two three four"
    fpath = create_file(tmp_path / "test.csv", (row,))

    args = create_default_show_args()
    args.delimiter = " "
    args.files = [fpath]
    args.no_header = True
    args.c_index = [2]

    table.callback_show(args)
    out = capsys.readouterr().out

    assert out[:-1] == "three"


def test_show_entire_table_with_default_parameters(tmp_path, capsys):
    header = "Date;String;Int;Double"
    r1 = "2020-01-01;Hello;4;23.5"
    r2 = "2020-02-01;World;3;3.14"
    r3 = "2020-03-03;Today;10;9.81"
    r4 = "2020-04-08;Is;1;12.3"
    r5 = "2020-01-01;Saturday;-56;-5.64"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4, r5))

    args = create_default_show_args()
    args.files = [fpath]

    table.callback_show(args)
    out = capsys.readouterr().out

    assert out[:-1] == '\n'.join((header, r1, r2, r3, r4, r5))
    # Same test but without header
    fpath = create_file(tmp_path/"test.csv", (r1, r2, r3, r4, r5))

    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r2, r3, r4, r5))


def test_get_row_indexes():
    res = table.get_row_indexes(total_row_count=5,
                                head=None, tail=None,
                                from_index=None, to_index=None,
                                r_index=None)
    assert res == [0, 1, 2, 3, 4]

    res = table.get_row_indexes(total_row_count=5,
                                head=0, tail=None,
                                from_index=None, to_index=None,
                                r_index=None)
    assert res == []

    res = table.get_row_indexes(total_row_count=5,
                                head=None, tail=0,
                                from_index=None, to_index=None,
                                r_index=None)
    assert res == []

    res = table.get_row_indexes(total_row_count=5,
                                head=0, tail=0,
                                from_index=None, to_index=None,
                                r_index=None)
    assert res == []

    res = table.get_row_indexes(total_row_count=5,
                                head=3, tail=None,
                                from_index=None, to_index=None,
                                r_index=None)
    assert res == [0, 1, 2]

    res = table.get_row_indexes(total_row_count=5,
                                head=None, tail=3,
                                from_index=None, to_index=None,
                                r_index=None)
    assert res == [2, 3, 4]

    res = table.get_row_indexes(total_row_count=5,
                                head=1, tail=1,
                                from_index=None, to_index=None,
                                r_index=None)
    assert res == [0, 4]

    res = table.get_row_indexes(total_row_count=5,
                                head=3, tail=3,
                                from_index=None, to_index=None,
                                r_index=None)
    assert res == [0, 1, 2, 3, 4]

    res = table.get_row_indexes(total_row_count=5,
                                head=30, tail=30,
                                from_index=None, to_index=None,
                                r_index=None)
    assert res == [0, 1, 2, 3, 4]

    res = table.get_row_indexes(total_row_count=5,
                                head=10, tail=None,
                                from_index=None, to_index=None,
                                r_index=None)
    assert res == [0, 1, 2, 3, 4]

    res = table.get_row_indexes(total_row_count=5,
                                head=None, tail=50,
                                from_index=None, to_index=None,
                                r_index=None)
    assert res == [0, 1, 2, 3, 4]

    res = table.get_row_indexes(total_row_count=0,
                                head=None, tail=None,
                                from_index=None, to_index=None,
                                r_index=None)
    assert res == []

    res = table.get_row_indexes(total_row_count=0,
                                head=5, tail=None,
                                from_index=None, to_index=None,
                                r_index=None)
    assert res == []

    res = table.get_row_indexes(total_row_count=0,
                                head=None, tail=10,
                                from_index=None, to_index=None,
                                r_index=None)
    assert res == []

    res = table.get_row_indexes(total_row_count=0,
                                head=25, tail=10,
                                from_index=None, to_index=None,
                                r_index=None)
    assert res == []

    res = table.get_row_indexes(total_row_count=0,
                                head=None, tail=None,
                                from_index=None, to_index=None,
                                r_index=[1, 2, 3, 4, 5])
    assert res == []

    res = table.get_row_indexes(total_row_count=6,
                                head=None, tail=None,
                                from_index=[1, 3], to_index=[2, 4],
                                r_index=None)
    assert res == [1, 3]

    res = table.get_row_indexes(total_row_count=6,
                                head=None, tail=None,
                                from_index=[0, 1, 3], to_index=[1, 3, 6],
                                r_index=None)
    assert res == [0, 1, 2, 3, 4, 5]

    res = table.get_row_indexes(total_row_count=6,
                                head=4, tail=2,
                                from_index=[1, 3], to_index=[2, 4],
                                r_index=None)
    assert res == [0, 1, 2, 3, 4, 5]

    res = table.get_row_indexes(total_row_count=6,
                                head=None, tail=None,
                                from_index=None, to_index=None,
                                r_index=[1, 3, 4, 5])
    assert res == [1, 3, 4, 5]

    res = table.get_row_indexes(total_row_count=6,
                                head=None, tail=None,
                                from_index=None, to_index=None,
                                r_index=[1000])
    assert res == []

    res = table.get_row_indexes(total_row_count=6,
                                head=1, tail=1,
                                from_index=None, to_index=None,
                                r_index=[2])
    assert res == [0, 2, 5]

    res = table.get_row_indexes(total_row_count=6,
                                head=1, tail=1,
                                from_index=[1], to_index=[4],
                                r_index=[2, 3, 5])
    assert res == [0, 1, 2, 3, 5]


def test_show_table_with_only_head(tmp_path, capsys):
    header = "Int;Double;String"
    r1 = "1; 1.0; one"
    r2 = "3; 3.0; three"
    r3 = "5; 5.0; five"
    r4 = "4; 4.0; four"
    r5 = "2; 2.0; two"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4, r5))

    args = create_default_show_args()
    args.files = [fpath]

    args.r_head = 0
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == header

    args.r_head = 1
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1))

    args.r_head = 2
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r2))

    args.r_head = 20
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r2, r3, r4, r5))


def test_show_table_with_only_head_and_columns(tmp_path, capsys):
    header = "Int;Double;String"
    r1 = "1; 1.0; one"
    r2 = "3; 3.0; three"
    r3 = "5; 5.0; five"
    r4 = "4; 4.0; four"
    r5 = "2; 2.0; two"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4, r5))

    exp_header = "Int;String"
    exp_r1 = "1; one"
    exp_r2 = "3; three"
    exp_r3 = "5; five"
    exp_r4 = "4; four"
    exp_r5 = "2; two"

    args = create_default_show_args()
    args.files = [fpath]
    args.delimiter = ";"
    args.c_index = [0, 2]

    args.r_head = 0
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == exp_header

    args.r_head = 1
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1))

    args.r_head = 2
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1, exp_r2))

    args.r_head = 20
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1,
                                 exp_r2, exp_r3, exp_r4, exp_r5))


def test_show_table_with_only_tail(tmp_path, capsys):
    header = "Int;Double;String"
    r1 = "1; 1.0; one"
    r2 = "3; 3.0; three"
    r3 = "5; 5.0; five"
    r4 = "4; 4.0; four"
    r5 = "2; 2.0; two"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4, r5))

    args = create_default_show_args()
    args.files = [fpath]

    args.r_tail = 0
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == header

    args.r_tail = 1
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r5))

    args.r_tail = 2
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r4, r5))

    args.r_tail = 20
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r2, r3, r4, r5))


def test_show_table_with_only_tail_and_columns(tmp_path, capsys):
    header = "Int;Double;String"
    r1 = "1; 1.0; one"
    r2 = "3; 3.0; three"
    r3 = "5; 5.0; five"
    r4 = "4; 4.0; four"
    r5 = "2; 2.0; two"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4, r5))

    exp_header = "Int;String"
    exp_r1 = "1; one"
    exp_r2 = "3; three"
    exp_r3 = "5; five"
    exp_r4 = "4; four"
    exp_r5 = "2; two"

    args = create_default_show_args()
    args.files = [fpath]
    args.delimiter = ";"
    args.c_index = [2, 0]

    args.r_tail = 0
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == exp_header

    args.r_tail = 1
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r5))

    args.r_tail = 2
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r4, exp_r5))

    args.r_tail = 20
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1,
                                 exp_r2, exp_r3, exp_r4, exp_r5))


def test_show_table_with_head_and_tail(tmp_path, capsys):
    r1 = "1; 1.0; one"
    r2 = "3; 3.0; three"
    r3 = "5; 5.0; five"
    r4 = "4; 4.0; four"
    r5 = "2; 2.0; two"
    fpath = create_file(tmp_path / "test.csv", (r1, r2, r3, r4, r5))

    args = create_default_show_args()
    args.files = [fpath]
    args.no_header = True

    args.r_head = 0
    args.r_tail = 0
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out == '\n'

    args.r_head = 1
    args.r_tail = 1
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r5))

    args.r_head = 2
    args.r_tail = 2
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r2, r4, r5))

    args.r_head = 46
    args.r_tail = 20
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r2, r3, r4, r5))


def test_show_table_with_only_head_and_tail_and_columns(tmp_path, capsys):
    header = "Int;Double;String"
    r1 = "1; 1.0; one"
    r2 = "3; 3.0; three"
    r3 = "5; 5.0; five"
    r4 = "4; 4.0; four"
    r5 = "2; 2.0; two"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4, r5))

    exp_header = "Int;String"
    exp_r1 = "1; one"
    exp_r2 = "3; three"
    exp_r3 = "5; five"
    exp_r4 = "4; four"
    exp_r5 = "2; two"

    args = create_default_show_args()
    args.files = [fpath]
    args.delimiter = ";"
    args.c_index = [0, 2]

    args.r_head = 0
    args.r_tail = 0
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == exp_header

    args.r_head = 1
    args.r_tail = 1
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1, exp_r5))

    args.r_head = 2
    args.r_tail = 2
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1, exp_r2, exp_r4, exp_r5))

    args.r_head = 20
    args.r_tail = 20
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1,
                                 exp_r2, exp_r3, exp_r4, exp_r5))


def test_expand_int_ranges():
    assert table.expand_int_ranges([(1, 2), (4, 6)]) == [1, 4, 5]
    assert table.expand_int_ranges([(1, 2)]) == [1]
    assert table.expand_int_ranges([(1, 1)]) == []
    assert table.expand_int_ranges([(1, 1), (1, 1), (1, 1)]) == []
    assert table.expand_int_ranges([(1, 1), (2, 3), (3, 3)]) == [2]
    assert table.expand_int_ranges([(1, 5)]) == [1, 2, 3, 4]
    assert table.expand_int_ranges([(1, 5), (2, 7)]) == [1, 2, 3, 4, 5, 6]
    assert table.expand_int_ranges([(1, 5), (2, 7), (3, 6)]) == [
        1, 2, 3, 4, 5, 6]


def test_show_table_row_range_only(tmp_path, capsys):
    header = "Int;Double;String"
    r1 = "1; 1.0; one"
    r2 = "3; 3.0; three"
    r3 = "5; 5.0; five"
    r4 = "4; 4.0; four"
    r5 = "2; 2.0; two"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4, r5))

    args = create_default_show_args()
    args.files = [fpath]
    args.delimiter = ';'

    args.from_row = [0]
    args.to_row = [0]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == header

    args.from_row = [100]
    args.to_row = [100]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == header

    args.from_row = [0, 2, 4]
    args.to_row = [1, 3, 5]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r3, r5))

    args.from_row = [0, 2]
    args.to_row = [4, 5]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r2, r3, r4, r5))

    args.from_row = [0]
    args.to_row = [5]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r2, r3, r4, r5))

    args.from_row = [0]
    args.to_row = [50]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r2, r3, r4, r5))

    exp_header = "Int;String"
    exp_r1 = "1; one"
    exp_r2 = "3; three"
    exp_r3 = "5; five"
    exp_r4 = "4; four"
    exp_r5 = "2; two"

    args.c_index = [2, 0]
    args.from_row = [1]
    args.to_row = [4]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r2, exp_r3, exp_r4))


def test_show_head_tail_and_ranges(tmp_path, capsys):
    header = "Int;Double;String"
    r1 = "1; 1.0; one"
    r2 = "3; 3.0; three"
    r3 = "5; 5.0; five"
    r4 = "4; 4.0; four"
    r5 = "2; 2.0; two"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4, r5))

    args = create_default_show_args()
    args.files = [fpath]
    args.delimiter = ';'

    # No crossection
    args.r_head = 1
    args.r_tail = 1
    args.from_row = [1, 3]
    args.to_row = [2, 4]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r2, r4, r5))

    # With crossection
    args.r_head = 3
    args.r_tail = 3
    args.from_row = [1, 2, 3, 4]
    args.to_row = [4, 3, 5, 5]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r2, r3, r4, r5))


def test_show_specific_rows(tmp_path, capsys):
    header = "Int;Double;String"
    r1 = "1; 1.0; one"
    r2 = "3; 3.0; three"
    r3 = "5; 5.0; five"
    r4 = "4; 4.0; four"
    r5 = "2; 2.0; two"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4, r5))

    args = create_default_show_args()
    args.files = [fpath]
    args.delimiter = ';'

    args.r_index = [0, 2, 4]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r3, r5))

    args.r_index = [4, 2, 0]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r3, r5))

    exp_header = "Int;String"
    exp_r1 = "1; one"
    exp_r2 = "3; three"
    exp_r3 = "5; five"
    exp_r4 = "4; four"
    exp_r5 = "2; two"
    args.c_index = [0, 2]
    args.r_index = [1, 2, 20]

    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r2, exp_r3))


def test_show_all_row_filters_together(tmp_path, capsys):
    header = "Int;Double;String"
    r1 = "1; 1.0; one"
    r2 = "3; 3.0; three"
    r3 = "5; 5.0; five"
    r4 = "4; 4.0; four"
    r5 = "2; 2.0; two"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4, r5))

    args = create_default_show_args()
    args.files = [fpath]
    args.delimiter = ';'

    # No crossection
    args.r_head = 1
    args.r_tail = 1
    args.from_row = [1]
    args.to_row = [2]
    args.r_index = [3]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r2, r4, r5))

    # With crossection
    args.r_head = 2
    args.r_tail = 2
    args.from_row = [1, 2]
    args.to_row = [3, 5]
    args.r_index = [1, 3, 4]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r2, r3, r4, r5))


def test_show_everything_without_header(tmp_path, capsys):
    header = "Int;Double;String"
    r1 = "1; 1.0; one"
    r2 = "3; 3.0; three"
    r3 = "5; 5.0; five"
    r4 = "4; 4.0; four"
    r5 = "2; 2.0; two"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3, r4, r5))

    args = create_default_show_args()
    args.files = [fpath]
    args.delimiter = ';'
    args.hide_header = True
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r2, r3, r4, r5))


def test_show_hide_header_whith_no_rows(tmp_path, capsys):
    header = "Int;Double;String"
    fpath = create_file(tmp_path / "test.csv", (header,))

    args = create_default_show_args()
    args.files = [fpath]
    args.hide_header = True
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == ""


def test_show_hide_header_ignored_when_no_header_present(tmp_path, capsys):
    r1 = "1; 1.0; one"
    r2 = "3; 3.0; three"
    r3 = "5; 5.0; five"
    r4 = "4; 4.0; four"
    r5 = "2; 2.0; two"
    fpath = create_file(tmp_path / "test.csv", (r1, r2, r3, r4, r5))

    args = create_default_show_args()
    args.files = [fpath]
    args.no_header = True
    args.hide_header = True
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r2, r3, r4, r5))


def test_show_column_head_and_tail(tmp_path, capsys):
    r1 = "1,2,3,4,5,6,7,8,9"
    r2 = "11,12,13,14,15,16,17,18,19"
    r3 = "111,112,113,114,115,116,117,118,119"
    fpath = create_file(tmp_path/"test.csv", (r1, r2, r3))

    args = create_default_show_args()
    args.files = [fpath]
    args.no_header = True
    args.delimiter = ','

    args.c_head = 0
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == ""

    args.c_tail = 0
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == ""

    exp_r1 = "1,2,3,4"
    exp_r2 = "11,12,13,14"
    exp_r3 = "111,112,113,114"
    args.c_head = 4
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_r1, exp_r2, exp_r3))

    exp_r1 = "6,7,8,9"
    exp_r2 = "16,17,18,19"
    exp_r3 = "116,117,118,119"
    args.c_head = None
    args.c_tail = 4
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_r1, exp_r2, exp_r3))

    exp_r1 = "1,2,9"
    exp_r2 = "11,12,19"
    exp_r3 = "111,112,119"
    args.c_head = 2
    args.c_tail = 1
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_r1, exp_r2, exp_r3))

    args.c_tail = None
    args.c_head = 20
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r2, r3))

    args.c_head = None
    args.c_tail = 20
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r2, r3))

    args.c_head = 5
    args.c_tail = 5
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r2, r3))


def test_show_column_head_tail_and_particular(tmp_path, capsys):
    header = "one,trow,three,four,five"
    r1 = "1,2,3,4,5"
    r2 = "11,12,13,14,15"
    r3 = "21,22,23,24,25"
    r4 = "31,32,33,34,35"
    r5 = "41,42,43,44,45"
    r6 = "51,52,53,54,55"
    fpath = create_file(tmp_path / "test.csv",
                        (header, r1, r2, r3, r4, r5, r6))

    args = create_default_show_args()
    args.files = [fpath]
    args.delimiter = ','

    # No crossection
    exp_header = "one,three,four,five"
    exp_r1 = "1,3,4,5"
    exp_r2 = "11,13,14,15"
    exp_r3 = "21,23,24,25"
    exp_r4 = "31,33,34,35"
    exp_r5 = "41,43,44,45"
    exp_r6 = "51,53,54,55"

    args.c_head = 1
    args.c_tail = 1
    args.c_name = ["three", "four"]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1,
                                 exp_r2, exp_r3, exp_r4, exp_r5, exp_r6))

    # With croseection
    exp_header = "three,four,five"
    exp_r1 = "3,4,5"
    exp_r2 = "13,14,15"
    exp_r3 = "23,24,25"
    exp_r4 = "33,34,35"
    exp_r5 = "43,44,45"
    exp_r6 = "53,54,55"
    args.c_head = None
    args.c_tail = 2
    args.c_name = ["three", "four"]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1,
                                 exp_r2, exp_r3, exp_r4, exp_r5, exp_r6))

    # With some row filter
    args.r_head = 2
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1, exp_r2))


def test_show_column_ranges_and_all(tmp_path, capsys):
    header = "one,two,three,four,five"
    r1 = "1,2,3,4,5"
    r2 = "11,12,13,14,15"
    r3 = "21,22,23,24,25"
    r4 = "31,32,33,34,35"
    r5 = "41,42,43,44,45"
    r6 = "51,52,53,54,55"
    fpath = create_file(tmp_path / "test.csv",
                        (header, r1, r2, r3, r4, r5, r6))

    args = create_default_show_args()
    args.files = [fpath]
    args.delimiter = ','

    # No crossection
    exp_header = "one,three,four,five"
    exp_r1 = "1,3,4,5"
    exp_r2 = "11,13,14,15"
    exp_r3 = "21,23,24,25"
    exp_r4 = "31,33,34,35"
    exp_r5 = "41,43,44,45"
    exp_r6 = "51,53,54,55"

    args.from_col = [0, 2]
    args.to_col = [1, 10]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1,
                                 exp_r2, exp_r3, exp_r4, exp_r5, exp_r6))

    # With croseection
    exp_header = "three,four,five"
    exp_r1 = "3,4,5"
    exp_r2 = "13,14,15"
    exp_r3 = "23,24,25"
    exp_r4 = "33,34,35"
    exp_r5 = "43,44,45"
    exp_r6 = "53,54,55"
    args.from_col = [2, 3]
    args.to_col = [4, 5]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1,
                                 exp_r2, exp_r3, exp_r4, exp_r5, exp_r6))

    # With some row filter
    args.r_head = 2
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1, exp_r2))

    # With others
    args.r_head = None
    args.c_head = 1
    args.c_tail = 1
    args.from_col = [1]
    args.to_col = [4]
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1], '\n'.join((header, r1, r2, r3, r4, r5, r6))


def test_show_except_show_all(tmp_path, capsys):
    header = "One,Twom,Three,Four,Five"
    r1 = "1,2,3,4,5"
    r2 = "11,22,33,44,55"
    r3 = "12,23,34,45,56"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3))

    args = create_default_show_args()
    args.files = [fpath]
    # Without delimiter
    args.except_flag = True
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == ""

    # With delimiter
    args.delimiter = ','
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == ""

    # Case with empty file
    fpath = tmp_path / "empty.csv"
    fpath.touch()

    args.files = [fpath]
    args.except_flag = True
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == ""


def test_show_except_show_nothing(tmp_path, capsys):
    header = "One,Twom,Three,Four,Five"
    r1 = "1,2,3,4,5"
    r2 = "11,22,33,44,55"
    r3 = "12,23,34,45,56"
    fpath = create_file(tmp_path / "test.csv", (header, r1, r2, r3))

    args = create_default_show_args()
    args.files = [fpath]
    args.r_head = 0
    args.c_head = 0
    args.except_flag = True
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r2, r3))

    # Case with empty file
    fpath = tmp_path / "empty.csv"
    fpath.touch()
    args.files = [fpath]
    args.r_head = 0
    args.c_head = 0
    args.except_flag = True
    table.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == ""


def test_show_except_show_selected(tmp_path, capsys):
    header = "one,two,three,four,five"
    r1 = "1,2,3,4,5"
    r2 = "11,12,13,14,15"
    r3 = "21,22,23,24,25"
    r4 = "31,32,33,34,35"
    r5 = "41,42,43,44,45"
    r6 = "51,52,53,54,55"
    fpath = create_file(tmp_path / "test.csv",
                        (header, r1, r2, r3, r4, r5, r6))

    args = create_default_show_args()
    args.files = [fpath]
    args.delimiter = ','
    args.r_head = 1
    args.r_tail = 1
    args.r_index = [3]
    args.c_index = [0, 2, 4]
    args.except_flag = True
    table.callback_show(args)
    out = capsys.readouterr().out

    exp_header = "two,four"
    exp_r2 = "12,14"
    exp_r3 = "22,24"
    exp_r5 = "42,44"
    assert out[:-1] == '\n'.join((exp_header, exp_r2, exp_r3, exp_r5))
