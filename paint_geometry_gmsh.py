import gmsh
import numpy as np


def imitate_gmsh_reload(fname):
    gmsh.initialize()
    gmsh.open(fname)
    gmsh.finalize()
    return 0


def get_brep_file_names(geometry_file):
    '''Returns dictionary with name of loaded brep_file pointing to
       the name of the component in the gmsh geomerty file'''
    brep_to_name = {}
    f = open(geometry_file, "r")
    for line in f:
        line = line.split("//")[0]
        if line=="":
            continue
        if ("ShapeFromFile" in line) and (".brep" in line):
            fancy_name = line.split("=")[0].replace(" ", "")
            brep = line.split("\"")[1].replace(" ", "")    
            brep_to_name[brep] = fancy_name
    f.close()
    return brep_to_name


def get_other_dimtags(current_brep, brep_to_dimtags):
    dimtags = []
    for k in brep_to_dimtags.keys():
        if k != current_brep:
            dimtags.extend(brep_to_dimtags[k])
    return dimtags


def get_surfaces_for_one_component(brep_file, brep_to_name):
    gmsh.initialize()
    brep_to_dimtags = {}
    for brep in brep_to_name.keys():
        dimtags = gmsh.model.occ.importShapes(brep, highestDimOnly=True, format="brep")
        brep_to_dimtags[brep] = dimtags
        gmsh.model.occ.synchronize()
    #here everything is imported
    current_dimtags = brep_to_dimtags[brep_file]
    other_dimtags = get_other_dimtags(brep_file, brep_to_dimtags)
    result_dimtags, UNUSED_map = gmsh.model.occ.cut(current_dimtags, other_dimtags, removeObject=True, removeTool=True)
    gmsh.model.occ.synchronize()
    bounding_boxes = []
    dimTags = gmsh.model.getEntities(2)
    for dt in dimTags:
        bounding_boxes.append(np.array(gmsh.model.getBoundingBox(dt[0], dt[1])))
    full_bounding_box = np.array(gmsh.model.getBoundingBox(-1, -1))
    gmsh.finalize()
    return bounding_boxes, full_bounding_box


def get_surfaces_for_breps(brep_to_name):
    brep_to_bnd_box = {}
    for brep in brep_to_name.keys():
        bounding_boxes, full_bounding_box = get_surfaces_for_one_component(brep, brep_to_name)
        brep_to_bnd_box[brep] = {}
        brep_to_bnd_box[brep]["surfaces"] = bounding_boxes
        brep_to_bnd_box[brep]["full_component"] = full_bounding_box
    return brep_to_bnd_box
    

def download_geo_entities():
    '''
       Returns geo_plane = [[plane_tag, plane_bounding_box], ...]
       and geo_vols = [[volume_tag, volume_bounding_box], ...]
    '''
    dimTags_pl = gmsh.model.getEntities(2)
    geo_planes = []
    for dt in dimTags_pl:
        geo_planes.append([dt[1], np.array(gmsh.model.getBoundingBox(dt[0], dt[1]))])
    dimTags_v = gmsh.model.getEntities(3)
    geo_vols=[]
    for dt in dimTags_v:
        geo_vols.append([dt[1], np.array(gmsh.model.getBoundingBox(dt[0], dt[1]))])
    return geo_planes, geo_vols


def check_bnd_box_equal(lhs, rhs, epsilon=1e-9):
    norm = (np.array(lhs) - np.array(rhs))**2
    return sum(norm)<=epsilon


def find_brep_file_for_plane(plane, brep_to_bnd_box):
    '''Looking for plane --> we are no checking here "full_bounding_box" key"'''
    for brep in brep_to_bnd_box.keys():
        for bnd_box in brep_to_bnd_box[brep]["surfaces"]:
            if check_bnd_box_equal(bnd_box, plane[1], epsilon=1e-9):
                return brep
    raise Warning("I have not found brep file for plane tag %i" % plane[0])
    return None


def get_name_dict(brep_to_name):
    d = {}
    for k in brep_to_name.keys():
        d[brep_to_name[k]] = []
    return d


def write_surfaces(name_to_planes, geo_file):
    f = open(geo_file, "a")
    f.write("\n\n//Here I add physical planes\n")
    for name in name_to_planes.keys():
        if len(name_to_planes[name])==0:
            print("Object %s has no surfaces in current geometry" % name)
            continue
        f.write('Physical Surface("%s") = { %i' % (name, name_to_planes[name][0]))
        for i in range(1, len(name_to_planes[name])):
            f.write(", %i" % name_to_planes[name][i])
        f.write("};\n")
    f.close()


if __name__ == "__main__":
    GEO_FILE = "rme_gmsh.geo"    

    #get all brep files
    brep_to_name = get_brep_file_names(GEO_FILE)
    #get brep file translations
    #apply brep file translations and subtract files --> bounding boxes for all surfaces
    brep_to_bnd_box = get_surfaces_for_breps(brep_to_name)
    #Load gmsh geometry for calculations
    imitate_gmsh_reload(GEO_FILE)
    gmsh.initialize()
    gmsh.open(GEO_FILE)
    geo_planes, geo_vols = download_geo_entities()
    gmsh.finalize()
    #paint stuff
    name_to_planes = get_name_dict(brep_to_name)    #dictionary name --> tag
    for plane in geo_planes:
        brep_it_belongs = find_brep_file_for_plane(plane, brep_to_bnd_box)
        name = brep_to_name[brep_it_belongs]
        name_to_planes[name].append(plane[0])
    
    #write physical groups to file
    write_surfaces(name_to_planes, GEO_FILE)





















    
    
    