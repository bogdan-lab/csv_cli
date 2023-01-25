from typing import List, Tuple

from csv_read_write import FileContent, \
    read_file,        \
    convert_to_text,  \
    print_to_std_out, \
    get_column_count
from csv_utility import select_from_row, \
    merge_particular_c_indexes, \
    get_row_indexes, \
    has_duplicates, \
    invert_indexes


def check_arguments(args) -> None:
    '''Does some early basic checks if the user input is valid.
    If it is not an exception will be raised'''
    if args.c_index is not None and any(el < 0 for el in args.c_index):
        raise ValueError("Column index cannot have negative value.")
    if args.c_index is not None and has_duplicates(args.c_index):
        raise ValueError(
            "Duplicate indexes in 'c_index' argument are not allowed")
    if args.c_name is not None and args.no_header:
        raise ValueError(
            "You cannot select column by name if there is no header")
    if args.c_name is not None and has_duplicates(args.c_name):
        raise ValueError(
            "Duplicate names in 'c_name' argument are not allowed")
    if args.r_head is not None and args.r_head < 0:
        raise ValueError("Row head value cannot be negative")
    if args.r_tail is not None and args.r_tail < 0:
        raise ValueError("Row tail value cannot be negative")
    has_row_ranges = args.from_row is not None and args.to_row is not None
    miss_row_edge = (args.from_row and not args.to_row) or (
        args.to_row and not args.from_row)
    if miss_row_edge or (has_row_ranges and len(args.from_row) != len(args.to_row)):
        raise ValueError(
            "For each given `from_row` value one has to set `to_row` value")
    if args.from_row is not None and any(el < 0 for el in args.from_row):
        raise ValueError(
            "Row indexes defined in from_row arguments cannot be negative")
    if args.to_row is not None and any(el < 0 for el in args.to_row):
        raise ValueError(
            "Row indexes defined in to_row arguments cannot be negative")
    if has_row_ranges and any(fr > to for fr, to in zip(args.from_row, args.to_row)):
        raise ValueError(
            "End of row range cannot be smaller than the beginning of row range")
    if args.r_index is not None and any(el < 0 for el in args.r_index):
        raise ValueError("Row index in -r_index argument cannot be negative.")
    if args.r_index is not None and has_duplicates(args.r_index):
        raise ValueError(
            "Duplicate indexes in 'r_index' argument are not allowed")
    if args.c_head is not None and args.c_head < 0:
        raise ValueError("Column head value cannot be negative")
    if args.c_tail is not None and args.c_tail < 0:
        raise ValueError("Column tail value cannot be negative")
    has_col_ranges = args.from_col is not None and args.to_col is not None
    miss_col_edge = (args.from_col and not args.to_col) or (
        args.to_col and not args.from_col)
    if miss_col_edge or (has_col_ranges and len(args.from_col) != len(args.to_col)):
        raise ValueError(
            "For each given `from_col` value one has to set `to_col` value")
    if args.from_col is not None and any(el < 0 for el in args.from_col):
        raise ValueError(
            "Column indexes defined in from_col arguments cannot be negative")
    if args.to_col is not None and any(el < 0 for el in args.to_col):
        raise ValueError(
            "Column indexes defined in to_col arguments cannot be negative")
    if has_col_ranges and any(fr > to for fr, to in zip(args.from_col, args.to_col)):
        raise ValueError(
            "End of col range cannot be smaller than the beginning of column range")


def filter_content(content: Tuple[str], delimiter: str, col_indexes: List[int], row_indexes: List[int]) -> Tuple[str]:
    '''Returns the filtered content which contains only the chosen row_indexes and col_indexes'''
    if len(col_indexes) == 0:
        return tuple()
    return tuple(select_from_row(content[i], delimiter, col_indexes) for i in row_indexes)


def apply_show(file_data: FileContent, row_indexes: List[int], col_indexes: List[int],
               delimiter: str, hide_header: bool) -> FileContent:
    '''Forms new FileContent object which containes only selected column indexes'''
    new_header = None
    if file_data.header and not hide_header:
        new_header = select_from_row(file_data.header, delimiter, col_indexes)
    return FileContent(new_header,
                       tuple(filter_content(file_data.content, delimiter, col_indexes, row_indexes)))


def callback_show(args):
    '''Performes columns selection from file according the the given arguments'''
    check_arguments(args)
    for file in args.files:
        file_data = read_file(file, not args.no_header)
        column_count = get_column_count(file_data, args.delimiter)
        row_count = len(file_data.content)
        c_index = merge_particular_c_indexes(
            args.c_index, args.c_name, file_data.header, args.delimiter)
        col_indexes = get_row_indexes(
            column_count, args.c_head, args.c_tail, args.from_col, args.to_col, c_index)
        row_indexes = get_row_indexes(row_count, args.r_head, args.r_tail,
                                      args.from_row, args.to_row, args.r_index)
        if args.except_flag:
            col_indexes = invert_indexes(col_indexes, column_count)
            row_indexes = invert_indexes(row_indexes, row_count)
        file_data = apply_show(file_data, row_indexes,
                               col_indexes, args.delimiter, args.hide_header)
        print_to_std_out(convert_to_text(file_data), file,
                         need_to_mark_filename=len(args.files) > 1)
