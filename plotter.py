#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt


def get_col_nums(args):
    cols = args.columns.split(' ')
    cols[0] = int(cols[0])
    cols[1] = int(cols[1])
    return cols


def get_labels(args):
    labels = ["X coordinate", "Y coordinate"]
    f = open(args.files[0], 'r')
    fst_line = f.readline()
    f.close()
    fst_line = fst_line.replace('\n', '').replace('#', '')
    fst_line = fst_line.split(args.delimiter)
    cols = get_col_nums(args)
    try:
        labels[0] = fst_line[cols[0]]
        labels[1] = fst_line[cols[1]]
    except:
        pass
    return labels


if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs='+', help="File names with data columns")
    parser.add_argument("-c", "--columns", type=str, default='0 1', help="x and y column indexes in file, [def = '0 1']")
    parser.add_argument('-d', '--delimiter', type=str, default='\t', help="delimiter used in files [def = '\t']")
    parser.add_argument('-ll', '--legend_loc', type=int, default=0, help="legend location id [def = 0]")
    parser.add_argument('-o', '--out_file', type=str, default='', help="output_filename, if not given -> graph is not saved")
    args = parser.parse_args()
    
    cols = get_col_nums(args)
    labels = get_labels(args)
    
    plt.figure()
    plt.grid()
    plt.title("Used cols xcol=%i ycol=%i" % (cols[0], cols[1]), pad=15)
    plt.xlabel(labels[0])
    plt.ylabel(labels[1])
    for file in args.files:
        data = np.loadtxt(file, delimiter=args.delimiter, usecols=cols)
        plt.plot(data[:,0], data[:,1], label=file)
    plt.legend(loc=args.legend_loc)
    plt.ticklabel_format(scilimits=(-3, 4), style="sci")
    if args.out_file:
        name = args.out_file if ".png"==args.out_file[:-4] else "%s.png" % args.out_file
        plt.savefig(name, dpi=300)
    plt.show()
