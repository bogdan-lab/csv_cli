import argparse

def get_header(args):
    header = ""
    for i_file in args.input_files:
        f = open(i_file, "r")
        fst_line = f.readline()
        if fst_line[0]=="#":
            header = fst_line
        f.close()
    return header

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('input_files', nargs="+")
    parser.add_argument('-o', "--output_file", default="stacked_files.txt", help='merged file')
    args = parser.parse_args()
    
    
    fout = open(args.output_file, 'w')
    fout.write(get_header(args))
    for i_file in args.input_files:
        f = open(i_file, "r")
        for line in f:
            if line[0]=="#":
                continue
            fout.write(line)
        f.close()
    fout.close()