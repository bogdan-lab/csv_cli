import pytest

from csv_utility import select_from_row, \
    ranges_to_int_sequence, \
    get_indexes_by_names, \
    has_duplicates, \
    crossect_ranges, \
    build_ranges_for_singles, \
    build_ranges_for_begins_ends, \
    merge_ranges, \
    invert_indexes


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


def test_select_from_row_special():
    assert select_from_row("", ',', []) == ""
    assert select_from_row("one", ',', [0]) == "one"
    assert select_from_row("", ',', [0]) == ""
    with pytest.raises(ValueError):
        select_from_row("one", ',', [1])
    with pytest.raises(ValueError):
        select_from_row("one,two,three", ',', [1, 3])


def test_select_from_row_order():
    assert select_from_row("1,2,3,4", ',', [0, 2]) == "1,3"
    assert select_from_row("1,2,3,4", ',', [2, 0]) == "1,3"
    assert select_from_row("1,2,3,4", ',', [3, 2, 1, 0]) == "1,2,3,4"
    assert select_from_row("1,2,3,4", ',', [1, 3, 2, 0]) == "1,2,3,4"
    assert select_from_row("1,2,3,4", ',', [0, 3, 1]) == "1,2,4"


def test_elect_from_row_order_duplicates():
    assert select_from_row("1;2;3;4", ';', [0, 0, 0]) == "1;1;1"
    assert select_from_row("1;2;3;4", ';', [3, 3, 3]) == "4;4;4"
    assert select_from_row("1;2;3;4", ';', [0, 2, 2, 3]) == "1;3;3;4"


def test_crossect_ranges_empty():
    res = crossect_ranges((1, 1), (2, 2))
    assert res[0] == res[1]
    res = crossect_ranges((1, 1), (2, 2))
    assert res[0] == res[1]
    res = crossect_ranges((1, 1), (1, 5))
    assert res[0] == res[1]
    res = crossect_ranges((3, 3), (1, 5))
    assert res[0] == res[1]
    res = crossect_ranges((1, 5), (3, 3))
    assert res[0] == res[1]


def test_crossect_ranges_general():
    assert crossect_ranges((1, 5), (3, 4)) == (3, 4)
    assert crossect_ranges((1, 4), (3, 5)) == (3, 4)
    assert crossect_ranges((1, 4), (3, 5)) == (3, 4)
    assert crossect_ranges((3, 5), (1, 4)) == (3, 4)
    res = crossect_ranges((1, 3), (4, 5))
    assert res[0] == res[1]


def test_build_ranges_for_singles():
    assert build_ranges_for_singles([]) == []
    assert build_ranges_for_singles([1, 2, 3]) == [(1, 2), (2, 3), (3, 4)]
    assert build_ranges_for_singles([3, 2, 1]) == [(1, 2), (2, 3), (3, 4)]
    assert build_ranges_for_singles([1, 1, 3, 2]) == [
        (1, 2), (1, 2), (2, 3), (3, 4)]


def test_build_ranges():
    assert build_ranges_for_begins_ends([], []) == []
    assert build_ranges_for_begins_ends([1, 2], [4, 5]) == [(1, 4), (2, 5)]
    assert build_ranges_for_begins_ends([2, 1], [5, 4]) == [(1, 4), (2, 5)]
    assert build_ranges_for_begins_ends([1, 4], [2, 3]) == [(1, 2), (4, 4)]
    assert build_ranges_for_begins_ends([1, 1], [3, 3]) == [(1, 3), (1, 3)]
    with pytest.raises(ValueError):
        build_ranges_for_begins_ends([1], [2, 3])


def tes_merge_ranges():
    assert merge_ranges() == []
    assert merge_ranges([]) == []
    assert merge_ranges((1, 2), []) == [(1, 2)]
    assert merge_ranges((1, 2), (3, 4), (5, 6)) == [(1, 2), (3, 4), (5, 6)]
    assert merge_ranges([(1, 2), (3, 4)], (1, 2), (0, 6)) == [
        (0, 6), (1, 2), (1, 2), (3, 4)]
    assert merge_ranges([(1, 2), (3, 4)], [(0, 6), (1, 2)]) == [
        (0, 6), (1, 2), (1, 2), (3, 4)]
    with pytest.raises(TypeError):
        merge_ranges(1, 2, 3)


def test_expand_int_ranges():
    assert ranges_to_int_sequence([(1, 2), (4, 6)]) == [1, 4, 5]
    assert ranges_to_int_sequence([(1, 2)]) == [1]
    assert ranges_to_int_sequence([(1, 1)]) == []
    assert ranges_to_int_sequence([(1, 1), (1, 1), (1, 1)]) == []
    assert ranges_to_int_sequence([(1, 1), (2, 3), (3, 3)]) == [2]
    assert ranges_to_int_sequence([(1, 5)]) == [1, 2, 3, 4]
    assert ranges_to_int_sequence([(1, 5), (2, 7)]) == [1, 2, 3, 4, 5, 6]
    assert ranges_to_int_sequence([(1, 5), (2, 7), (3, 6)]) == [
        1, 2, 3, 4, 5, 6]
    assert ranges_to_int_sequence([(1, 10), (2, 4), (3, 5), (4, 7), (8, 9), (8, 11)]) == [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert ranges_to_int_sequence([(1, 3), (5, 8)]) == [1, 2, 5, 6, 7]
    assert ranges_to_int_sequence([(-1, 3), (5, 8)]) == [-1, 0, 1, 2, 5, 6, 7]


def test_invert_indexes():
    assert invert_indexes([], 5) == [0, 1, 2, 3, 4]
    assert invert_indexes([0, 1, 2, 3, 4], 5) == []
    assert invert_indexes([0, 1, 2, 3], 5) == [4]
    assert invert_indexes([0, 2, 3], 5) == [1, 4]
    assert invert_indexes([0], 1) == []
    assert invert_indexes([2, 3], 5) == [0, 1, 4]
