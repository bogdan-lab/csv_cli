from argparse import Namespace

from typing import Iterable
from pathlib import Path

from csv_defaults import *


def create_file(file_path: Path, content: Iterable) -> Path:
    '''Creates file in file_path, fills it with a content
    and returns the path to the filled file'''
    file_path.touch()
    with open(file_path, 'w') as out:
        out.write('\n'.join(content))
    return file_path


def convert_argparse_action_to_bool(action: str) -> bool:
    return not action == "store_true"


def create_default_file_params() -> Namespace():
    args = Namespace()
    args.delimiter = DEFAULT_TABLE_DELIMITER
    args.no_header = convert_argparse_action_to_bool(
        DEFAULT_NO_HEADER_ACTION)
    return args


def create_default_column_selector() -> Namespace():
    args = Namespace()
    args.c_name = DEFAULT_COLUMN_NAME_LIST
    args.c_index = DEFAULT_COLUMN_INDEX_LIST
    return args


def create_default_inplace_argument() -> Namespace:
    args = Namespace()
    args.inplace = convert_argparse_action_to_bool(
        DEFAULT_INPLACE_ACTION)
    return args


def create_default_hide_header_argument() -> Namespace:
    args = Namespace()
    args.hide_header = convert_argparse_action_to_bool(
        DEFAULT_HIDE_HEADER_ACTION)
    return args


def merge_args(*seq) -> Namespace:
    total = {}
    for val in seq:
        total.update(vars(val))
    return Namespace(**total)
