import csv_read_write as crw
from utils_for_tests import create_file


def test_read_empty_file(tmp_path):
    fpath = tmp_path / 'test.csv'
    fpath.touch()
    # with header
    res = crw.read_file(fpath, has_header=True)
    assert res.header is not None
    assert res.header == ""
    assert res.content is not None
    assert len(res.content) == 0
    # whithout header
    res = crw.read_file(fpath, has_header=False)
    assert res.header is None
    assert res.content is not None
    assert len(res.content) == 0


def test_raed_filled_file(tmp_path):
    header = "   one   ,   two   ,   three   "
    r1 = "1,   2   , 3    "
    r2 = "       4,5,6"
    r3 = "7,8,9        "
    # with header
    fpath = create_file(tmp_path / 'test.csv', (header, r1, r2, r3))
    res = crw.read_file(fpath, has_header=True)
    assert res.header == header
    assert res.content == (r1, r2, r3)
    # without header
    fpath = create_file(tmp_path / 'test.csv', (r1, r2, r3))
    res = crw.read_file(fpath, has_header=False)
    assert res.header is None
    assert res.content == (r1, r2, r3)


def get_column_count_empty():
    assert crw.get_column_count(crw.FileContent(None, tuple())) == 0
    assert crw.get_column_count(crw.FileContent("", tuple())) == 0


def test_get_column_count_single(tmp_path):
    header = "One"
    r1 = "1"
    r2 = "2"
    r3 = "3"
    fpath = create_file(tmp_path / 'test.csv', (header, r1, r2, r3))
    fc = crw.read_file(fpath, has_header=True)
    assert crw.get_column_count(fc, delimiter=',') == 1
    assert crw.get_column_count(fc, delimiter=';') == 1

    fpath = create_file(tmp_path / 'test.csv', (header,))
    fc = crw.read_file(fpath, has_header=True)
    assert crw.get_column_count(fc, delimiter=',') == 1
    assert crw.get_column_count(fc, delimiter=';') == 1

    fpath = create_file(tmp_path / 'test.csv', (r1, r2, r3))
    fc = crw.read_file(fpath, has_header=False)
    assert crw.get_column_count(fc, delimiter=',') == 1
    assert crw.get_column_count(fc, delimiter=';') == 1

    fpath = create_file(tmp_path / 'test.csv', (header,))
    fc = crw.read_file(fpath, has_header=False)
    assert crw.get_column_count(fc, delimiter=',') == 1
    assert crw.get_column_count(fc, delimiter=';') == 1


def test_get_column_count_general(tmp_path):
    header = "one, two, three"
    r1 = "1, 2, 3"
    r2 = "2, 3, 4"
    r3 = "3, 4, 5"

    fpath = create_file(tmp_path / 'test.csv', (header, r1, r2, r3))
    fc = crw.read_file(fpath, has_header=True)
    assert crw.get_column_count(fc, ',') == 3

    fpath = create_file(tmp_path / 'test.csv', (header,))
    fc = crw.read_file(fpath, has_header=True)
    assert crw.get_column_count(fc, delimiter=',') == 3

    fpath = create_file(tmp_path / 'test.csv', (r1, r2, r3))
    fc = crw.read_file(fpath, has_header=False)
    assert crw.get_column_count(fc, delimiter=',') == 3

    fpath = create_file(tmp_path / 'test.csv', (r1,))
    fc = crw.read_file(fpath, has_header=False)
    assert crw.get_column_count(fc, delimiter=',') == 3


def test_convert_to_text():
    test = crw.FileContent(None, [])  # empty file
    assert len(crw.convert_to_text(test, hide_header=False)) == 0
    assert len(crw.convert_to_text(test, hide_header=True)) == 0
    test = crw.FileContent('header', [])  # with header but no content
    assert crw.convert_to_text(test, hide_header=False) == 'header'
    assert crw.convert_to_text(test, hide_header=True) == ''
    # no header with content
    test = crw.FileContent(None, ['one', 'two', 'three'])
    assert crw.convert_to_text(test, hide_header=False) == 'one\ntwo\nthree'
    assert crw.convert_to_text(test, hide_header=True) == 'one\ntwo\nthree'
    # empty header with content
    test = crw.FileContent("", ['one', 'two', 'three'])
    assert crw.convert_to_text(test, hide_header=False) == 'one\ntwo\nthree'
    assert crw.convert_to_text(test, hide_header=True) == 'one\ntwo\nthree'
    # with header and content
    test = crw.FileContent('header', ['one'])
    assert crw.convert_to_text(test, hide_header=False) == 'header\none'
    assert crw.convert_to_text(test, hide_header=True) == 'one'
