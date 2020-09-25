import vtk
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy


def reshape_cells(cells):
    '''convert vet 1D array into cell_id -> points dictionary'''
    cell_dict = {}
    idx = 0
    curr_cell_id = 0
    while(idx<len(cells)):
        n = cells[idx]
        idx+=1
        cell_dict[curr_cell_id] = []
        for i in range(idx, idx+n):
            cell_dict[curr_cell_id].append(cells[i])
        idx+=n
        curr_cell_id += 1
    return cell_dict



def read_vtk_struct(filename):
    reader = vtk.vtkDataSetReader()
    reader.SetFileName(filename)
    reader.ReadAllFieldsOn() 
    reader.Update()
    polydata = reader.GetOutput()
    points = vtk_to_numpy(polydata.GetPoints().GetData())
    cells = vtk_to_numpy(polydata.GetCells().GetData())
    cells = reshape_cells(cells)
    return cells, points


def check_cell_in_area(c, points, x_bnd, y_bnd, z_bnd):
    x_pts = []
    y_pts = []
    z_pts = []
    for p_idx in c:
        x_pts.append(points[p_idx][0])
        y_pts.append(points[p_idx][1])
        z_pts.append(points[p_idx][2])
    if max(x_pts)>max(x_bnd) or min(x_pts)<min(x_bnd):
        return False
    if max(y_pts)>max(y_bnd) or min(y_pts)<min(y_bnd):
        return False
    if max(z_pts)>max(z_bnd) or min(z_pts)<min(z_bnd):
        return False
    return True

def read_bnd(arg):
    arr = arg.split(" ")
    arr[0] = float(arr[0])
    arr[1] = float(arr[1])
    return arr

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', '-i', default='pellicle.vtk', help='input vtk file [def = "pellicle.vtk"]')
    parser.add_argument('--output_file', '-o', default='', help='output file name where cell ids will be saved [def = ""]')
    parser.add_argument('--x_bnd', '-x', type=str, default='-1 1', help='range along x coordinate [def = "-1 1"]')
    parser.add_argument('--y_bnd', '-y', type=str, default='12 12.4', help='range along y coordinate [def = "12 12.4"]')
    parser.add_argument('--z_bnd', '-z', type=str, default='164 165', help='range along z coordinate [def = "164 165"]')
    args = parser.parse_args()
    
    cells, points = read_vtk_struct(args.input_file)
    
    x_bnd = read_bnd(args.x_bnd)
    y_bnd = read_bnd(args.y_bnd)
    z_bnd = read_bnd(args.z_bnd)
    
    ids = []
    for k in cells.keys():
        if check_cell_in_area(cells[k], points, x_bnd, y_bnd, z_bnd):
            ids.append(k)
            
    ids_string = ""
    for i in ids:
        ids_string += str(i) + " "
    
    if(args.output_file):
        f = open(args.output_file, "w")
        f.write("%s" % ids_string)
        f.close()
    else:
        print(ids_string)
    
    
    
    
    
    
    
    
    
    
