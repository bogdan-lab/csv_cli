import argparse
from typing import Tuple, Any, List, NamedTuple


class FileContent(NamedTuple):
    header: str
    content: List[str]


class RowSorter:
    '''Defines the comparator for sorting rows in the file according to the
    arguments passed by user.'''
    def __init__(self, col_index: int, col_type: str, delimiter: str) -> None:
        self.col_index = col_index
        self.col_type = col_type
        self.delimiter = delimiter

    def comparator(self, row: str) -> Tuple[Any]:
        value = row.split(self.delimiter)[self.col_index]
        if self.col_type == 'number':
            return (float(value),)
        elif self.col_type == 'string':
            return (value, )
        else:
            raise NotImplementedError


def read_file(filename: str) -> FileContent:
    with open(filename, 'r') as fin:
        header = fin.readline().strip()
        data = [l.strip() for l in fin]
        return FileContent(header, data)


def get_col_index_by_name(header: str, col_name: str, delimiter: str) -> int:
    '''Searches for the column name in header and returns the coresponding
    index. Search is case insensitive'''
    name_list = [el.strip() for el in header.casefold().split(delimiter)]
    return name_list.index(col_name.casefold())


def sort_content(file_data: FileContent, col_index: int, col_type: str,
                 delimiter: str, rev_order: bool) -> FileContent:
    '''Sorts the content field in the FileContent object according to the
    settings'''
    sorter = RowSorter(col_index, col_type, delimiter)
    return FileContent(file_data.header, sorted(file_data.content,
                                                key=sorter.comparator,
                                                reverse=rev_order))


def callback_sort(args):
    if args.c_index is None and args.c_name is None:
        raise ValueError("Column must be specified by name or index!")
    file_data = read_file(args.file)
    if len(file_data.header) == 0 and len(file_data.content) == 0:
        new_data = ""
    elif len(file_data.content) == 0:
        new_data = file_data.header
    else:
        col_index = args.c_index
        if not col_index:
            col_index = get_col_index_by_name(file_data.header, args.c_name,
                                              args.delimiter)
        file_data = sort_content(file_data, col_index, args.c_type,
                                 args.delimiter, args.reverse)
        new_data = '\n'.join((file_data.header, *file_data.content))
    if args.inplace:
        with open(args.file, 'w') as fout:
            fout.write(new_data)
    else:
        print(new_data)


def setup_parser(parser):
    '''Declares CLI parameters of the script'''
    subparsers = parser.add_subparsers(title="Chose operation to perform")

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("-d", "--delimiter", action="store", type=str, default='\t',
                               help="Delimiter, which separates columns in the file")
    parent_parser.add_argument("-f", "--file", action="store",
                               help="File with table data which is needed to be sorted")
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
                             choices=["string", "number", "time"],
                             help="Sets type of the values in the chosen column")
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