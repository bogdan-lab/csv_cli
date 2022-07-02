import argparse


def callback_sort(args):
    pass



def setup_parser(parser):
    '''Declares CLI parameters of the script'''
    subparsers = parser.add_subparsers(title="Chose operation to perform")

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("-d", action="store", type=str, default='\t',
                               help="Delimiter, which separates columns in the file")

    sort_parser = subparsers.add_parser("sort", parents=[parent_parser],
                                        help="allows to sort rows according to data in certain columns",
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    sort_parser.add_argument("--c_name", action="store", default=None,
                             help="Column name according to which we want to sort data")
    sort_parser.add_argument("--c_index", action="store", default=None,
                             help="Column index according to which we want to sort data, starts from 0.")
    sort_parser.add_argument("--as", action="store", default="string",
                             choices=["string", "number", "time"],
                             help="Sets type of the values in the chosen column")
    sort_parser.add_argument("-i", action="store_true",
                             help="If set sorting will be performed inplace")
    sort_parser.add_argument("-r", action="store_true",
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