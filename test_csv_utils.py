import pytest

from csv_utility import select_from_row, \
    get_row_indexes, \
    expand_int_ranges, \
    get_indexes_by_names, \
    has_duplicates


def test_has_duplicates():
    assert has_duplicates([1, 1, 1, 1])
    assert has_duplicates([1, 1, 2, 3])
    assert has_duplicates([1, 2, 2, 3])
    assert has_duplicates([1, 2, 3, 3])
    assert has_duplicates([3, 3, 2, 1])
    assert has_duplicates([3, 2, 2, 1])
    assert has_duplicates([3, 2, 1, 1])
    assert not has_duplicates([1])
    assert not has_duplicates([])
    assert not has_duplicates([1, 2, 3])
    assert not has_duplicates([3, 2, 1])


def test_get_index_by_names_empty():
    header = ""
    assert get_indexes_by_names(header, ';', []) == []
    assert get_indexes_by_names(header, '-', []) == []


def test_get_index_by_names_one():
    header = "header"
    assert get_indexes_by_names(header, ';', []) == []
    assert get_indexes_by_names(header, ',', ["header"]) == [0]
    with pytest.raises(ValueError):
        get_indexes_by_names(header, '-', ["Header"])


def test_get_index_by_names_spaces():
    header = "\theader   "
    assert get_indexes_by_names(header, ';', ["header"]) == [0]
    assert get_indexes_by_names(header, ',', ["\theader   "]) == [0]
    with pytest.raises(ValueError):
        get_indexes_by_names(header, ',', ["  \t  "])
    header == '    '
    assert get_indexes_by_names(header, ';', []) == []
    # There is no sense in keeping name which consists of white spaces only
    with pytest.raises(ValueError):
        get_indexes_by_names(header, ';', ["\t"])
    with pytest.raises(ValueError):
        get_indexes_by_names(header, ';', ['    '])


def test_get_index_by_names_general():
    header = "one,two,three"
    assert get_indexes_by_names(header, ',', []) == []
    assert get_indexes_by_names(
        header, ',', ["one", "two", "three"]) == [0, 1, 2]
    assert get_indexes_by_names(
        header, ',', ["three", "two", "one"]) == [2, 1, 0]
    assert get_indexes_by_names(
        header, ',', [" one", " two ", " three\t"]) == [0, 1, 2]
    with pytest.raises(ValueError):
        get_indexes_by_names(header, ',', ["tWo"])

    header = "   one    ,   two\t\t, three"
    assert get_indexes_by_names(
        header, ',', ["two", "one", "three"]) == [1, 0, 2]


def test_get_index_by_names_duplicates():
    header = "one;two;two;three"
    assert get_indexes_by_names(header, ';', ['three', 'one']) == [3, 0]
    with pytest.raises(ValueError):
        get_indexes_by_names(header, ';', ['two'])
    with pytest.raises(ValueError):
        get_indexes_by_names(header, ';', ['one', 'two'])
    with pytest.raises(ValueError):
        get_indexes_by_names(header, ';', ['one', 'one'])
    with pytest.raises(ValueError):
        get_indexes_by_names(header, ';', ['three', 'one', 'one'])
    with pytest.raises(ValueError):
        get_indexes_by_names(header, ';', ['two', 'two'])


def test_get_index_by_names_hidden_diplicates():
    header = "one; two; three"
    with pytest.raises(ValueError):
        get_indexes_by_names(header, ';', ["     two", "two     "])


def test_select_from_row():
    assert select_from_row("1;2;3;4;5", ";", [0, 2, 4]) == "1;3;5"
    assert select_from_row(
        "1;2;3;4;5", ";", [0, 1, 2, 3, 4]) == "1;2;3;4;5"
    assert select_from_row("1;2;3;4;5", ";", [1, 3]) == "2;4"
    assert select_from_row("1;2;3;4;5", ";", [1]) == "2"
    assert select_from_row("1;2;3;4;5", ",", [0]) == "1;2;3;4;5"
    assert select_from_row("1,2,3,4,5", ",", [4]) == "5"
    assert select_from_row("onetwoonethree", "one", [
        1, 2]) == "twoonethree"
    assert select_from_row("1;2;3;4;5", ";", []) == ""


