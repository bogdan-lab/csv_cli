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
                                  delimiter=';', rev_order=False)
    assert res_file.header == header
    assert res_file.content == ["1;2;3", "4;2;0", "5;6;7"]

    res_file = table.sort_content(test_file, col_index=2, col_type="number",
                                  delimiter=';', rev_order=True)
    assert res_file.header == header
    assert res_file.content == ["5;6;7", "1;2;3", "4;2;0"]


def test_sort_content_strings():
    header = "One;Two;Three"
    test_file = table.FileContent(header, ["d,  f  ,g", "a,  b  ,c", "w,x,z"])
    res_file = table.sort_content(test_file, col_index=1, col_type="string",
                                  delimiter=',', rev_order=False)
    assert res_file.header == header
    assert res_file.content == ["a,  b  ,c", "d,  f  ,g", "w,x,z"]


def test_sort_empty_file(tmp_path):
    fpath = tmp_path / "empty.csv"
    fpath.touch()
    args = Namespace()
    args.delimiter = ";"
    args.file = fpath
    args.header = True
    args.c_name = None
    args.c_index = 0
    args.c_type = 'string'
    args.inplace = True
    table.callback_sort(args)
    with open(fpath, 'r') as fin:
        data = fin.readlines()
    assert len(data) == 0

# TODO Add test where we try to sort empty file
# TODO test with header only file
# TODO we cannot sort by 0 column!