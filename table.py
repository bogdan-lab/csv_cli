import argparse
from typing import Tuple, Any, NamedTuple, Optional, List
import datetime
from enum import Enum
import math


class ColumnType(Enum):
    STRING = "string"
    NUMBER = "number"
    TIME = "time"


class FileContent(NamedTuple):
    header: Optional[str]
    content: Tuple[str]


DEFAULT_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_TABLE_DELIMITER = "\t"
DEFAULT_NO_HEADER_ACTION = "store_true"
DEFAULT_COLUMN_NAME_LIST = None
DEFAULT_COLUMN_INDEX_LIST = None
DEFAULT_INPLACE_ACTION = "store_true"
DEFAULT_COLUMN_TYPE_LIST = None
DEFAULT_SORT_REVERSE_ACTION = "store_true"
DEFAULT_SHOW_HEAD_NUMBER = None
DEFAULT_SHOW_TAIL_NUMBER = None
DEFAULT_SHOW_FROM_ROW = None
DEFAULT_SHOW_TO_ROW = None


def convert_to_text(file_data: FileContent) -> str:
    '''Puts all data from the file content class into single string'''
    if file_data.header is None and len(file_data.content) == 0:
        # empty file case
        return ""
    elif len(file_data.content) == 0:
        # Header only case
        return file_data.header
    elif file_data.header is None and len(file_data.content) != 0:
        # File without header
        return '\n'.join(file_data.content)
    else:
        # File with header and content
        return '\n'.join((file_data.header, *file_data.content))


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


def read_file(filename: str, has_header: bool) -> FileContent:
    with open(filename, 'r') as fin:
        header = None
        if has_header:
            header = fin.readline().rstrip('\n')
        return FileContent(header, tuple(l.rstrip('\n') for l in fin))


def sort_content(file_data: FileContent, col_indexes: List[int],
                 col_types: List[str], delimiter: str, rev_order: bool,
                 time_fmt: str) -> FileContent:
    '''Sorts the content field in the FileContent object according to the
    settings'''
    sorter = RowSorter(col_indexes, col_types, delimiter, time_fmt)
    return FileContent(file_data.header, tuple(sorted(file_data.content,
                                                      key=sorter.comparator,
                                                      reverse=rev_order)))


def get_col_indexes(col_indexes: List[int], header: str, col_names: List[str],
                    delimiter: str) -> List[int]:
    '''Returns column indexes selected by user either directly or according to
    column names in the header'''
    if col_indexes is not None:
        return col_indexes
    name_list = [el.strip() for el in header.casefold().split(delimiter)]
    return [name_list.index(cn.casefold()) for cn in col_names]


def print_to_std_out(content: str, filename: str,
                     need_to_mark_filename: bool) -> None:
    if need_to_mark_filename:
        print('\n'.join((f"==> {filename} <==", content, "")))
    else:
        print(content)


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


def callback_sort(args):
    '''Performes sorting files on the command line request'''
    check_arguments(args)
    for file in args.files:
        file_data = read_file(file, not args.no_header)
        col_index = get_col_indexes(args.c_index, file_data.header,
                                    args.c_name, args.delimiter)
        file_data = sort_content(file_data, col_index, args.c_type,
                                 args.delimiter, args.reverse, args.time_fmt)
        if args.inplace:
            with open(file, 'w') as fout:
                fout.write(convert_to_text(file_data))
        else:
            print_to_std_out(convert_to_text(file_data), file,
                             need_to_mark_filename=len(args.files) > 1)


def check_arguments_show(args) -> None:
    '''Does some early basic checks if the user input is valid.
    If it is not an exception will be raised'''
    if args.c_index is not None and args.c_name is not None:
        raise ValueError("Please define column by index OR by name!")
    if args.c_name is not None and args.no_header:
        raise ValueError(
            "You cannot select column by name if there is no header")
    if args.head is not None and args.head < 0:
        raise ValueError("head value cannot be negative")
    if args.tail is not None and args.tail < 0:
        raise ValueError("tail value cannot be negative")
    has_row_ranges = args.from_row is not None and args.to_row is not None
    has_not_defined_edge = (args.from_row and not args.to_row) or (
        args.to_row and not args.from_row)
    if has_not_defined_edge or (has_row_ranges and len(args.from_row) != len(args.to_row)):
        raise ValueError(
            "For each given `from_row` value one has to set `to_row` value")


def select_from_row(row: str, delimiter: str, col_indexes: List[int]):
    '''Filters the given row in the way, that only the given column indexes are left in it.
       Columns in the row are defined by delimiter.
       Note that the result will be still string with the same delimiter but
       it will contain only the chosen columns
    '''
    l = row.split(delimiter)
    return delimiter.join(l[i] for i in col_indexes)


def apply_show(file_data: FileContent, row_indexes: List[int], col_indexes: List[int],
               delimiter: str) -> FileContent:
    '''Forms new FileContent object which containes only selected column indexes'''
    new_header = None
    if file_data.header:
        new_header = select_from_row(file_data.header, delimiter, col_indexes)
    return FileContent(new_header,
                       tuple(select_from_row(file_data.content[i], delimiter, col_indexes)
                             for i in row_indexes))


def get_column_count(fc: FileContent, delimiter: str) -> int:
    if fc.header is not None:
        return fc.header.count(delimiter) + 1
    if len(fc.content) > 0:
        return fc.content[0].count(delimiter) + 1
    return 1


