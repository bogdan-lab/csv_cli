import subprocess
import argparse


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--converter_path', '-cp', help='Path to converter script [no default!]')
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()
    
    for file in args.files:
        status = subprocess.run(['pvpython', args.converter_path, file])
        if status.returncode==0:
            subprocess.run(['rm', file])
        else:
            print("\nSOME ERROR IN CONVERTING OCCURE\n")
            
