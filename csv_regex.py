from argparse import Namespace
from typing import List
from re import compile, \
    IGNORECASE, \
    Pattern

from csv_read_write import FileContent, \
    read_file, \
    convert_to_text, \
    print_to_std_out
from csv_utility import get_indexes_by_names, \
    has_duplicates


def check_arguments(args: Namespace) -> None:
    '''Performs high level input parameters check and raises
    error if some problem is found
    '''
    if not args.c_name and not args.c_index:
        raise ValueError("No columns were selected.")
    if args.c_name and args.c_index:
        raise ValueError("One should define columns of interest by indexes OR by names."
                         "Simultaneous use of these two flags is not allowed.")
    if args.c_index and any(el < 0 for el in args.c_index):
        raise ValueError("Column index value cannot be negative.")
    if args.c_index and has_duplicates(args.c_index):
        raise ValueError(
            "One can define only one regular expression per one column")
    if args.c_name and has_duplicates(args.c_name):
        raise ValueError(
            "One can define only one regular expression per one column")
    if not args.expression:
        raise ValueError("There is no regular expression to search for.")
    if any(len(el) == 0 for el in args.expression):
        raise ValueError(
            "Empty string is considered to be invalid regular expression.")
    if args.c_index and len(args.c_index) != len(args.expression):
        raise ValueError("The number of given expressions should match the"
                         "number of column indexes.")
    if args.c_name and len(args.c_name) != len(args.expression):
        raise ValueError("The number of given expressions should match the"
                         "number of column names.")


def match_all_regex(line: str, delimiter: str, expressions: List[Pattern],
                    indexes: List[int]) -> bool:
    '''Function returns True if we can find all expressions in the defined column in
    the given line. Function assumes that both (expressions and indexes) lists are
    not empty and have the same length.
    '''
    # Note that we have to form string for each column value, otherwise behavior of
    # `^` symbol is undefined according to the documentation
    data = line.split(delimiter)
    for index, regex in zip(indexes, expressions):
        if index >= len(data):
            raise ValueError(f"There is no {index} column in the row {line}")
        if not regex.search(data[index]):
            return False
    return True


def select_rows(file_data: FileContent, col_indexes: List[int],
                expressions: List[str], delimiter: str) -> FileContent:
    '''Constructs new FileContent instance by selecting only those content rows, which
    contain given expressions in the given columns.
    '''
    return FileContent(file_data.header,
                       tuple(line for line in
                             filter(lambda x: match_all_regex(x, delimiter, expressions, col_indexes),
                                    file_data.content)))


def compile_regex(raw: str, ignore_case: bool) -> Pattern:
    '''Compiles the given regex with appended ignore_case flag if it is necessary.
    If the input string is invalid regular expression, re.error will be raised.
    '''
    return compile(raw, IGNORECASE) if ignore_case else compile(raw)


def callback_regex(args: Namespace) -> None:
    '''Performs filtering table content by regular expressions'''
    check_arguments(args)
    args.expression = list(compile_regex(el, args.ignore_case)
                           for el in args.expression)
    for file in args.files:
        file_data = read_file(file, not args.no_header)
        col_indexes = (args.c_index
                       if args.c_index is not None
                       else get_indexes_by_names(file_data.header, args.delimiter, args.c_name))
        file_data = select_rows(file_data, col_indexes,
                                args.expression, args.delimiter)
    if args.inplace:
        with open(file, 'w') as out:
            out.write(convert_to_text(file_data, hide_header=False))
    else:
        print_to_std_out(convert_to_text(file_data, hide_header=args.hide_header), file,
                         need_to_mark_filename=len(args.files) > 1)
