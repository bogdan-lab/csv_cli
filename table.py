import argparse
from typing import Tuple, Any, List, NamedTuple, Optional
import datetime
from enum import Enum


class ColumnType(Enum):
    STRING = "string"
    NUMBER = "number"
    TIME = "time"


class FileContent(NamedTuple):
    header: Optional[str]
    content: List[str]


def fix_new_line(content: List[str]) -> None:
    '''It is not guaranteed that after the last row in the file \n symbol
    will always be present. After sorting, this row will be mixed up with
    others and we will have to move \n symbol from the new last row to the
    one which was placed in the middle of the content
    '''
    for i in range(len(content)):
        if content[i][-1] != '\n':
            content[i] += '\n'
            content[-1] = content[-1][:-1]
            break


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
        fix_new_line(file_data.content)
        return ''.join(file_data.content)
    else:
        # File with header and content
        fix_new_line(file_data.content)
        return ''.join((file_data.header, *file_data.content))


class RowSorter:
    '''Defines the comparator for sorting rows in the file according to the
    arguments passed by user.'''
    def __init__(self, col_index: int, col_type: str, delimiter: str,
                 time_fmt: str) -> None:
        self.col_index = col_index
        self.col_type = ColumnType(col_type)
        self.delimiter = delimiter
        self.time_fmt = time_fmt

    def comparator(self, row: str) -> Tuple[Any]:
        value = row.split(self.delimiter)[self.col_index].strip()
        if self.col_type is ColumnType.NUMBER:
            return (float(value),)
        elif self.col_type is ColumnType.STRING:
            return (value, )
        elif self.col_type is ColumnType.TIME:
            return (datetime.datetime.strptime(value, self.time_fmt), )
        else:
            raise NotImplementedError


def read_file(filename: str, has_header: bool) -> FileContent:
    with open(filename, 'r') as fin:
        header = None
        if has_header:
            header = fin.readline()
        data = [l for l in fin]
        return FileContent(header, data)


def get_col_index_by_name(header: str, col_name: str, delimiter: str) -> int:
    '''Searches for the column name in header and returns the coresponding
    index. Search is case insensitive'''
    name_list = [el.strip() for el in header.casefold().split(delimiter)]
    return name_list.index(col_name.casefold())


def sort_content(file_data: FileContent, col_index: int, col_type: str,
                 delimiter: str, rev_order: bool,
                 time_fmt: str) -> FileContent:
    '''Sorts the content field in the FileContent object according to the
    settings'''
    sorter = RowSorter(col_index, col_type, delimiter, time_fmt)
    return FileContent(file_data.header, sorted(file_data.content,
                                                key=sorter.comparator,
                                                reverse=rev_order))


def get_column_index(arg_index: int, has_header: bool, header: str,
                     arg_col_name: str, arg_delimiter: str) -> int:
    if arg_index is not None:
        return arg_index
    if not has_header:
        raise ValueError("If columns index is set by its name, header options"
                         "should be on!")
    return get_col_index_by_name(header, arg_col_name, arg_delimiter)


def print_to_std_out(content: str, filename: str,
                     need_to_mark_filename: bool) -> None:
    if need_to_mark_filename:
        print('\n'.join((f"==> {filename} <==", content, "")))
    else:
        print(content)


def callback_sort(args):
    if args.c_index is None and args.c_name is None:
        raise ValueError("Column must be specified by name or index!")
    if args.c_index is not None and args.c_name is not None:
        raise ValueError("Please define column by index OR by name!")
    for file in args.files:
        file_data = read_file(file, args.header)
        col_index = get_column_index(args.c_index, args.header,
                                     file_data.header, args.c_name,
                                     args.delimiter)
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
    parent_parser.add_argument("files", nargs="+", action="store",
                               help="Files with table data which are needed to be sorted")
    parent_parser.add_argument("--header", action="store_false",
                               help="If set table will be considered as the one without header.")

    sort_parser = subparsers.add_parser("sort", parents=[parent_parser],
                                        help="allows to sort rows according to data in certain columns",
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    sort_parser.add_argument("--c_name", action="store", default=None,
                             help="Column name according to which we want to sort data")
    sort_parser.add_argument("--c_index", action="store", default=None,
                             help="Column index according to which we want to sort data, starts from 0.")
    sort_parser.add_argument("-as", "--c_type", action="store", default="string",
                             choices=[el.value for el in ColumnType],
                             help="Sets type of the values in the chosen column")
    sort_parser.add_argument("-t_fmt", "--time_fmt", action="store", default="%Y-%m-%d %H:%M:%S",
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