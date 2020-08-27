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
    x = pt_data[ptype]['x'][:]
    y = pt_data[ptype]['y'][:]
    z = pt_data[ptype]['z'][:]
    Vx = pt_data[ptype]['Vx'][:]
    Vy = pt_data[ptype]['Vy'][:]
    Vz = pt_data[ptype]['Vz'][:]
    w = pt_data[ptype]['w'][:]
    t = pt_data[ptype]['t'][:]
    for i in range(len(z)):
        data.append([x[i], y[i], z[i], Vx[i], Vy[i], Vz[i], w[i], t[i]])
    FILE.close()
    return data


def check_val_in_range(val, rng):
    return (val>rng[0] and val<rng[1])


def check_particle(pt, bnd_x, bnd_y, bnd_z):
    if not check_val_in_range(pt[0], bnd_x):
        return False
    if not check_val_in_range(pt[1], bnd_y):
        return False
    if not check_val_in_range(pt[2], bnd_z):
        return False
    return True


def filter_particles(data, bnd_x, bnd_y, bnd_z):
    arr = []
    for i in range(len(data)):
        if check_particle(data[i], bnd_x, bnd_y, bnd_z):
            arr.append(data[i])
    return np.array(arr)


def mk_array_from_hist(hist, bins):
    arr = [[bins[0], hist[0]]]
    for i in range(1, len(bins)-1):
        arr.append([bins[i], hist[i-1]])
        arr.append([bins[i], hist[i]])
    arr.append([bins[-1], hist[-1]])
    return np.array(arr)


def convert_coor_ranges(dx, dy, dz):
    dx = dx.split(';')
    dy = dy.split(';')
    dz = dz.split(';')
    for i in range(2):
        dx[i] = float(dx[i])
        dy[i] = float(dy[i])
        dz[i] = float(dz[i])
    return (dx, dy, dz)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s'  ,'--species'     ,action='store', default='H+;H2+;H3+', help='list of particles I am interested in [def = "H+;H2+;H3+"]')
    parser.add_argument('-F', '--filter'  , action='store_true', default=False, help='True/False Turn on filter by coordinates [def = False]')
    parser.add_argument('-dx' ,'--dx'     ,action='store', default='-7.0;7.0', help='x interval [def = "-7.0;7.0"]')
    parser.add_argument('-dy' ,'--dy'     ,action='store', default='7.5;9.7', help='y interval [def = "7.5;9.7"]')
    parser.add_argument('-dz' ,'--dz'     ,action='store', default='164.0;165.6', help='z interval [def = "164.0;165.6"]')
    parser.add_argument('-p'  ,'--path'   , action='store', default='particles', help="path to particle dataset in h5 [default = 'particles']") 
    parser.add_argument('-o' ,'--out_file'     ,action='store',default='collected_pt', help='name for output file name [def = collected_pt]')
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()
    
    
    pt_list = args.species.split(';')
    dx, dy, dz = convert_coor_ranges(args.dx, args.dy, args.dz)
    path = args.path.split('/')
    
    for filename in args.files:
        print("PROCESSING FILE\t%s" % filename)
        data = []
        for ptype in pt_list:
            tmp = collect_particles(filename, ptype, path)
            if args.filter:
                tmp = filter_particles(tmp, dx, dy, dz)
            data.extend(tmp)
        np.savetxt(args.out_file + '.txt', data, delimiter='\t', fmt="%.6e", header='x, cm\ty, cm\tz, cm\tVx, cm/s\tVy, cm/s\tVz, cm/s\tw\ttime, s')
    
