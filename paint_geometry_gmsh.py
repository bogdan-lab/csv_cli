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
    '''
    returns list of dimtags without the current_brep
    '''
    dimtags = []
    for k in brep_to_dimtags.keys():
        if k != current_brep:
            dimtags.extend(brep_to_dimtags[k])
    return dimtags


def construct_main_box(main_box_info):
    '''Function will construct in the current gmsh model main box according to main_box_info
    '''
    main_tag = gmsh.model.occ.addBox(main_box_info["main"][0],
                                     main_box_info["main"][1],
                                     main_box_info["main"][2],
                                     main_box_info["main"][3],
                                     main_box_info["main"][4],
                                     main_box_info["main"][5], tag=-1)
    main_box_dimtags = [(3, main_tag)]
    corrections = []
    for box in main_box_info["corrections"]:
        tag = gmsh.model.occ.addBox(box[0], box[1], box[2], box[3], box[4], box[5], tag=-1)
        corrections.append((3, tag))
    if len(corrections)>0:
        main_box_dimtags = gmsh.model.occ.cut(main_box_dimtags, corrections, removeObject=True, removeTool=True)
    return main_box_dimtags


def get_surfaces_for_one_component(brep_file, brep_to_name, brep_to_translation, main_box_info):
    gmsh.initialize()
    brep_to_dimtags = {}
    for brep in brep_to_name.keys():
        dimtags = gmsh.model.occ.importShapes(brep, highestDimOnly=True, format="brep")
        brep_to_dimtags[brep] = dimtags
        gmsh.model.occ.synchronize()
    #here everything is imported
    #Lets apply translations
    for brep in brep_to_translation.keys():
        dimtags = brep_to_dimtags[brep]
        gmsh.model.occ.translate(dimtags, brep_to_translation[brep][0], brep_to_translation[brep][1], brep_to_translation[brep][2])
        gmsh.model.occ.synchronize()
    #Now lets crossect all components
    current_dimtags = brep_to_dimtags[brep_file]
    other_dimtags = get_other_dimtags(brep_file, brep_to_dimtags)
    cut_dimtags, UNUSED_map = gmsh.model.occ.cut(current_dimtags, other_dimtags, removeObject=True, removeTool=True)
    gmsh.model.occ.synchronize()
    #now intersect the component with main_box -> get surfaces which actually are present in the calculation area
    main_box_dimtags = construct_main_box(main_box_info)
    gmsh.model.occ.synchronize()
    intersect_dimtags, UNUSED_map = gmsh.model.occ.intersect(main_box_dimtags, cut_dimtags, tag=-1, removeObject=True, removeTool=True)
    gmsh.model.occ.synchronize()
    #now in current model only surfaces which will actually be in calculation area are presented
    bounding_boxes = []
    dimtags = gmsh.model.getEntities(2)
    for dt in dimtags:
        bounding_boxes.append(np.array(gmsh.model.getBoundingBox(dt[0], dt[1])))
    full_bounding_box = np.array(gmsh.model.getBoundingBox(-1, -1))
    gmsh.finalize()
    return bounding_boxes, full_bounding_box


def get_surfaces_for_breps(brep_to_name, brep_to_translation, main_box_info):
    ''' Function will return dictionary with 
       brep_file_name -> {"surfaces": its surface bounding boxes, "full_component": bounding box over all surfaces together}
       Function takes into account the component crossection with the main box and component translations applied in geometry file
    '''
    brep_to_bnd_box = {}
    for brep in brep_to_name.keys():
        bounding_boxes, full_bounding_box = get_surfaces_for_one_component(brep, brep_to_name, brep_to_translation, main_box_info)
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
    '''Looking for plane --> we are not checking here "full_bounding_box" key"
       Not all surfaces are constructed from brep files --> 
       if surface is not found function returns False
    '''
    for brep in brep_to_bnd_box.keys():
        for bnd_box in brep_to_bnd_box[brep]["surfaces"]:
            if check_bnd_box_equal(bnd_box, plane[1], epsilon=1e-9):
                return brep
    print("I have not found brep file for plane tag %i" % plane[0])
    return False


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


