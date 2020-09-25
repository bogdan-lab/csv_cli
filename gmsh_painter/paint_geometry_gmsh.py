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


def get_surfaces_for_one_component(curr_comp_id, component_boxes, brep_to_name, component_to_translation, main_box_coors):
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
    main_box_tag = gmsh.model.occ.addBox(main_box_coors[0],
                                         main_box_coors[1],
                                         main_box_coors[2],
                                         main_box_coors[3],
                                         main_box_coors[4],
                                         main_box_coors[5], tag=-1)
    main_box_dimtags = [(3, main_box_tag)]
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


def get_surfaces_for_components(component_to_fancy, component_boxes, brep_to_name, component_to_translation, main_box_coors):
    ''' Function will return dictionary with 
       component_id -> {"surfaces": its surface bounding boxes, "full_component": bounding box over all surfaces together}
       Function takes into account the component crossection with the main box and component translations applied in geometry file
    '''
    component_to_bnd_box = {}
    for comp_id in component_to_fancy.keys():
        bounding_boxes, full_bounding_box = get_surfaces_for_one_component(comp_id, component_boxes, brep_to_name, component_to_translation, main_box_coors)
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
    return False


def find_component_for_volume(vol, component_to_bnd_box, match_precision):
    '''Similar but for volumes'''
    for comp_id in component_to_bnd_box.keys():
        if check_bnd_box_equal(component_to_bnd_box[comp_id]["full_component"], vol[1], epsilon=match_precision):
            return comp_id
    return False


def get_volume_planes(name, vol_comp_surfaces, geo_planes, match_precision):
    this_vol_planes = []
    for bnd in vol_comp_surfaces:
        for pl in geo_planes:
            if check_bnd_box_equal(bnd, pl[1], match_precision):
                this_vol_planes.append(pl[0])
    if len(this_vol_planes)!=len(vol_comp_surfaces):
        print("Not all surfaces of volume \"%s\" was found! If you used 'res_metal_flag' some of them can be marked as metall!" % name)
    return this_vol_planes


def get_empty_key_dict(given_key_list):
    d = {}
    for k in given_key_list:
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
    return 0


def write_volumes(name_to_volumes, geo_file):
    f = open(geo_file, "a")
    f.write("\n\n//Here I add physical volumes\n")
    for name in name_to_volumes.keys():
        if len(name_to_volumes[name])==0:
            print("Object %s has no volumes in current geometry" % name)
            continue
        f.write('Physical Volume("%s") = { %i' % (name, name_to_volumes[name][0]))
        for i in range(1, len(name_to_volumes[name])):
            f.write(", %i" % name_to_volumes[name][i])
        f.write("};\n")
    f.close()
    return 0


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


def split_boxes(boxes_to_params, main_box_mark):
    main_box_coors = []
    component_boxes = {}
    for box_id in boxes_to_params.keys():
        if box_id == main_box_mark:
            main_box_coors = boxes_to_params[box_id]
        else:
            component_boxes[box_id] = boxes_to_params[box_id]
    if len(main_box_coors)==0:
        raise Warning("Main box %s was not found!" % main_box_mark)
    return main_box_coors, component_boxes


def split_components_bnd_box(component_to_bnd_box, component_to_fancy, surface_names, volume_names):
    plane_compon_to_bnd_box = {}
    vol_compon_to_bnd_box = {}
    for comp in component_to_bnd_box.keys():
        name = component_to_fancy[comp]
        if name in volume_names:
            vol_compon_to_bnd_box[comp] = component_to_bnd_box[comp]
        else:
            plane_compon_to_bnd_box[comp] = component_to_bnd_box[comp]
    return plane_compon_to_bnd_box, vol_compon_to_bnd_box


def read_names_to_components(name_group, used_names):
    name_to_components = {}
    for i in range(len(name_group)):
        name = name_group[i]["name"]
        if name in used_names:
            raise Warning("Fancy name %s is used twice" % name)
        used_names.add(name)
        components = []
        for j in range(len(name_group[i]["components"])):
            components.append(name_group[i]["components"][j])
        name_to_components[name] = components
    return name_to_components, used_names


def read_names(name_group):
    names = []
    for i in range(len(name_group)):
        names.append(name_group[i]["name"])
    return names


