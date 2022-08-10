import table
from argparse import Namespace


def test_get_col_index_by_name():
    header = "One;TwO;THREE"
    assert table.get_col_index_by_name(header, "TWO", ";") == 1
    assert table.get_col_index_by_name(header, "one", ";") == 0
    assert table.get_col_index_by_name(header, "Three", ";") == 2

    header = " \t one, \t two  , three  \t   "
    assert table.get_col_index_by_name(header, "TWO", ",") == 1
    assert table.get_col_index_by_name(header, "one", ",") == 0
    assert table.get_col_index_by_name(header, "Three", ",") == 2


def test_sort_content_numbers():
    header = "One;Two;Three"
    test_file = table.FileContent(header, ["5;6;7", "1;2;3", "4;2;0"])
    res_file = table.sort_content(test_file, col_index=0, col_type="number",
                                  delimiter=';', rev_order=False, time_fmt="")
    assert res_file.header == header
    assert res_file.content == ["1;2;3", "4;2;0", "5;6;7"]

    res_file = table.sort_content(test_file, col_index=2, col_type="number",
                                  delimiter=';', rev_order=True, time_fmt="")
    assert res_file.header == header
    assert res_file.content == ["5;6;7", "1;2;3", "4;2;0"]


def test_sort_content_strings():
    header = "One;Two;Three"
    test_file = table.FileContent(header, ["d,  f  ,g", "a,  b  ,c", "w,x,z"])
    res_file = table.sort_content(test_file, col_index=1, col_type="string",
                                  delimiter=',', rev_order=False, time_fmt="")
    assert res_file.header == header
    assert res_file.content == ["a,  b  ,c", "d,  f  ,g", "w,x,z"]


def test_convert_to_text():
    test = table.FileContent(None, [])  # empty file
    assert len(table.convert_to_text(test)) == 0
    test = table.FileContent('header', [])  # with header but no content
    assert table.convert_to_text(test) == 'header'
    test = table.FileContent(None, ['one\n', 'two\n', 'three'])  # no header with content
    assert table.convert_to_text(test) == 'one\ntwo\nthree'
    test = table.FileContent('header\n', ['one'])  # with header and content
    assert table.convert_to_text(test) == 'header\none'


def test_sort_empty_file(tmp_path):
    fpath = tmp_path / "empty.csv"
    fpath.touch()
    args = Namespace()
    args.delimiter = ";"
    args.files = [fpath]
    args.header = True
    args.c_name = None
    args.c_index = 0
    args.c_type = 'string'
    args.inplace = True
    args.reverse = False
    args.time_fmt = table.DEFAULT_TIME_FORMAT
    table.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.readlines()
    assert len(data) == 0


def test_header_only_file(tmp_path):
    fpath = tmp_path / "empty.csv"
    fpath.touch()
    header = "Header1,Header2,Header3"
    with open(fpath, 'w') as fout:
        fout.write(header)
    args = Namespace()
    args.delimiter = ","
    args.files = [fpath]
    args.header = True
    args.c_name = "Header1"
    args.c_index = None
    args.c_type = 'string'
    args.inplace = True
    args.reverse = False
    args.time_fmt = table.DEFAULT_TIME_FORMAT
    table.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == header


def test_sort_file_by_one_column_1(tmp_path):
    fpath = tmp_path / "test.csv"
    fpath.touch()
    r1 = "1;2;3"
    r2 = "2;3;4"
    r3 = "3;4;5"
    r4 = "4;5;6"
    r5 = "5;6;7"
    with open(fpath, 'w') as fout:
        fout.write('\n'.join((r4, r5, r3, r1, r2)))
    args = Namespace()
    args.delimiter = ";"
    args.files = [fpath]
    args.header = False
    args.c_name = None
    args.c_index = 0
    args.c_type = 'number'
    args.inplace = True
    args.reverse = False
    args.time_fmt = table.DEFAULT_TIME_FORMAT
    table.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((r1, r2, r3, r4, r5))