def read_boxes_in_geometry(geom_file):
    '''
    Function will parse geometry file for Box()
    '''
    boxes = {}
    f = open(geom_file, "r")
    for line in f:
        line = line.split("//")[0]
        if line=="":
            continue
        if ("Box(" in line) and ("=" in line) and ("{" in line) and ("};" in line):
            box_id = int(line.split('(')[1].split(')')[0])
            coors = line.split('{')[1].split('}')[0].split(',')
            for i in range(len(coors)):
                coors[i] = float(coors[i])
            boxes[box_id] = coors
    f.close()
    return boxes


def get_main_box_info(geom_file, main_box_mark=100):
    '''
    main_box_mark - Box id of the main box
    All other boxes in the file will be treated as simple main box corrections
    and not like geometry components!
    main_box_info = {"main": [x, y, z, dx, dy, dz], "corrections":[[x,y,z,...], ...]}
    '''
    boxes = read_boxes_in_geometry(geom_file)
    main_box_info = {}
    main_box_info["corrections"] = []
    for id_ in boxes.keys():
        if id_ == main_box_mark:
            main_box_info["main"] = boxes[id_]
        else:
            main_box_info["corrections"].append(boxes[id_])
    if len(main_box_info.keys())<2:
        raise Warning("I did not found main box in geometry file. Chack its ID %i" % main_box_mark)
    return main_box_info
    

def parse_translation_buffers(translation_lines):
    name_to_translations = {}
    for trans in translation_lines:
        coors = trans.split('{')[1].split('}')[0].replace(' ', '').split(',')
        for i in range(len(coors)):
            coors[i] = float(coors[i])
        coors = np.array(coors)
        names = trans.split('{')[3].split('}')[0].replace(' ', '').split(',')
        for n in names:
            if not (n in name_to_translations.keys()):
                name_to_translations[n] = []
            name_to_translations[n].append(coors)
    for k in name_to_translations.keys():
        name_to_translations[k] = sum(name_to_translations[k])
    return name_to_translations


def read_translations_in_geometry(geom_file):
    '''Function will parse geometry file for translation information'''
    f = open(geom_file, 'r')
    translation_lines = []
    save_trans_flag = False
    tmp_trans = ''
    count_open = 0
    count_close = 0
    for line in f:
        line = line.split("//")[0]
        if line=="":
            continue
        if "Translate" in line:
            save_trans_flag=True
        if save_trans_flag:
            count_open  += line.count('{') 
            count_close += line.count('}') 
            tmp_trans+=line.replace('\n', '')
        if count_open==3 and count_close==3:
            #translation buffer is read
            save_trans_flag=False
            translation_lines.append(tmp_trans)
            tmp_trans = ''
            count_open = 0
            count_close = 0
    name_to_translations = parse_translation_buffers(translation_lines)
    f.close()
    return name_to_translations

def get_component_translations(name_to_brep, geom_file):
    '''Returns dictionary with information about translations for each brep file
    '''
    brep_to_translation = {}
    name_to_translations = read_translations_in_geometry(geom_file)
    for n in name_to_translations.keys():
        brep_file = name_to_brep[n]
        brep_to_translation[brep_file] = name_to_translations[n]
    return brep_to_translation


if __name__ == "__main__":
    GEO_FILE = "rme_gmsh.geo"    
    MAIN_BOX_MARK=100
    
    #get all brep files
    brep_to_name = get_brep_file_names(GEO_FILE)
    name_to_brep = dict([(value, key) for key, value in brep_to_name.items()])
    #get main box stuff
    main_box_info = get_main_box_info(GEO_FILE, MAIN_BOX_MARK)
    #get brep file translations
    brep_to_translation = get_component_translations(name_to_brep, GEO_FILE)
    #apply brep file translations and subtract files --> bounding boxes for all surfaces
    brep_to_bnd_box = get_surfaces_for_breps(brep_to_name, brep_to_translation, main_box_info)
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
        if brep_it_belongs:
            name = brep_to_name[brep_it_belongs]
            name_to_planes[name].append(plane[0])
    
    #write physical groups to file
    write_surfaces(name_to_planes, GEO_FILE)





















    
    
    