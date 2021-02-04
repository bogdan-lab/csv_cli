import pandas as pd
import numpy as np




if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_csv")
    parser.add_argument("-o", "--output_txt")
    parser.add_argument("-x", "--xlabel", default="Time", help="[def = 'Time']")
    parser.add_argument("-y", "--ylabel")
    args = parser.parse_args()
    
    data = pd.read_csv(args.input_csv)
    data = np.column_stack((data[args.xlabel].values, data[args.ylabel].values))
    
    name = args.output_txt
    if name[-4:]!=".txt":
        name+=".txt"
    np.savetxt(name, data, fmt="%.10e", delimiter='\t', header="%s\t%s" % (args.xlabel, args.ylabel))
    
    
    
    