import numpy as np
import h5py


def collect_particles(filename, ptype):
    FILE = h5py.File(filename, 'r')
    pt_data = FILE['particles']
    if not(ptype in pt_data.keys()):
        return np.array([])
    x = pt_data[ptype]['x'][:]
    y = pt_data[ptype]['y'][:]
    z = pt_data[ptype]['z'][:]
    Vx = pt_data[ptype]['Vx'][:]
    Vy = pt_data[ptype]['Vy'][:]
    Vz = pt_data[ptype]['Vz'][:]
    w = pt_data[ptype]['w'][:]
    data = np.column_stack((x, y, z, Vx, Vy, Vz, w))
    FILE.close()
    return data


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
    parser.add_argument('-ot' ,'--out_file_tag'     ,action='store',default='collected_pt', help='tag which will be added to the out file name [def = collected_pt]')
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()
    
    
    pt_list = args.species.split(' ')
    if args.filter:
        dx, dy, dz = convert_coor_ranges(args.dx, args.dy, args.dz)
    
    for filename in args.files:
        print("PROCESSING FILE\t%s" % filename)
        data = {}
        for ptype in pt_list:
            tmp = collect_particles(filename, ptype)
            if args.filter and len(tmp)>0:
                tmp = filter_particles(tmp, dx, dy, dz)
            data[ptype] = tmp
        if args.separate:
            for k in data.keys():
                np.savetxt('%s_%s_%s.txt' % (k, args.out_file_tag, filename), data[k], delimiter='\t', fmt="%.6e", header='x, cm\ty, cm\tz, cm\tVx, cm/s\tVy, cm/s\tVz, cm/s\tw')
        else:
            res = merge_lists(data)
            np.savetxt('%s_%s.txt' % (args.out_file_tag, filename), res, delimiter='\t', fmt="%.6e", header='x, cm\ty, cm\tz, cm\tVx, cm/s\tVy, cm/s\tVz, cm/s\tw')