def test_get_row_indexes():
    res = get_row_indexes(total_row_count=5,
                          head=None, tail=None,
                          from_index=None, to_index=None,
                          r_index=None)
    assert res == [0, 1, 2, 3, 4]

    res = get_row_indexes(total_row_count=5,
                          head=0, tail=None,
                          from_index=None, to_index=None,
                          r_index=None)
    assert res == []

    res = get_row_indexes(total_row_count=5,
                          head=None, tail=0,
                          from_index=None, to_index=None,
                          r_index=None)
    assert res == []

    res = get_row_indexes(total_row_count=5,
                          head=0, tail=0,
                          from_index=None, to_index=None,
                          r_index=None)
    assert res == []

    res = get_row_indexes(total_row_count=5,
                          head=3, tail=None,
                          from_index=None, to_index=None,
                          r_index=None)
    assert res == [0, 1, 2]

    res = get_row_indexes(total_row_count=5,
                          head=None, tail=3,
                          from_index=None, to_index=None,
                          r_index=None)
    assert res == [2, 3, 4]

    res = get_row_indexes(total_row_count=5,
                          head=1, tail=1,
                          from_index=None, to_index=None,
                          r_index=None)
    assert res == [0, 4]

    res = get_row_indexes(total_row_count=5,
                          head=3, tail=3,
                          from_index=None, to_index=None,
                          r_index=None)
    assert res == [0, 1, 2, 3, 4]

    res = get_row_indexes(total_row_count=5,
                          head=30, tail=30,
                          from_index=None, to_index=None,
                          r_index=None)
    assert res == [0, 1, 2, 3, 4]

    res = get_row_indexes(total_row_count=5,
                          head=10, tail=None,
                          from_index=None, to_index=None,
                          r_index=None)
    assert res == [0, 1, 2, 3, 4]

    res = get_row_indexes(total_row_count=5,
                          head=None, tail=50,
                          from_index=None, to_index=None,
                          r_index=None)
    assert res == [0, 1, 2, 3, 4]

    res = get_row_indexes(total_row_count=0,
                          head=None, tail=None,
                          from_index=None, to_index=None,
                          r_index=None)
    assert res == []

    res = get_row_indexes(total_row_count=0,
                          head=5, tail=None,
                          from_index=None, to_index=None,
                          r_index=None)
    assert res == []

    res = get_row_indexes(total_row_count=0,
                          head=None, tail=10,
                          from_index=None, to_index=None,
                          r_index=None)
    assert res == []

    res = get_row_indexes(total_row_count=0,
                          head=25, tail=10,
                          from_index=None, to_index=None,
                          r_index=None)
    assert res == []

    res = get_row_indexes(total_row_count=0,
                          head=None, tail=None,
                          from_index=None, to_index=None,
                          r_index=[1, 2, 3, 4, 5])
    assert res == []

    res = get_row_indexes(total_row_count=6,
                          head=None, tail=None,
                          from_index=[1, 3], to_index=[2, 4],
                          r_index=None)
    assert res == [1, 3]

    res = get_row_indexes(total_row_count=6,
                          head=None, tail=None,
                          from_index=[1, 1, 1, 3, 3],
                          to_index=[2, 2, 2, 4, 4],
                          r_index=None)
    assert res == [1, 3]

    res = get_row_indexes(total_row_count=6,
                          head=None, tail=None,
                          from_index=[0, 1, 3], to_index=[1, 3, 6],
                          r_index=None)
    assert res == [0, 1, 2, 3, 4, 5]

    res = get_row_indexes(total_row_count=6,
                          head=4, tail=2,
                          from_index=[1, 3], to_index=[2, 4],
                          r_index=None)
    assert res == [0, 1, 2, 3, 4, 5]

    res = get_row_indexes(total_row_count=6,
                          head=None, tail=None,
                          from_index=None, to_index=None,
                          r_index=[1, 3, 4, 5])
    assert res == [1, 3, 4, 5]

    res = get_row_indexes(total_row_count=6,
                          head=None, tail=None,
                          from_index=None, to_index=None,
                          r_index=[1, 1, 1, 1, 1, 1])
    assert res == [1]

    res = get_row_indexes(total_row_count=6,
                          head=None, tail=None,
                          from_index=None, to_index=None,
                          r_index=[1000])
    assert res == []

    res = get_row_indexes(total_row_count=6,
                          head=1, tail=1,
                          from_index=None, to_index=None,
                          r_index=[2])
    assert res == [0, 2, 5]

    res = get_row_indexes(total_row_count=6,
                          head=1, tail=1,
                          from_index=[1], to_index=[4],
                          r_index=[2, 3, 5])
    assert res == [0, 1, 2, 3, 5]

    res = get_row_indexes(total_row_count=6,
                          head=1, tail=1,
                          from_index=[1, 1, 1], to_index=[4, 4, 4],
                          r_index=[2, 2, 3, 3, 3, 5, 5])
    assert res == [0, 1, 2, 3, 5]


def test_expand_int_ranges():
    assert expand_int_ranges([(1, 2), (4, 6)]) == [1, 4, 5]
    assert expand_int_ranges([(1, 2)]) == [1]
    assert expand_int_ranges([(1, 1)]) == []
    assert expand_int_ranges([(1, 1), (1, 1), (1, 1)]) == []
    assert expand_int_ranges([(1, 1), (2, 3), (3, 3)]) == [2]
    assert expand_int_ranges([(1, 5)]) == [1, 2, 3, 4]
    assert expand_int_ranges([(1, 5), (2, 7)]) == [1, 2, 3, 4, 5, 6]
    assert expand_int_ranges([(1, 5), (2, 7), (3, 6)]) == [
        1, 2, 3, 4, 5, 6]
