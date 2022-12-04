import argparse
from typing import Tuple, Any, NamedTuple, Optional, List
import datetime
from enum import Enum

DEFAULT_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class ColumnType(Enum):
    STRING = "string"
    NUMBER = "number"
    TIME = "time"


class FileContent(NamedTuple):
    header: Optional[str]
    content: Tuple[str]


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
            return float(value)
        elif v_type is ColumnType.STRING:
            return value
        elif v_type is ColumnType.TIME:
            return datetime.datetime.strptime(value, self.time_fmt)
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
        if len(args.c_name) != len(args.c_type):
            raise ValueError("Number of columns should be equal to number of"
                             " provided number of column types")
        if not args.header:
            raise ValueError("If columns index is set by its name, header"
                             " options should be on!")
    if args.c_name is None:
        if len(args.c_index) != len(args.c_type):
            raise ValueError("Number of columns should be equal to number of"
                             " provided number of column types")


def callback_sort(args):
    '''Performes sorting files on the command line request'''
    check_arguments(args)
    for file in args.files:
        file_data = read_file(file, args.header)
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


def setup_parser(parser):
    '''Declares CLI parameters of the script'''
    subparsers = parser.add_subparsers(title="Chose operation to perform")

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("-d", "--delimiter", action="store", type=str, default='\t',
                               help="Delimiter, which separates columns in the file")
    parent_parser.add_argument("-f", "--files", nargs="+", action="store",
                               help="Files with table data which are needed to be sorted")
    parent_parser.add_argument("--header", action="store_false",
                               help="If set table will be considered as the one without header.")

    sort_parser = subparsers.add_parser("sort", parents=[parent_parser],
                                        help="allows to sort rows according to data in certain columns",
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    sort_parser.add_argument("-cn", "--c_name", nargs="+", action="store",
                             default=None, type=str,
                             help="Column name according to which we want to sort data")
    sort_parser.add_argument("-ci", "--c_index", nargs="*", action="store", type=int,
                             default=None,
                             help="Column index according to which we want to sort data, starts from 0.")
    sort_parser.add_argument("-as", "--c_type", nargs="+", action="store",
                             default="string",
                             choices=[el.value for el in ColumnType],
                             help="Sets type of the values in the chosen column")
    sort_parser.add_argument("-t_fmt", "--time_fmt", action="store", default=DEFAULT_TIME_FORMAT,
                             help="time string format which will be used in order to parse time values")
    sort_parser.add_argument("-i", "--inplace", action="store_true",
                             help="If set sorting will be performed inplace")
    sort_parser.add_argument("-r", "--reverse", action="store_true",
                             help="If set sorting order will be reversed - the first element will be the smallest one.")
    sort_parser.set_defaults(callback=callback_sort)


def main():
    parser = argparse.ArgumentParser(prog="Table",
                                     description="Script for performing different operations on the csv table",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    setup_parser(parser)
    arguments = parser.parse_args()
    arguments.callback(arguments)


if __name__ == "__main__":
    main()
