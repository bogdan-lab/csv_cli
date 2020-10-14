#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt


def get_weights(weight_col, data):
    weights = None
    if weight_col>0:
        weights = data[:, weight_col]
    return weights

def convert_hist_to_points(bins_edges,hist):
    Y = np.zeros(2*len(hist))
    X = np.zeros(2*len(hist))    
    for i in range(len(hist)):
        Y[2 * i    ] = hist[i]
        Y[2 * i + 1] = hist[i]
        X[2 * i    ] = bins_edges[i]
        X[2 * i + 1] = bins_edges[i + 1]
    return np.column_stack((X, Y))

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs='+', help="File names with data columns")
    parser.add_argument("-v", "--val_col", type=int, default=0, help="index of column WITH VALUES FOR HIST [def = 0]")
    parser.add_argument("-w", "--weight_col", type=int, default=-1, help="index of column WITH WEIGHTS. If negative - ignored [def = -1]")
    parser.add_argument("-b", "--bins", type=int, default=50, help="number of bins [def = 50]")
    parser.add_argument('-d', '--delimiter', type=str, default='\t', help="delimiter used in files [def = '\t']")
    parser.add_argument('-r', '--range', type=str, default='', help="Range forp plotting histogram SPACE SEPARATED [def = '']")
    parser.add_argument('-ll', '--legend_loc', type=int, default=0, help="legend location id [def = 0]")
    parser.add_argument('-ot', '--out_tag', type=str, default='', help="out file tag for the txt file name [def='']")
    parser.add_argument('-S', '--save_hist', action='store_true', default=False, help='True/False for saving histogram as a data [def=False]')
    parser.add_argument('-C', '--accumulate', action='store_true', default=False, help='True/False for data accumulation [def=False]')
    parser.add_argument('-N', '--normalize', action='store_true', default=False, help='True/False histogram normalization [def=False]')
    parser.add_argument('-sF', '--show_fig', action='store_true', default=False, help='True/False show and figure [def=False]')
    args = parser.parse_args()
    
    hist_range = None
    if len(args.range)>0:
        hist_range = args.range.split(' ')
        hist_range[0] = float(hist_range[0])
        hist_range[1] = float(hist_range[1])
    
    plt.figure()
    plt.grid()
    plt.title("Vcol=%i ; Wcol=%i" % (args.val_col, args.weight_col))
    for file in args.files:
        data = np.loadtxt(file, delimiter=args.delimiter)
        weights = get_weights(args.weight_col, data)
        res_arr, res_bins, empty = plt.hist(data[:,args.val_col], 
                                             bins  = args.bins, 
                                             range = hist_range,
                                             density = args.normalize, 
                                             weights = weights,
                                             cumulative = args.accumulate,
                                             histtype = 'step',
                                             lw = 1.5,
                                             label = file[:-4])
        hist = convert_hist_to_points(res_bins, res_arr)
        header = "Hist was obtained from\nFILE: %s\nVALUE_COL_IDX = %i\nWEIGHT_COL_IDX = " % (file, args.val_col)
        if args.weight_col<0:
            header += "None"
        else:
            header += "%i" % args.weight_col
        if args.save_hist:
            np.savetxt('HIST_%s_%s.txt' % (args.out_tag, file), hist, fmt='%.6e', delimiter='\t', header=header)
    plt.legend(loc=args.legend_loc)
    if(args.show_fig):
        plt.show()
