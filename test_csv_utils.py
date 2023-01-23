from csv_utility import get_col_indexes, \
    select_from_row, \
    get_row_indexes, \
    expand_int_ranges


def test_get_col_index():
    header = "One;TwO;THREE"
    assert get_col_indexes(None, header, ["TWO"], ";") == [1]
    assert get_col_indexes(None, header, ["one"], ";") == [0]
    assert get_col_indexes(None, header, ["Three"], ";") == [2]
    assert get_col_indexes(None, header, ["one", 'three'], ";") == [0, 2]

    header = " \t one, \t two  , three  \t   "
    assert get_col_indexes(None, header, ["TWO"], ",") == [1]
    assert get_col_indexes(None, header, ["one"], ",") == [0]
    assert get_col_indexes(None, header, ["Three"], ",") == [2]
    assert get_col_indexes(None, header, ["one", 'three'], ",") == [0, 2]


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
