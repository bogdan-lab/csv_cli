import numpy as np



def get_header(file):
    header = ""
    f = open(file, "r")
    for line in f:
        if line[0]!="#":
            break
        header += line.replace("#", "")
    f.close()
    return header

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    parser.add_argument("-m", "--multiplier", type=str, default=1, help="[def=1]")
    parser.add_argument("-a", "--addition", type=str, default=0, help="def=0")
    parser.add_argument("-c", "--col_idx", type=str)
    parser.add_argument("--copy", action="store_true", default=False, help="True/False to generate file copy [def=False]")
    args = parser.parse_args()
    
    c = int(args.col_idx)
    m = float(args.multiplier)
    a = float(args.addition)
    for file in args.files:
        header=get_header(file)
        data = np.loadtxt(file)
        data = np.column_stack((data[:,0:c], m*data[:,c]+a, data[:,c+1:]))
        name = file
        if args.copy:
            name = "copy_"+file
        np.savetxt(name, data, fmt="%.10e", delimiter="\t", header=header)
    
    