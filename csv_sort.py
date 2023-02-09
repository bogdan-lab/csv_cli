from typing import List, Tuple, Any
from enum import Enum
import datetime
import math

from csv_read_write import FileContent, \
    read_file, \
    convert_to_text, \
    print_to_std_out
from csv_utility import get_indexes_by_names, \
    has_duplicates


class ColumnType(Enum):
    STRING = "string"
    NUMBER = "number"
    TIME = "time"


class RowSorter:
    '''Defines the comparator for sorting rows in the file according to the
    arguments passed by user.'''

    def __init__(self, col_indexes: List[int], col_types: List[str],
                 delimiter: str, time_fmt: str) -> None:
        self.col_indexes = col_indexes
        self.col_types = [ColumnType(ct) for ct in col_types]
        self.delimiter = delimiter
        self.time_fmt = time_fmt

    def _convert_value(self, value: str, v_type: ColumnType) -> Any:
        if v_type is ColumnType.NUMBER:
            try:
                res = float(value)
            except:
                res = math.nan
            return math.inf if math.isnan(res) else res
        elif v_type is ColumnType.STRING:
            return value
        elif v_type is ColumnType.TIME:
            try:
                res = datetime.datetime.strptime(value, self.time_fmt)
            except:
                res = datetime.datetime.max
            return res
        else:
            raise NotImplementedError

    def _value_iterator(self, splitted_row: List[str]):
        for i, row_idx in enumerate(self.col_indexes):
            yield self._convert_value(splitted_row[row_idx].strip(),
                                      self.col_types[i])

    def comparator(self, row: str) -> Tuple[Any]:
        splitted_row = row.split(self.delimiter)
        return tuple(el for el in self._value_iterator(splitted_row))


def sort_content(file_data: FileContent, col_indexes: List[int],
                 col_types: List[str], delimiter: str, rev_order: bool,
                 time_fmt: str) -> FileContent:
    '''Sorts the content field in the FileContent object according to the
    settings'''
    sorter = RowSorter(col_indexes, col_types, delimiter, time_fmt)
    return FileContent(file_data.header, tuple(sorted(file_data.content,
                                                      key=sorter.comparator,
                                                      reverse=rev_order)))


def check_arguments(args) -> None:
    if args.c_index is None and args.c_name is None:
        raise ValueError("Column must be specified by name or index!")
    if args.c_index is not None and args.c_name is not None:
        raise ValueError("Please define column by index OR by name!")
    if args.c_index is None:
        if args.c_type is None or len(args.c_type) == 0:
            args.c_type = [ColumnType.NUMBER.value for _ in args.c_name]
        elif len(args.c_name) != len(args.c_type):
            raise ValueError("Number of columns should be equal to number of"
                             " provided number of column types")
        if args.no_header:
            raise ValueError("If columns index is set by its name, header"
                             " options should be on!")
    if args.c_name is None:
        if args.c_type is None or len(args.c_type) == 0:
            args.c_type = [ColumnType.NUMBER.value for _ in args.c_index]
        elif len(args.c_index) != len(args.c_type):
            raise ValueError("Number of columns should be equal to number of"
                             " provided number of column types")
    if args.c_name is not None and has_duplicates(args.c_name):
        raise ValueError(
            "Duplicate names in 'c_name' argument are not allowed.")
    if args.c_index is not None and has_duplicates(args.c_index):
        raise ValueError(
            "Duplicate indexes in 'c_index' argument are not allowed.")


def callback_sort(args):
    '''Performes sorting files on the command line request'''
    check_arguments(args)
    for file in args.files:
        file_data = read_file(file, not args.no_header)
        col_index = (args.c_index
                     if args.c_index is not None
                     else get_indexes_by_names(file_data.header,
                                               args.delimiter, args.c_name))
        file_data = sort_content(file_data, col_index, args.c_type,
                                 args.delimiter, args.reverse, args.time_fmt)
        if args.inplace:
            with open(file, 'w') as fout:
                fout.write(convert_to_text(file_data, hide_header=False))
        else:
            print_to_std_out(convert_to_text(file_data, hide_header=args.hide_header), file,
                             need_to_mark_filename=len(args.files) > 1)
