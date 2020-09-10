import numpy as np
import h5py
import os
#from numba import njit

#@njit
def index(X, value):
     index1 = 0
     index2 = len(X)-1
     while( ( index2 - index1 ) > 1 ):    
         tmp_index = index1 + (index2 - index1) // 2
         if(value > X[tmp_index]):
             index1=tmp_index        
         else:
             index2=tmp_index
     if(X[index1] == value):        
         return index1
     if(X[index2] == value):
         return index2
     raise ValueError

#@njit
def mk_face_area(mfaces, points, pidx):
    area = np.zeros(len(mfaces))
    for fi in range(len(mfaces)):
        face = mfaces[fi]
        p1 = index(pidx,face['pidx1'])
        p2 = index(pidx,face['pidx2'])
        p3 = index(pidx,face['pidx3'])
        
        a = np.zeros(3)
        b = np.zeros(3)
         
        a[0] = points[p1]['x'] - points[p3]['x']
        a[1] = points[p1]['y'] - points[p3]['y']
        a[2] = points[p1]['z'] - points[p3]['z']
        b[0] = points[p2]['x'] - points[p3]['x']
        b[1] = points[p2]['y'] - points[p3]['y']
        b[2] = points[p2]['z'] - points[p3]['z']
        
        c = np.zeros(3)
         
        c[0] =  a[1] * b[2] - a[2] * b[1];
        c[1] = -a[0] * b[2] + a[2] * b[0];
        c[2] =  a[0] * b[1] - a[1] * b[0];
         
        area[fi] = 0.5 * np.sqrt(c[0] * c[0] + c[1]*c[1] + c[2]*c[2])
    return area



def load_particles(pn, stat_file, surface):
    Vx = stat_file[surface][pn]['Vx'][:]
    Vy = stat_file[surface][pn]['Vy'][:]
    Vz = stat_file[surface][pn]['Vz'][:]
    w = stat_file[surface][pn]['w'][:]
    t = stat_file[surface][pn]['t'][:]
    fidx = stat_file[surface][pn]['face_idx'][:]
    data = np.column_stack((Vx,Vy,Vz,w,t,fidx))
    data = data.tolist()
    data.sort(key=lambda x: x[-1])
    return np.array(data)

#@njit
def get_left_boundary_EXACT(fidx_data, given_fidx):
    idx1 = 0
    idx2 = len(fidx_data)-1
    while idx2-idx1>1:
        tmp_idx = idx1 + (idx2 - idx1)//2
        if given_fidx>fidx_data[tmp_idx]:
            idx1 = tmp_idx
        else:
            idx2 = tmp_idx
    if fidx_data[idx1]==given_fidx:
        return idx1
    if fidx_data[idx2]==given_fidx:
        return idx2
    return None

#@njit
def get_right_boundary_EXACT(fidx_data, given_fidx):
    idx1 = 0
    idx2 = len(fidx_data)-1
    while idx2-idx1>1:
        tmp_idx = idx1 + (idx2 - idx1)//2
        if given_fidx>=fidx_data[tmp_idx]:
            idx1 = tmp_idx
        else:
            idx2 = tmp_idx
    if fidx_data[idx1]==given_fidx:
        return idx1+1
    if fidx_data[idx2]==given_fidx:
        return idx2+1
    raise None
    

def get_E_avg_with_time(time_bins, E, pt_times, pt_weights):
    w_hist, bins = np.histogram(pt_times, bins=time_bins, weights=pt_weights)
    Ew_hist, bins = np.histogram(pt_times, bins=time_bins, weights=E*pt_weights)
    E_avg = np.zeros(len(time_bins)-1)
    for i in range(len(time_bins)-1):
        if w_hist[i]!=0:
            E_avg[i] = Ew_hist[i]/w_hist[i]
    return E_avg


def write_vtk_data(out_dir, times, surface, points, faces, all_data):
    print("Writing vtk")
    for ti in range(len(times)):
        t = times[ti]
        name = "%s/%s_%i.vtk" % (out_dir, surface, int(t*1e10))
        print(name)
        f = open(name, "w")
        f.write("# vtk DataFile Version 3.0\n")
        f.write("time = %.6e s\n" % t)
        f.write("ASCII\n")
        f.write("DATASET UNSTRUCTURED_GRID\n")
        f.write('POINTS %i FLOAT\n' % len(points)) 
        for i in range(len(points)):
            f.write('%e %e %e \n' % (points[i]['x'],points[i]['y'],points[i]['z']))
        f.write('\nCELLS %i %i\n' % (len(faces), len(faces) * 4 ))
        pidx = points[:]['pidx']
        for i in range(len(faces)):
            f.write('3 %i %i %i \n' % (index(pidx,faces[i]['pidx1']),index(pidx,faces[i]['pidx2']),index(pidx,faces[i]['pidx3'])))
        f.write('\nCELL_TYPES %i\n' % (len(faces)) )
        for i in range(len(faces)):
            f.write('5 \n')
        f.write("\nCELL_DATA %i\n" % len(faces));
        for pt in all_data.keys():
            for par in all_data[pt].keys():
                field_name = "%s_%s" % (pt, par)
                f.write("SCALARS %s float\n" % field_name);
                f.write("LOOKUP_TABLE default\n");
                for dxi in range(len(faces["face_idx"])):
                    fidx = faces["face_idx"][dxi]
                    f.write("%e\n" % all_data[pt][par][fidx][ti])
        f.close()
    return 0


