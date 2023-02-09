
from typing import NamedTuple, Optional, Tuple


class FileContent(NamedTuple):
    header: Optional[str]
    content: Tuple[str]


def convert_to_text(file_data: FileContent, hide_header: bool) -> str:
    '''Puts all data from the file content class into single string.
    If hide_header is True there will be no header in the result
    regardless whether there was any header initially.
    '''
    # Here I do not consider empty line in header as a valid header
    # and allow to throw it away in the text generation
    header = None if hide_header else file_data.header
    if not header and not file_data.content:
        # empty file case
        return ""
    elif header and not file_data.content:
        # Header only case
        return header
    elif not header and file_data.content:
        # File without header
        return '\n'.join(file_data.content)
    else:
        # File with header and content
        return '\n'.join((header, *file_data.content))


def read_file(filename: str, has_header: bool) -> FileContent:
    '''Converts the content of the given file into an instance of the FileContent
    '''
    with open(filename, 'r') as fin:
        header = None
        if has_header:
            header = fin.readline().rstrip('\n')
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


def print_table(file_data: FileContent, filename: str,
                need_to_mark_filename: bool, inplace: bool,
                hide_header: bool) -> None:
    '''Saves the table content into the file or prints it into the stdout
    according to the given parameters.
    need_to_mark_filename is relevant only for printing into std out case.
    If it is true than the file content will be prepended by the file name.
    '''
    if inplace:
        with open(filename, 'w') as out:
            out.write(convert_to_text(file_data, hide_header=False))
        return
    print_to_std_out(convert_to_text(file_data, hide_header), filename,
                     need_to_mark_filename)
