from argparse import Namespace


from utils_for_tests import merge_args, \
    create_default_file_params, \
    create_default_column_selector, \
    convert_argparser_action_to_bool, \
    create_file
from csv_defaults import *
import csv_show


def create_default_show_args() -> Namespace:
    args = merge_args(create_default_file_params(),
                      create_default_column_selector())
    args.r_head = DEFAULT_SHOW_ROW_HEAD_NUMBER
    args.r_tail = DEFAULT_SHOW_ROW_TAIL_NUMBER
    args.c_head = DEFAULT_SHOW_COL_HEAD_NUMBER
    args.c_tail = DEFAULT_SHOW_COL_TAIL_NUMBER
    args.from_row = DEFAULT_SHOW_FROM_ROW
    args.to_row = DEFAULT_SHOW_TO_ROW
    args.from_col = DEFAULT_SHOW_FROM_COL
    args.to_col = DEFAULT_SHOW_TO_COL
    args.r_index = DEFAULT_SHOW_ROW_INDEX
    args.hide_header = convert_argparser_action_to_bool(
        DEFAULT_SHOW_HIDE_HEADER_ACTION)
    args.except_flag = convert_argparser_action_to_bool(
        DEFAULT_SHOW_EXCEPT_ACTION)
    return args


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

    csv_show.callback_show(args)

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

    csv_show.callback_show(args)

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

    csv_show.callback_show(args)

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

    csv_show.callback_show(args)

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

    csv_show.callback_show(args)

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

    csv_show.callback_show(args)

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
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out == "\n"

    # Show file with empty header
    args.no_header = False
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out == '\n'


def test_show_from_file_with_header_only(tmp_path, capsys):
    header = "one,two,three,four"
    fpath = create_file(tmp_path / "test.csv", (header,))

    args = create_default_show_args()
    args.delimiter = ","
    args.files = [fpath]
    args.c_index = [0, 2]

    csv_show.callback_show(args)

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

    csv_show.callback_show(args)
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

    csv_show.callback_show(args)
    out = capsys.readouterr().out

    assert out[:-1] == '\n'.join((header, r1, r2, r3, r4, r5))
    # Same test but without header
    fpath = create_file(tmp_path/"test.csv", (r1, r2, r3, r4, r5))

    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r2, r3, r4, r5))


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
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == header

    args.r_head = 1
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1))

    args.r_head = 2
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r2))

    args.r_head = 20
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == exp_header

    args.r_head = 1
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1))

    args.r_head = 2
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1, exp_r2))

    args.r_head = 20
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == header

    args.r_tail = 1
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r5))

    args.r_tail = 2
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r4, r5))

    args.r_tail = 20
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == exp_header

    args.r_tail = 1
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r5))

    args.r_tail = 2
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r4, exp_r5))

    args.r_tail = 20
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out == '\n'

    args.r_head = 1
    args.r_tail = 1
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r5))

    args.r_head = 2
    args.r_tail = 2
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r2, r4, r5))

    args.r_head = 46
    args.r_tail = 20
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == exp_header

    args.r_head = 1
    args.r_tail = 1
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1, exp_r5))

    args.r_head = 2
    args.r_tail = 2
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1, exp_r2, exp_r4, exp_r5))

    args.r_head = 20
    args.r_tail = 20
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1,
                                 exp_r2, exp_r3, exp_r4, exp_r5))


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
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == header

    args.from_row = [100]
    args.to_row = [100]
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == header

    args.from_row = [0, 2, 4]
    args.to_row = [1, 3, 5]
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r3, r5))

    args.from_row = [0, 2]
    args.to_row = [4, 5]
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r2, r3, r4, r5))

    args.from_row = [0]
    args.to_row = [5]
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r2, r3, r4, r5))

    args.from_row = [0]
    args.to_row = [50]
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r2, r4, r5))

    # With crossection
    args.r_head = 3
    args.r_tail = 3
    args.from_row = [1, 2, 3, 4]
    args.to_row = [4, 3, 5, 5]
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r3, r5))

    args.r_index = [4, 2, 0]
    csv_show.callback_show(args)
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

    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r2, r4, r5))

    # With crossection
    args.r_head = 2
    args.r_tail = 2
    args.from_row = [1, 2]
    args.to_row = [3, 5]
    args.r_index = [1, 3, 4]
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r2, r3, r4, r5))


def test_show_hide_header_whith_no_rows(tmp_path, capsys):
    header = "Int;Double;String"
    fpath = create_file(tmp_path / "test.csv", (header,))

    args = create_default_show_args()
    args.files = [fpath]
    args.hide_header = True
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == ""

    args.c_tail = 0
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == ""

    exp_r1 = "1,2,3,4"
    exp_r2 = "11,12,13,14"
    exp_r3 = "111,112,113,114"
    args.c_head = 4
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_r1, exp_r2, exp_r3))

    exp_r1 = "6,7,8,9"
    exp_r2 = "16,17,18,19"
    exp_r3 = "116,117,118,119"
    args.c_head = None
    args.c_tail = 4
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_r1, exp_r2, exp_r3))

    exp_r1 = "1,2,9"
    exp_r2 = "11,12,19"
    exp_r3 = "111,112,119"
    args.c_head = 2
    args.c_tail = 1
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_r1, exp_r2, exp_r3))

    args.c_tail = None
    args.c_head = 20
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r2, r3))

    args.c_head = None
    args.c_tail = 20
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((r1, r2, r3))

    args.c_head = 5
    args.c_tail = 5
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1,
                                 exp_r2, exp_r3, exp_r4, exp_r5, exp_r6))

    # With some row filter
    args.r_head = 2
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1,
                                 exp_r2, exp_r3, exp_r4, exp_r5, exp_r6))

    # With some row filter
    args.r_head = 2
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((exp_header, exp_r1, exp_r2))

    # With others
    args.r_head = None
    args.c_head = 1
    args.c_tail = 1
    args.from_col = [1]
    args.to_col = [4]
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == ""

    # With delimiter
    args.delimiter = ','
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == ""

    # Case with empty file
    fpath = tmp_path / "empty.csv"
    fpath.touch()

    args.files = [fpath]
    args.except_flag = True
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
    out = capsys.readouterr().out
    assert out[:-1] == '\n'.join((header, r1, r2, r3))

    # Case with empty file
    fpath = tmp_path / "empty.csv"
    fpath.touch()
    args.files = [fpath]
    args.r_head = 0
    args.c_head = 0
    args.except_flag = True
    csv_show.callback_show(args)
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
    csv_show.callback_show(args)
    out = capsys.readouterr().out

    exp_header = "two,four"
    exp_r2 = "12,14"
    exp_r3 = "22,24"
    exp_r5 = "42,44"
    assert out[:-1] == '\n'.join((exp_header, exp_r2, exp_r3, exp_r5))
