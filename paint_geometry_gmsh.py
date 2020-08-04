import gmsh
import numpy as np
import pylibconfig3


def imitate_gmsh_reload(fname):
    gmsh.initialize()
    gmsh.open(fname)
    gmsh.finalize()
    return 0


def get_brep_file_names(geometry_file):
    '''Returns dictionary with name of loaded brep_file pointing to
       the name of the component in the gmsh geomerty file'''
    brep_to_name = {}
    name_to_brep = {}
    f = open(geometry_file, "r")
    for line in f:
        line = line.split("//")[0]
        if line=="":
            continue
        if ("ShapeFromFile" in line) and (".brep" in line):
            fancy_name = line.split("=")[0].replace(" ", "")
            brep = line.split("\"")[1].replace(" ", "")    
            brep_to_name[brep] = fancy_name
            name_to_brep[fancy_name] = brep
    f.close()
    return brep_to_name, name_to_brep


def get_other_dimtags(current_comp, component_to_dimtags):
    '''
    returns list of dimtags without the current_brep
    '''
    dimtags = []
    for k in component_to_dimtags.keys():
        if k != current_comp:
            dimtags.extend(component_to_dimtags[k])
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
        main_box_dimtags, UNUSED_map = gmsh.model.occ.cut(main_box_dimtags, corrections, removeObject=True, removeTool=True)
    return main_box_dimtags


def get_surfaces_for_one_component(curr_comp_id, component_boxes, brep_to_name, component_to_translation, main_box_info):
    print("Working on component %s" % curr_comp_id)
    gmsh.initialize()
    gmsh.option.setNumber("Geometry.OCCScaling", 0.1)
    component_to_dimtags = {}
    for brep in brep_to_name.keys():
        dimtags = gmsh.model.occ.importShapes(brep, highestDimOnly=True, format="brep")
        component_to_dimtags[brep] = dimtags
        gmsh.model.occ.synchronize()
    for box in component_boxes.keys():
        tag = gmsh.model.occ.addBox(component_boxes[box][0], 
                                    component_boxes[box][1],
                                    component_boxes[box][2],
                                    component_boxes[box][3],
                                    component_boxes[box][4],
                                    component_boxes[box][5], tag=-1)
        component_to_dimtags[box] = [(3, tag)]
        gmsh.model.occ.synchronize()
    #here everything is imported
    #Lets apply translations
    for comp in component_to_translation.keys():
        dimtags = component_to_dimtags[comp]
        gmsh.model.occ.translate(dimtags, component_to_translation[comp][0], component_to_translation[comp][1], component_to_translation[comp][2])
        gmsh.model.occ.synchronize()
    #Now lets crossect all components
    current_dimtags = component_to_dimtags[curr_comp_id]
    other_dimtags = get_other_dimtags(curr_comp_id, component_to_dimtags)
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
    full_bounding_box = []
    if len(intersect_dimtags)>0:
        full_bounding_box = np.array(gmsh.model.getBoundingBox(-1, -1))
    gmsh.finalize()
    return bounding_boxes, full_bounding_box


def get_surfaces_for_components(component_to_fancy, component_boxes, brep_to_name, component_to_translation, main_box_info):
    ''' Function will return dictionary with 
       component_id -> {"surfaces": its surface bounding boxes, "full_component": bounding box over all surfaces together}
       Function takes into account the component crossection with the main box and component translations applied in geometry file
    '''
    component_to_bnd_box = {}
    for comp_id in component_to_fancy.keys():
        bounding_boxes, full_bounding_box = get_surfaces_for_one_component(comp_id, component_boxes, brep_to_name, component_to_translation, main_box_info)
        component_to_bnd_box[comp_id] = {}
        component_to_bnd_box[comp_id]["surfaces"] = bounding_boxes
        component_to_bnd_box[comp_id]["full_component"] = full_bounding_box
    return component_to_bnd_box
    

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


def check_bnd_box_equal(lhs, rhs, epsilon):
    norm = (np.array(lhs) - np.array(rhs))**2
    return sum(norm)<=epsilon


def find_component_for_plane(plane, component_to_bnd_box, match_precision):
    '''Looking for plane --> we are not checking here "full_bounding_box" key"
       Not all surfaces are constructed from brep files --> 
       if surface is not found function returns False
    '''
    for comp_id in component_to_bnd_box.keys():
        for bnd_box in component_to_bnd_box[comp_id]["surfaces"]:
            if check_bnd_box_equal(bnd_box, plane[1], epsilon=match_precision):
                return comp_id
    #print("I have not found brep file for plane tag %i" % plane[0])
    return False


def get_empty_key_dict(given_dict):
    d = {}
    for k in given_dict.keys():
        d[k] = []
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


