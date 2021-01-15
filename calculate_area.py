import gmsh
import numpy as np

def get_area(ncoors):
    a = ncoors[0,:] - ncoors[2,:]
    b = ncoors[1,:] - ncoors[2,:]
    c = np.zeros(3)
    c[0] =  a[1] * b[2] - a[2] * b[1];
    c[1] =- a[0] * b[2] + a[2] * b[0];
    c[2] =  a[0] * b[1] - a[1] * b[0];
    s = 0.5 * np.sqrt(c[0] * c[0] + c[1]*c[1] + c[2]*c[2])
    return s

def get_phys_group_dim_tag(phys_group_name):
    PhysGroups = gmsh.model.getPhysicalGroups()     #(dim, tag) of all groups
    for i in range(len(PhysGroups)):
        dim = PhysGroups[i][0]
        tag = PhysGroups[i][1]
        name = gmsh.model.getPhysicalName(dim, tag)
        if name==phys_group_name:
            return (dim, tag)
    raise Warning("No such physical group %s" % phys_group_name)

def download_elements(phg_dim_tag):
    entity_data = []
    EntitesTags = gmsh.model.getEntitiesForPhysicalGroup(phg_dim_tag[0], phg_dim_tag[1])
    for ent_tg in EntitesTags:
        elementTypes, elementTags, nodeTags = gmsh.model.mesh.getElements(2, ent_tg)
        for i in range(len(elementTypes)):
            if elementTypes[i]==2:    #triangle
                entity_data.append([elementTags[i], nodeTags[i]])  #tags-1 in order to keep node numeration from 0!
            else:
                print('\nBAD ELEMENT TYPES. TYPE = %i\n' % elementTypes[i])
                exit(1)
    return entity_data


def check_val_in_boundary(val, bnd):
    if np.any(bnd==None):
        return True
    return val>=bnd[0] and val<=bnd[1]
    

def check_element_in_boundaries(node_coordinates, x_bnd, y_bnd, z_bnd):
    for p in node_coordinates:
        if not check_val_in_boundary(p[0], x_bnd):
            return False
        if not check_val_in_boundary(p[1], y_bnd):
            return False
        if not check_val_in_boundary(p[2], z_bnd):
            return False
    return True

def calculate_area(entity_data, x_bnd, y_bnd, z_bnd):
    area = 0
    for ElementGroup in entity_data:
        ElementTags, ElementNodes = ElementGroup
        for el_idx in range(len(ElementTags)):
            #collecting nodes in this element
            nodes_in_element = []
            for i in range(3):  #here we still have all quadrangle of the first order
                nodes_in_element.append(ElementNodes[3*el_idx + i])
            #collecting coordinates of this element nodes
            node_coordinates = []
            for n in nodes_in_element:
                coors, empty = gmsh.model.mesh.getNode(n)                                    
                node_coordinates.append(coors)
            node_coordinates = np.array(node_coordinates)
            if check_element_in_boundaries(node_coordinates, x_bnd, y_bnd, z_bnd):
                area += get_area(node_coordinates)
    return area
             

def get_boundary(arg_bnd):
    if arg_bnd==None:
        return None
    bnd = np.zeros(2)
    tmp_0 = float(arg_bnd.split(" ")[0])
    tmp_1 = float(arg_bnd.split(" ")[1])
    bnd[0] = min(tmp_0, tmp_1)
    bnd[1] = max(tmp_0, tmp_1)
    return bnd

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mesh_file", action='store', default="mesh.msh", help="def = 'mesh.msh'")
    parser.add_argument("-n", "--group_name", action='store', default="reticle_FS", help="def = 'reticle_FS'")
    parser.add_argument("-dx", action='store', default=None, help="x boundaries of area of interest; format 'lhs rhs' [def=None - no restriction]")
    parser.add_argument("-dy", action='store', default=None, help="y boundaries of area of interest; format 'lhs rhs' [def=None - no restriction]")
    parser.add_argument("-dz", action='store', default=None, help="z boundaries of area of interest; format 'lhs rhs' [def=None - no restriction]")
    args = parser.parse_args()
    
    x_bnd = get_boundary(args.dx)
    y_bnd = get_boundary(args.dy)
    z_bnd = get_boundary(args.dz)
        
    gmsh.initialize()
    gmsh.open(args.mesh_file)
    dim_tag = get_phys_group_dim_tag(args.group_name)
    entity_data = download_elements(dim_tag)
    print("Finished with entity data")
    area = calculate_area(entity_data, x_bnd, y_bnd, z_bnd)
    gmsh.finalize()
    
    print("Area = %.6e cm^2" % area)    
    
    
    
    
    
    
    
    
    

