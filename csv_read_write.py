
from typing import NamedTuple, Optional, Tuple


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


def read_file(filename: str, has_header: bool) -> FileContent:
    '''Converts the content of the given file into an instance of the FileContent
    Note that in case of empty file function returnes the same output regardless
    the `has_header` value. If the file is empty FileContent.header is None
    and FileContent.content is empty.
    '''
    with open(filename, 'r') as fin:
        header = None
        if has_header:
            header = fin.readline().rstrip('\n')
            if len(header) == 0:
                header = None
        return FileContent(header, tuple(l.rstrip('\n') for l in fin))


def print_to_std_out(content: str, filename: str,
                     need_to_mark_filename: bool) -> None:
    '''Prints file content into stdout, indicating the beginning of the table
       by the table name, if corresponding flag is set
    '''
    if need_to_mark_filename:
        print('\n'.join((f"==> {filename} <==", content, "")))
    else:
        print(content)


def get_column_count(fc: FileContent, delimiter: str) -> int:
    '''Returns the number of columns in the given file content instance
    according to the user provided delimiter. Note that returned column number
    is defined by the header (if one exists) or by the first table row after header.
    Empty file has 0 columns.
    '''
    if fc.header is not None:
        return fc.header.count(delimiter) + 1
    if len(fc.content) > 0:
        return fc.content[0].count(delimiter) + 1
    return 1
