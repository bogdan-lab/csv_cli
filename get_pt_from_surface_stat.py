import numpy as np
import h5py


def get_particle_data(file, path):
    dataset = None
    for p in path:
        dataset = file[p]
    if dataset == None:
        raise Warning("Did not found particle dataset")
    return dataset


def collect_particles(filename, ptype, path):
    data = []
    FILE = h5py.File(filename, 'r')
    pt_data = get_particle_data(FILE, path)
    keys = pt_data.keys()
    if ptype not in keys:
        print("Particles %s was not found" % ptype)
        return np.array([])
    x = pt_data[ptype]['x'][:]
    y = pt_data[ptype]['y'][:]
    z = pt_data[ptype]['z'][:]
    Vx = pt_data[ptype]['Vx'][:]
    Vy = pt_data[ptype]['Vy'][:]
    Vz = pt_data[ptype]['Vz'][:]
    w = pt_data[ptype]['w'][:]
    t = pt_data[ptype]['t'][:]
    data = np.column_stack((x, y, z, Vx, Vy, Vz, w, t))
    FILE.close()
    return data


def get_range_filter(column, rng):
    return (column>rng[0])*(column<rng[1])

def filter_particles(data, bnd_x, bnd_y, bnd_z, bnd_t):
    if len(data)==0:
        return data
    x_filter = get_range_filter(data[:,0], bnd_x)
    y_filter = get_range_filter(data[:,1], bnd_y)
    z_filter = get_range_filter(data[:,2], bnd_z)
    t_filter = get_range_filter(data[:,7], bnd_t)
    arr = data[x_filter*y_filter*z_filter*t_filter]
    return arr


def mk_array_from_hist(hist, bins):
    arr = [[bins[0], hist[0]]]
    for i in range(1, len(bins)-1):
        arr.append([bins[i], hist[i-1]])
        arr.append([bins[i], hist[i]])
    arr.append([bins[-1], hist[-1]])
    return np.array(arr)

def convert_range(dx):
    dx = dx.split(' ')
    dx[0] = float(dx[0])
    dx[1] = float(dx[1])
    return dx

def merge_lists(data):
    arr = []
    for k in data.keys():
        arr.extend(data[k])
    return np.array(arr)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s'  ,'--species'     ,action='store', default='H+ H2+ H3+', help='list of particles I am interested in [def = "H+ H2+ H3+"]')
    parser.add_argument('-SP', '--separate', action='store_true', default=False, help="True/False - to save different particles in different files [def = False]")
    parser.add_argument('-F', '--filter'  , action='store_true', default=False, help='True/False Turn on filter by coordinates [def = False]')
    parser.add_argument('-dx' ,'--dx'     ,action='store', default='-7.0 7.0', help='x interval [def = "-7.0 7.0"]')
    parser.add_argument('-dy' ,'--dy'     ,action='store', default='7.5 9.7', help='y interval [def = "7.5 9.7"]')
    parser.add_argument('-dz' ,'--dz'     ,action='store', default='164.0 165.6', help='z interval [def = "164.0 165.6"]')
    parser.add_argument('-dt' ,'--dt'     ,action='store', default='0 20e-6', help='time interval [def = "0 20e-6"]')
    parser.add_argument('-p'  ,'--path'   , action='store', default='particles', help="path to particle dataset in h5 [default = 'particles']") 
    parser.add_argument('-o' ,'--out_file'     ,action='store',default='collected_pt', help='name for output file name [def = collected_pt]')
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()
    
    
    pt_list = args.species.split(' ')
    if args.filter:
        dx = convert_range(args.dx)
        dy = convert_range(args.dy)
        dz = convert_range(args.dz)
        dt = convert_range(args.dt)
    path = args.path.split('/')
    
    for filename in args.files:
        print("PROCESSING FILE\t%s" % filename)
        data = {}
        for ptype in pt_list:
            tmp = collect_particles(filename, ptype, path)
            if args.filter:
                tmp = filter_particles(tmp, dx, dy, dz, dt)
            data[ptype] = tmp
        if args.separate:
            for k in data.keys():
                np.savetxt('%s_%s.txt' % (k, args.out_file), data[k], delimiter='\t', fmt="%.6e", header='x, cm\ty, cm\tz, cm\tVx, cm/s\tVy, cm/s\tVz, cm/s\tw\ttime, s')
        else:
            res = merge_lists(data)
            np.savetxt('%s.txt' % (args.out_file), res, delimiter='\t', fmt="%.6e", header='x, cm\ty, cm\tz, cm\tVx, cm/s\tVy, cm/s\tVz, cm/s\tw\ttime, s')