def filter_time_particles(particles, time_end):
    arr = []
    for pt in particles:
        if pt[-2]<time_end:
            arr.append(pt)
    return np.array(arr)
    
    

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-dt", "--dt", type=float, default=100e-9, help="Time step IN SECONDS for reading statistics [def=100e-9]")
    parser.add_argument("-t", "--time", type=float, default=500e-9, help="Time until which statistics will be read IN SECONDS [def=500e-9]")
    parser.add_argument("-fmf", "--face_file", type=str, default="face_map.h5", help="Face map file [def='face_map.h5']")
    parser.add_argument("-sf", "--surface_file", type=str, default="surface_stat.h5", help="Surface stat file [def='surface_stat.h5']")
    parser.add_argument("-s", "--surface", type=str, default='reticle', help="surface name for which statistics will be plotted")
    parser.add_argument("-od", "--out_dir", type=str, default='', help="Directory where generated vtk will be saved. [def - the name of the surface]")
    parser.add_argument("-xp", "--xp", type=str, default='', help="list of particles (separated by ;) which will be ignored during statistics plot [def = '']")
    args = parser.parse_args()
    
    DT = float(args.dt)
    T_END = float(args.time)
    time_bins = np.arange(0, T_END+DT, DT)
    times = np.arange(0.5*DT, T_END, DT)
    face_map_file = args.face_file
    surface = args.surface
    surface_stat_file = args.surface_file
    OUT_DIR = args.surface
    if len(args.out_dir)>0:
        OUT_DIR = args.out_dir
    os.mkdir(OUT_DIR)
    
    face_map = h5py.File(face_map_file, 'r')
    points        = face_map[surface]['points'][:]
    faces_struct  = face_map[surface]['faces'][:]
    pidx          = points[:]['pidx']
    surf_areas    = mk_face_area(faces_struct,points,pidx)
    stat_file = h5py.File(surface_stat_file,'r')
    pnames = list(stat_file[surface].keys())
    if len(args.xp)>0:
        xp_pt = (args.xp).replace(' ', '').split(';')
        for pt in xp_pt:
            if pt in pnames:
                pnames.remove(pt)
    
    all_data = {}
    print("Collecting statistics")
    for pn in pnames:
        print("%s" % pn)
        particles = load_particles(pn, stat_file, surface)  #[Vx,Vy,Vz,w,t,fidx]
        particles = filter_time_particles(particles, T_END)
        all_data[pn] = {}
        all_data[pn]["flux"] = {}
        all_data[pn]["E_avg"] = {}
        for i in range(len(faces_struct["face_idx"])):
            fidx = faces_struct["face_idx"][i]
            all_data[pn]["flux"][fidx] = np.zeros(len(times))
            all_data[pn]["E_avg"][fidx] = np.zeros(len(times))
        for i in range(len(faces_struct["face_idx"])):
            fidx = faces_struct["face_idx"][i]
            begin = get_left_boundary_EXACT(particles[:,-1], fidx)
            if begin!=None:
                end = get_right_boundary_EXACT(particles[:,-1], fidx)
                this_pt = particles[begin:end]
                #calculating flux
                hist, bins = np.histogram(this_pt[:,-2], bins=time_bins, weights=this_pt[:,-3])
                hist /= surf_areas[i]
                hist /= DT
                all_data[pn]["flux"][fidx] = hist     #in 1/(cm^2*s)
                #Calculating energy
                mass = stat_file[surface][pn].attrs["mass"]
                E = 0.5*(this_pt[:,0]**2 + this_pt[:,1]**2 + this_pt[:,2]**2)*mass*6.2415e11      #eV
                all_data[pn]["E_avg"][fidx] = get_E_avg_with_time(time_bins, E, this_pt[:,-2], this_pt[:,-3])
    
    write_vtk_data(OUT_DIR, times, surface, points, faces_struct, all_data)        


























