def load_config_data(config_file):
    config_data = {}
    cfg=pylibconfig3.libconfigConfiguration()
    cfg.read_file(config_file)
    config_data["main_box_mark"] = cfg["main_box_mark"]
    config_data["match_precision"] = cfg["match_precision"]
    config_data["fancy_names"] = {}
    used_names = set()
    #add planes
    name_to_components, used_names = read_names_to_components(cfg["fancy_names"]["surfaces"],used_names)
    config_data["fancy_names"].update(name_to_components)
    #add volumes
    name_to_components, used_names = read_names_to_components(cfg["fancy_names"]["volumes"],used_names)
    config_data["fancy_names"].update(name_to_components)
    config_data["surface_names"] = read_names(cfg["fancy_names"]["surfaces"])
    config_data["volume_names"] = read_names(cfg["fancy_names"]["volumes"])
    config_data["rest_metal"] = cfg["rest_metal"]
    config_data["rest_free_space"] = cfg["rest_free_space"]
    return config_data


def get_rest_metal_surfaces(geo_planes, marked_planes, volume_planes):
    metal_planes = []
    for pl in geo_planes:
        if not (pl[0] in marked_planes) and not (pl[0] in volume_planes):
            metal_planes.append(pl[0])
    return metal_planes


def get_rest_volumes(geo_vols, marked_volumes):
    free_spaces = []
    for vol in geo_vols:
        if not (vol[0] in marked_volumes):
            free_spaces.append(vol[0])
    return free_spaces


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-cfg', '--config', default="paint_config.dat", help="Config file for gmsh painter [def='paint_config.dat']")
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
    main_box_coors, component_boxes = split_boxes(boxes_to_params, config_data["main_box_mark"])
    #get brep file translations
    component_to_translation = get_component_translations(name_to_brep, GEO_FILE)
    #apply brep file translations and subtract files --> bounding boxes for all surfaces
    component_to_bnd_box = get_surfaces_for_components(component_to_fancy, component_boxes, brep_to_name, component_to_translation, main_box_coors)
    plane_compon_to_bnd_box, vol_compon_to_bnd_box = split_components_bnd_box(component_to_bnd_box, component_to_fancy, 
                                                                              config_data["surface_names"], config_data["volume_names"])
    #Load gmsh geometry for calculations
    imitate_gmsh_reload(GEO_FILE)
    gmsh.initialize()
    gmsh.open(GEO_FILE)
    geo_planes, geo_vols = download_geo_entities()
    gmsh.finalize()
    #paint stuff
    print("Searching for surfaces")
    marked_planes = []
    fancy_name_to_plane_tag = get_empty_key_dict(config_data["surface_names"])    #dictionary name --> tag
    for plane in geo_planes:
        component_it_belongs = find_component_for_plane(plane, plane_compon_to_bnd_box, config_data["match_precision"])
        if component_it_belongs:
            name = component_to_fancy[component_it_belongs]
            fancy_name_to_plane_tag[name].append(plane[0])
            if plane[0] in marked_planes:
                raise Warning("Plane %s occurs in two different physical groups!" % plane[0])
            marked_planes.append(plane[0])
    
    print("Searching for volumes")
    marked_volumes = []
    volume_planes = []
    fancy_name_to_vol_tag = get_empty_key_dict(config_data["volume_names"])
    for vol in geo_vols:
        component_it_belongs = find_component_for_volume(vol, vol_compon_to_bnd_box, config_data["match_precision"])
        if component_it_belongs:
            name = component_to_fancy[component_it_belongs]
            fancy_name_to_vol_tag[name].append(vol[0])
            if vol[0] in marked_volumes:
                raise Warning("Volume %s occurs in two different physical groups!" % vol[0])
            marked_volumes.append(vol[0])
            this_vol_planes = get_volume_planes(name, vol_compon_to_bnd_box[component_it_belongs]["surfaces"], geo_planes, config_data["match_precision"])
            volume_planes.extend(this_vol_planes)
    
    if config_data["rest_metal"]:
        fancy_name_to_plane_tag["metal"] = get_rest_metal_surfaces(geo_planes, marked_planes, volume_planes)
    if config_data["rest_free_space"]:
        fancy_name_to_vol_tag["free_space"] = get_rest_volumes(geo_vols, marked_volumes)

    #write physical groups to file
    write_surfaces(fancy_name_to_plane_tag, GEO_FILE)
    write_volumes(fancy_name_to_vol_tag, GEO_FILE)




















    
    
    