def test_sort_file_by_one_column_2(tmp_path):
    fpath = tmp_path / "test.csv"
    fpath.touch()
    header = 'one;two;three'
    r1 = "1;2;a"
    r2 = "2;3;b"
    r3 = "3;4;c"
    r4 = "4;5;d"
    r5 = "5;6;e"
    with open(fpath, 'w') as fout:
        fout.write('\n'.join((header, r4, r5, r3, r1, r2)))
    args = Namespace()
    args.delimiter = ";"
    args.files = [fpath]
    args.header = True
    args.c_name = 'three'
    args.c_index = None
    args.c_type = 'string'
    args.inplace = True
    args.reverse = True
    args.time_fmt = table.DEFAULT_TIME_FORMAT
    table.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((header, r5, r4, r3, r2, r1))


def test_sort_file_by_one_column_3(tmp_path):
    '''Sorting by time column'''
    fpath = tmp_path / "test.csv"
    fpath.touch()
    header = 'one;two;three'
    r1 = "2010-01-02 13:45:23;2;a"
    r2 = "1993-11-02 23:05:17;3;b"
    r3 = "2015-07-23 08:01:00;4;c"
    r4 = "2001-05-11 00:00:23;5;d"
    r5 = "2011-04-29 17:01:23;6;e"
    with open(fpath, 'w') as fout:
        fout.write('\n'.join((header, r4, r5, r3, r1, r2)))
    args = Namespace()
    args.delimiter = ";"
    args.files = [fpath]
    args.header = True
    args.c_name = 'one'
    args.c_index = None
    args.c_type = 'time'
    args.inplace = True
    args.reverse = False
    args.time_fmt = table.DEFAULT_TIME_FORMAT
    table.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((header, r2, r4, r1, r5, r3))


def test_sort_file_by_one_column_4(tmp_path):
    '''Sorting by time column with different format'''
    fpath = tmp_path / "test.csv"
    fpath.touch()
    header = 'one;two;three'
    r1 = "2010_01_02;2;a"
    r2 = "1993_11_02;3;b"
    r3 = "2015_07_23;4;c"
    r4 = "2001_05_11;5;d"
    r5 = "2011_04_29;6;e"
    with open(fpath, 'w') as fout:
        fout.write('\n'.join((header, r4, r5, r3, r1, r2)))
    args = Namespace()
    args.delimiter = ";"
    args.files = [fpath]
    args.header = True
    args.c_name = 'one'
    args.c_index = None
    args.c_type = 'time'
    args.inplace = True
    args.reverse = True
    args.time_fmt = "%Y_%m_%d"
    table.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((header, r3, r5, r1, r4, r2))


def test_sort_file_without_modification(tmp_path):
    '''Order of rows should be the only thing that is modified'''
    fpath = tmp_path / "test.csv"
    fpath.touch()
    header = '    one;   two   ;three  \t '
    r1 = "   1;  1  ;1   "
    r2 = "   2;  2  ;2   "
    r3 = "   3;  3  ;3   "
    r4 = "   4;  4  ;4   "
    r5 = "   5;  5  ;5   "
    r6 = "   6;  6  ;6   "
    with open(fpath, 'w') as fout:
        fout.write('\n'.join((header, r1, r2, r3, r4, r5, r6)))
    args = Namespace()
    args.delimiter = ";"
    args.files = [fpath]
    args.header = True
    args.c_name = 'one'
    args.c_index = None
    args.c_type = 'number'
    args.inplace = True
    args.reverse = False
    args.time_fmt = "%Y_%m_%d"
    table.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((header, r1, r2, r3, r4, r5, r6))
    # sort according to the second column
    args.c_name = "two"
    table.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((header, r1, r2, r3, r4, r5, r6))
    # sort according to the last column
    args.c_name = "three"
    table.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.read()
    assert data == '\n'.join((header, r1, r2, r3, r4, r5, r6))
