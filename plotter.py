#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt


if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs='+', help="File names with data columns")
    parser.add_argument("-c", "--columns", type=str, default='0 1', help="x and y column indexes in file, [def = '0 1']")
    parser.add_argument('-d', '--delimiter', type=str, default='\t', help="delimiter used in files [def = '\t']")
    parser.add_argument('-ll', '--legend_loc', type=int, default=0, help="legend location id [def = 0]")
    args = parser.parse_args()
    
    cols = args.columns.split(' ')
    cols[0] = int(cols[0])
    cols[1] = int(cols[1])
    
    plt.figure()
    plt.grid()
    for file in args.files:
        data = np.loadtxt(file, delimiter=args.delimiter, usecols=cols)
        plt.plot(data[:,0], data[:,1], label=file)
    plt.legend(loc=args.legend_loc)
    plt.show()
