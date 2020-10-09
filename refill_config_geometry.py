import re

def parse_mesh_file_line(line):
    line = line.replace('\n', '').replace('"', '')
    line = line.split(' ')
    return {'dimension':float(line[0]), 'name': line[-1]}


def get_phys_groups_names(mesh_file):
    f = open(mesh_file, 'r')
    enter_group_names = False
    phys_names = []
    for line in f:
        if "$PhysicalNames" in line:
            enter_group_names = True
            continue
        if "$EndPhysicalNames" in line:
            break
        if enter_group_names:
            phys_names.append(parse_mesh_file_line(line))
    f.close()
    return phys_names[1::]  #the first line in physical naming is the number of arguments --> ignore it


def get_file_content(config_file):
    f = open(config_file, 'r')
    content = list(f)
    f.close()
    one_str_content = ""
    for i in range(len(content)):
        one_str_content += content[i]
    return one_str_content


def get_internal_structure(content):
    begin = content.index("internal_structure")
    get_inside_structure_block = False
    bracket_count = 0
    end = None
    for i in range(begin, len(content)):
        if content[i]=='{':
            get_inside_structure_block = True
            bracket_count +=1
        if content[i]=='}':
            bracket_count -=1
        if get_inside_structure_block and bracket_count==0:
            end = i
            break
    if end<=len(content)-2:
        end+=1  #including closing bracket
    return (begin, end)


def get_default_properties(mesh_name):
    properties = []
    properties.append('ion_induced_emission_model = "default";')
    properties.append('type = "EMPTY_TYPE";')
    properties.append('material = "EMPTY_MATERIAL";') 
    if mesh_name['dimension']==2:
        properties.append('potential = (EMPTY_POTENTIAL ,"V");')
    if mesh_name['dimension']==3:    
        properties.append('epsilon=EMPTY_EPSILON;')
    return properties


def replace_internal_structure(content, phys_names):
    int_struct_range = get_internal_structure(content)
    internal_structure = content[int_struct_range[0]:int_struct_range[1]]
    structure = {}
    for mesh_name in phys_names:
        block_match = get_config_block(internal_structure, mesh_name['name'])
        if block_match!=None:
            structure[mesh_name['name']] = get_block_porperties(internal_structure[block_match.start():block_match.end()])
        else:
            structure[mesh_name['name']] = get_default_properties(mesh_name)
    new_internal_structure = 'internal_structure = {\n\n'
    for k in structure.keys():
        tmp = "%s = {\n" % k
        for el in structure[k]:
            tmp += "\t%s\n" %el
        tmp += "};\n\n"
        new_internal_structure += tmp  
    new_internal_structure += "}"   #; here taken from old content
    new_content = content[:int_struct_range[0]] + new_internal_structure + content[int_struct_range[1]:]
    return new_content


def replace_mesh_file(content, mesh_file):
    fname = mesh_file.split('/')[-1]
    start = content.index('mesh')
    end = content[start:].index(';')+start
    new_mesh_string = 'mesh = "%s"' % fname
    return content[:start] + new_mesh_string + content[end:]


def get_config_block(content, block_name):
    block_pattern = r"\s*%s\s*=\s*{(.*\n?)*?\s*};?" % block_name
    block_match = re.search(block_pattern, content)
    return block_match

def get_block_porperties(content):
    begin = content.find('{')
    end = content.find('}')
    property_pattern = "\w+\s*=\s*[\"(]?.*[\")]?;?"
    properties = re.findall(property_pattern, content[begin:end])
    return properties
                                   
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mesh_file", action='store', type=str, default='test_mesh_file', help="mesh file name [def = 'mesh.msh'")
    parser.add_argument("-c", "--config_file", action='store', type=str, default='config.dat', help="config which will be changed [def = 'config.dat']")
    args = parser.parse_args()
    
    phys_names = get_phys_groups_names(args.mesh_file)
    content = get_file_content(args.config_file)
    content = replace_internal_structure(content, phys_names)
    content = replace_mesh_file(content, args.mesh_file)
    f = open(args.config_file, 'w')
    f.write(content)
    f.close()
    
    
