import os
import argparse
import re
import numpy as np
import bisect



def get_save_interval(t):
    T  = [0.0 , 100.0, 500.0 , 1000.0, 2000.0, 5000.0, 10000.0, 20000.0 ]
    dt = [10.0, 10.0 , 50.0  , 100.0 , 200.0 ,  500.0, 1000.0 ,  1000.0 ]
    n = bisect.bisect_left(T,t)
    return dt[n]


def check_file(fname, np_pt_file_flag, no_snap_file_flag):
    if (re.findall('particles_(.*)\.h5',fname)) and not np_pt_file_flag:
        return True
    if (re.findall('snapshot_(.*)\.vt[kur]',fname)) and not no_snap_file_flag:
        return True
    return False

def get_time_stamp(fname):
    if(re.findall('particles_(.*)\.h5',f)):
        return 0.1 * float(re.findall('particles_(.*)\.h5',fname)[0]) # time stamp in ns
    if(re.findall('snapshot_(.*)\.vt[kur]',f)):
        return 0.1 * float(re.findall('snapshot_(.*)\.vt[kur]',fname)[0]) # time stamp in ns
    raise Warning("Incorrect file name in get time stamp %s" % fname)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='clean extra files')
    parser.add_argument('-d','--delete' ,action='store_true'  , default=False)
    parser.add_argument('-np','--no_particles' ,action='store_true'  , default=False,
                        help = "True/False - for dont touch particle files [def = 'False']")
    parser.add_argument('-ns','--no_snapshots' ,action='store_true'  , default=False,
                        help = "True/False - for dont touch snapshot files [def = 'False']")
    parser.add_argument("-rr", '--reprate', type=float, action='store', default=20e3,   
                        help="Repetition rate 'def = 20e3'")
    args = parser.parse_args()

l = os.listdir('.')
h5list  = []
vtulist = []
keeplist = []

reprate = 20e3 # in ns

file_list = []
for f in l:
    if check_file(f, args.no_particles, args.no_snapshots):
        timestamp = get_time_stamp(f)
        file_list.append([f, timestamp, False])
file_list.sort(key=lambda x : x[1])
prev_time = file_list[0][1]
for f in file_list:
    time_in_pulse = f[1] - np.floor(f[1] / reprate) * reprate
    dt = get_save_interval(time_in_pulse)
    if( abs(time_in_pulse - prev_time) >= dt):
        prev_time = time_in_pulse
    else:
        f[2] = True

file_list[0 ][2] = False
file_list[-1][2] = False
for f in file_list:
    print(f)


if(args.delete):
    answer = input("append .del files marked with true ? Y/N\t")
    if answer.upper() in ["Y", "YES"]:
        for f in file_list:
            if(f[2]):
                os.rename(f[0],f[0]+'.del')