def expand_int_ranges(ranges: List[Tuple[int]]) -> List[int]:
    '''This function will take a list of ranges (start, end) and expend those into the actual range of integers.
        Note that ranges are semi intervals, start is included and end is not.
        For example, input [(1,2), (4,6)] will be converted into [1, 4, 5].
        Note that function expects the list of ranges to be sorted by the left edge.
        The resulting list will contain only unique integers which are present in at least one of the given ranges.
    '''
    res = []
    for rng in ranges:
        if rng[0] >= rng[1]:
            continue
        if len(res) == 0:
            res.extend(range(rng[0], rng[1]))
        else:
            if res[-1] < rng[0]:
                res.extend(range(rng[0], rng[1]))
            elif res[-1] >= rng[0] and res[-1] + 1 < rng[1]:
                res.extend(range(res[-1]+1, rng[1]))
            else:
                pass
    return res


def get_row_indexes(total_row_count: int, head: int, tail: int,
                    from_index: List[int], to_index: List[int]) -> List[int]:
    '''This function will return list of row indexes based of head and tail counters.
       Returned values will be normalized to the size of the table and in case when
       they should be combined function will guarantee that indexes in the returned 
       list will be unique and will not crossect.
    '''
    if head is None and tail is None and from_index is None:
        return expand_int_ranges([(0, total_row_count)])

    ranges = []
    if head is not None:
        ranges.append((0, min(head, total_row_count)))
    if tail is not None:
        ranges.append((max(0, total_row_count - tail), total_row_count))
    if from_index is not None:
        ranges.extend(zip(from_index, to_index))
    ranges.sort(key=lambda x: x[0])
    return expand_int_ranges(ranges)


def callback_show(args):
    '''Performes columns selection from file according the the given arguments'''
    check_arguments_show(args)
    no_columns_set = args.c_index is None and args.c_name is None
    for file in args.files:
        file_data = read_file(file, not args.no_header)
        col_index = list(range(0, get_column_count(file_data, args.delimiter)))
        if not no_columns_set:
            col_index = get_col_indexes(args.c_index, file_data.header,
                                        args.c_name, args.delimiter)
        row_indexes = get_row_indexes(
            len(file_data.content), args.head, args.tail, args.from_row, args.to_row)
        file_data = apply_show(file_data, row_indexes,
                               col_index, args.delimiter)
        print_to_std_out(convert_to_text(file_data), file,
                         need_to_mark_filename=len(args.files) > 1)


def setup_parser(parser):
    '''Declares CLI parameters of the script'''
    subparsers = parser.add_subparsers(title="Chose operation to perform")

    file_params = argparse.ArgumentParser(add_help=False)
    file_params.add_argument("-d", "--delimiter", action="store", type=str, default=DEFAULT_TABLE_DELIMITER,
                             help="Delimiter, which separates columns in the file")
    file_params.add_argument("-f", "--files", nargs="+", action="store",
                             help="Files with table data on which we want to perform an operation")
    file_params.add_argument("--no_header", action=DEFAULT_NO_HEADER_ACTION,
                             help="If set table will be considered as the one without header.")

    column_selector = argparse.ArgumentParser(add_help=False)
    column_selector.add_argument("-cn", "--c_name", action="append",
                                 default=DEFAULT_COLUMN_NAME_LIST, type=str,
                                 help="Column name on which we want to perform an operation")
    column_selector.add_argument("-ci", "--c_index", action="append", type=int,
                                 default=DEFAULT_COLUMN_INDEX_LIST,
                                 help="Column index on which we want to perform an operation, starts from 0.")

    inplace_argument = argparse.ArgumentParser(add_help=False)
    inplace_argument.add_argument("-i", "--inplace", action=DEFAULT_INPLACE_ACTION,
                                  help="If set the operation will be performed inplace")

    sort_parser = subparsers.add_parser("sort", parents=[file_params, column_selector, inplace_argument],
                                        help="Allows to sort rows according to data in certain columns",
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    sort_parser.add_argument("-as", "--c_type", action="append",
                             default=DEFAULT_COLUMN_TYPE_LIST,
                             choices=[el.value for el in ColumnType],
                             help="Sets type of the values in the chosen column. "
                             "If nothing is set all column values will be interpreted as numbers")
    sort_parser.add_argument("-t_fmt", "--time_fmt", action="store", default=DEFAULT_TIME_FORMAT,
                             help="time string format which will be used in order to parse time values")
    sort_parser.add_argument("-r", "--reverse", action=DEFAULT_SORT_REVERSE_ACTION,
                             help="If set sorting order will be reversed - the first element will be the largest one.")
    sort_parser.set_defaults(callback=callback_sort)

    show_parser = subparsers.add_parser("show", parents=[file_params, column_selector],
                                        help="Allows to selectively show table content",
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    show_parser.add_argument("--head", action="store", type=int, default=DEFAULT_SHOW_HEAD_NUMBER,
                             help="Will display given number of top rows in the table")
    show_parser.add_argument("--tail", action="store", type=int, default=DEFAULT_SHOW_TAIL_NUMBER,
                             help="Will display given number of bottom rows in the table")
    show_parser.add_argument("--from_row", "-fr", action="append", type=int,
                             default=DEFAULT_SHOW_FROM_ROW,
                             help="Will display all rows between the given row number and the next 'to_row' number. "
                                  "The given row number is included into the displayed range. "
                                  "Note that header, if present, is not taken into account in row counting")
    show_parser.add_argument("--to_row", "-tr", action="append", type=int,
                             default=DEFAULT_SHOW_TO_ROW,
                             help="Will display all rows between the previously set `from_row` value and the given value. "
                                  "The given row number is NOT included into the displayed range."
                                  "Note that header, if present, is not taken into account in row counting")

    show_parser.set_defaults(callback=callback_show)


def main():
    parser = argparse.ArgumentParser(prog="Table",
                                     description="Script for performing different operations on the csv table",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    setup_parser(parser)
    arguments = parser.parse_args()
    arguments.callback(arguments)


if __name__ == "__main__":
    main()