def get_main_box_info(main_box_parts, main_box_mark):
    '''
    main_box_mark - Box id of the main box
    main_box_parts = {box_id: box coordinates, ....}
    main_box_info = {"main": [x, y, z, dx, dy, dz], "corrections":[[x,y,z,...], ...]}
    '''
    if not (main_box_mark in main_box_parts.keys()):
        raise Warning("Currently main box surfaces cannot be chosen to be painted. Or you simply wrote incorrect main box mark")
    main_box_info = {}
    main_box_info["corrections"] = []
    for id_ in main_box_parts.keys():
        if id_ == main_box_mark:
            main_box_info["main"] = main_box_parts[id_]
        else:
            main_box_info["corrections"].append(main_box_parts[id_])
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
    component_to_translation = {}
    name_to_translations = read_translations_in_geometry(geom_file)
    for n in name_to_translations.keys():
        if n in name_to_brep:
            brep_file = name_to_brep[n]
            component_to_translation[brep_file] = name_to_translations[n]
        else:   #we are translating box
            component_to_translation[int(n)] = name_to_translations[n]
    return component_to_translation


def get_component_to_fancy(fancy_to_componnet):
    component_to_fancy = {}
    for fancy in fancy_to_componnet.keys():
        for comp in fancy_to_componnet[fancy]:
            if comp in component_to_fancy.keys():
                raise Warning("Component %s belongs to two different fancy names!" % comp)
            component_to_fancy[comp] = fancy
    return component_to_fancy
        

def replace_gmsh_names(brep_to_name, fancy_to_component):
    for fancy in fancy_to_component.keys():
        for i in range(len(fancy_to_component[fancy])):
            if fancy_to_component[fancy][i] in name_to_brep.keys():
                fancy_to_component[fancy][i] = name_to_brep[fancy_to_component[fancy][i]]
    return fancy_to_component


def split_boxes(boxes_to_params, component_to_fancy):
    main_box_parts = {}
    component_boxes = {}
    for box_id in boxes_to_params.keys():
        if not (box_id in component_to_fancy.keys()):
            main_box_parts[box_id] = boxes_to_params[box_id]
        else:
            component_boxes[box_id] = boxes_to_params[box_id]
    return main_box_parts, component_boxes


def load_config_data(config_file):
    config_data = {}
    cfg=pylibconfig3.libconfigConfiguration()
    cfg.read_file(config_file)
    config_data["main_box_mark"] = cfg["main_box_mark"]
    config_data["match_precision"] = cfg["match_precision"]
    config_data["fancy_names"] = {}
    used_names = set()
    for i in range(len(cfg["fancy_names"])):
        name = cfg["fancy_names"][i]["name"]
        if name in used_names:
            raise Warning("Fancy name %s is used twice" % name)
        used_names.add(name)
        components = []
        for j in range(len(cfg["fancy_names"][i]["components"])):
            components.append(cfg["fancy_names"][i]["components"][j])
        config_data["fancy_names"][name] = components
    return config_data
    

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-cfg', '--config', default="config.dat", help="Config file for gmsh painter [def='config.dat']")
    parser.add_argument('-geo', '--geo_file', default="rme_gmsh.geo", help="Name of the file which contains gmsh script for geometry [def='rme_gmsh.geo']")
    args=parser.parse_args()
    
    GEO_FILE = args.geo_file    
    CONFIG_FILE = args.config
    
    #reading config data
    config_data = load_config_data(CONFIG_FILE)
    #get all brep files
    brep_to_name, name_to_brep = get_brep_file_names(GEO_FILE)
    config_data["fancy_names"] = replace_gmsh_names(name_to_brep, config_data["fancy_names"])
    component_to_fancy = get_component_to_fancy(config_data["fancy_names"])
    boxes_to_params = read_boxes_in_geometry(GEO_FILE)
    #get main box stuff - main box is all boxes except those who are added to the fancy_name structure
    main_box_parts, component_boxes = split_boxes(boxes_to_params, component_to_fancy)
    main_box_info = get_main_box_info(main_box_parts, config_data["main_box_mark"])
    #get brep file translations
    component_to_translation = get_component_translations(name_to_brep, GEO_FILE)
    #apply brep file translations and subtract files --> bounding boxes for all surfaces
    component_to_bnd_box = get_surfaces_for_components(component_to_fancy, component_boxes, brep_to_name, component_to_translation, main_box_info)
    #Load gmsh geometry for calculations
    imitate_gmsh_reload(GEO_FILE)
    gmsh.initialize()
    gmsh.open(GEO_FILE)
    geo_planes, geo_vols = download_geo_entities()
    gmsh.finalize()
    #paint stuff
    print("Searching for surfaces")
    fancy_name_to_plane_tag = get_empty_key_dict(config_data["fancy_names"])    #dictionary name --> tag
    for plane in geo_planes:
        component_it_belongs = find_component_for_plane(plane, component_to_bnd_box, config_data["match_precision"])
        if component_it_belongs:
            name = component_to_fancy[component_it_belongs]
            fancy_name_to_plane_tag[name].append(plane[0])
    
    #write physical groups to file
    write_surfaces(fancy_name_to_plane_tag, GEO_FILE)





















    
    
    