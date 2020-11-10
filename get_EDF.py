import numpy as np
import h5py
import matplotlib.pyplot as plt
import os

def collect_particles(filename, ptype):
    data = []
    FILE = h5py.File(filename, 'r')
    pt_data = FILE["particles"]
    x = pt_data[ptype]['x'][:]
    y = pt_data[ptype]['y'][:]
    z = pt_data[ptype]['z'][:]
    Vx = pt_data[ptype]['Vx'][:]
    Vy = pt_data[ptype]['Vy'][:]
    Vz = pt_data[ptype]['Vz'][:]
    w = pt_data[ptype]['w'][:]
    data = np.column_stack((x, y, z, Vx, Vy, Vz, w))
    FILE.close()
    return np.array(data)


def get_range_filter(column, rng):
    return (column>rng[0])*(column<rng[1])

def filter_particles(data, bnd_x, bnd_y, bnd_z):
    x_filter = get_range_filter(data[:,0], bnd_x)
    y_filter = get_range_filter(data[:,1], bnd_y)
    z_filter = get_range_filter(data[:,2], bnd_z)
    arr = data[x_filter*y_filter*z_filter]
    return arr


def mk_array_from_hist(hist, bins):
    arr = [[bins[0], hist[0]]]
    for i in range(1, len(bins)-1):
        arr.append([bins[i], hist[i-1]])
        arr.append([bins[i], hist[i]])
    arr.append([bins[-1], hist[-1]])
    return np.array(arr)


def convert_coor_ranges(dx, dy, dz):
    dx = dx.split(' ')
    dy = dy.split(' ')
    dz = dz.split(' ')
    for i in range(2):
        dx[i] = float(dx[i])
        dy[i] = float(dy[i])
        dz[i] = float(dz[i])
    return (dx, dy, dz)


def get_time(filename):
    return int(filename[10:-3])/10    #in ns


def convert_hist_to_points(bins_edges,hist):
    Y = np.zeros(2*len(hist))
    X = np.zeros(2*len(hist))    
    for i in range(len(hist)):
        Y[2 * i    ] = hist[i]
        Y[2 * i + 1] = hist[i]
        X[2 * i    ] = bins_edges[i]
        X[2 * i + 1] = bins_edges[i + 1]
    return np.column_stack((X, Y))


def calc_edf(data, bin_num, ptype, time, tag, folder):
    mass = {"e":9.1e-28, "H+":1.67e-24, "H2+":2*1.67e-24, "H3+":3*1.67e-24}
    energy = 0.5*mass[ptype]*(data[:,3]**2 + data[:,4]**2 + data[:,5]**2)*6.242e11    #in eV
    energy_weight = np.column_stack((energy, data[:,-1]))
    save_edf(energy_weight, bin_num, ptype, time, tag, folder)
    return energy_weight


def save_edf(energy_weight, bin_num, ptype, time, tag, folder):
    plt.figure()
    plt.grid()
    plt.xlabel("energy, eV")
    plt.ylabel("Probability density, 1/eV")
    plt.title("%s; %i ns" % (ptype, time))
    arr, bins, empty = plt.hist(energy_weight[:,0], bins=bin_num, density=True, weights=energy_weight[:,1], histtype="step", lw=1.5)
    plt.yscale("log")
    name = folder + "/EDF_%s_%ins_%s" % (ptype, time, tag)
    plt.savefig(name + ".png", dpi=300)
    plt.close()
    result = convert_hist_to_points(bins, arr)
    np.savetxt(name + ".txt", result, delimiter='\t', fmt="%.6e", header="Energy, eV\tProbability density, 1/eV")
    return 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s'  ,'--species',action='store'     , default='H+ H2+ H3+' , help='list of particles I am interested in [def = "H+ H2+ H3+"]')
    parser.add_argument('-F' ,'--filter'  ,action='store_true', default=False        , help='True/False filter particle according to position or not [def = False]')
    parser.add_argument('-S' ,'--sum'     ,action='store_true', default=False        , help='True/False save summarized EDF for all particles in list [def = False]')
    parser.add_argument('-dx' ,'--dx'     ,action='store'     , default='-7.0 7.0'   , help='x interval [def = "-7.0 7.0"]')
    parser.add_argument('-dy' ,'--dy'     ,action='store'     , default='8 9.5'      , help='y interval [def = "8 9.5"]')
    parser.add_argument('-dz' ,'--dz'     ,action='store'     , default='164.0 165.6', help='z interval [def = "164.0 165.6"]')
    parser.add_argument('-t' ,'--tag'     ,action='store'     , default=''           , help='tag for output file name [def = ""]')
    parser.add_argument('-b' ,'--bins'    ,action='store'     , default=50           , help='number of bins [def = 50]')
    parser.add_argument('-d' ,'--dir'     ,action='store'     , default="EDF"        , help='directory where result files will be saved [def = "EDF"]')
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()
    
    try:
        os.mkdir(args.dir)
    except:
        pass
    
    pt_list = args.species.split(' ')
    bins = int(args.bins)    
    tag = args.tag

    if args.filter:
        dx, dy, dz = convert_coor_ranges(args.dx, args.dy, args.dz)
        tag+="x_%s_y_%s_z_%s" % (args.dx, args.dy, args.dz)
    tag = tag.replace(' ', '_')
    summarized = []
    for filename in args.files:
        print("PROCESSING FILE\t%s" % filename)
        time = get_time(filename)
        for ptype in pt_list:
            data = collect_particles(filename, ptype)
            if args.filter:
                data = filter_particles(data, dx, dy, dz)
            tmp = calc_edf(data, bins, ptype, time, tag, args.dir)
            if args.sum:
                summarized.extend(tmp.tolist())
                tmp = []
        if args.sum:
            summarized = np.array(summarized)
            save_edf(summarized, bins, args.species, time, tag, args.dir)
            
