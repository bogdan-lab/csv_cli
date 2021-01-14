import argparse
import numpy as np

def get_header(args):
    header = ""
    for i_file in args.input_files:
        f = open(i_file, "r")
        fst_line = f.readline()
        if fst_line[0]=="#":
            header = fst_line
        f.close()
    return header

def direct_copy(input_files, fout):
    for i_file in input_files:
        f = open(i_file, "r")
        for line in f:
            if line[0]=="#":
                continue
            fout.write(line)
        f.close()
    return 0

def sorted_num_copy(input_files, sort_idx, delimiter, fout):
    data = []
    for i_file in input_files:
        f_cont = np.loadtxt(i_file, delimiter=delimiter)
        for i in range(len(f_cont)):
            data.append(f_cont[i])
    data.sort(key=lambda x: x[sort_idx])
    for i in range(len(data)):
        line = ""
        for j in range(len(data[i])-1):
            line += "%.18e%s" % (data[i][j], delimiter)
        line += "%.18e\n" % data[i][len(data[i])-1]
        fout.write(line)
    return 0

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('input_files', nargs="+")
    parser.add_argument('-o', "--output_file", default="stacked_files.txt", help='merged file')
    parser.add_argument('--sort_idx', default=None, type=int, help="column index which should be sorted in the final file [def=None - ignore this setting]")
    parser.add_argument('-d', "--delimiter", default='\t', help="delimiter to separate numerical data [def = <tab>]")
    args = parser.parse_args()
    
        
    fout = open(args.output_file, 'w')
    fout.write(get_header(args))
    if args.sort_idx==None:
        direct_copy(args.input_files, fout)
    else:
        sorted_num_copy(args.input_files, args.sort_idx, args.delimiter, fout)
    fout.close()