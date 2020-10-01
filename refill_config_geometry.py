

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


def get_block_begin(content, block_name):
    starts = []
    next_start = 0
    idx=0
    while idx >=0:
        idx = content[next_start:].find(block_name)
        if idx>0:
            starts.append(idx + next_start)
            next_start += idx + len(block_name)
    for i in range(len(starts)):
        check_1 = content[starts[i]+len(block_name)]==' ' or content[starts[i]+len(block_name)]=='='
        check_2 = content[starts[i]+len(block_name)]=='\t' or content[starts[i]+len(block_name)]=='\n' 
        if check_1 or check_2:
            return starts[i]
    raise Warning('Could not find block name %s \n' % block_name)
    

def get_data_block(content, block_name):
    begin = get_block_begin(content, block_name)
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


def get_cfg_group_names(content):
    #throw away 'internal_structure={' from the head
    idx = content.index('{')
    names = []
    name_start = True
    tmp_name = ''
    for i in range(idx+1,len(content)):
        if content[i]=='}':
            name_start = True
        if name_start and content[i]=='=':
            tmp_name = tmp_name.replace(' ', '')
            tmp_name = tmp_name.replace('\n', '')
            tmp_name = tmp_name.replace('\t', '')
            tmp_name = tmp_name.replace('}', '')
            tmp_name = tmp_name.replace(';', '')
            names.append(tmp_name)
            tmp_name = ''
            name_start = False
        if name_start:
            tmp_name += content[i]
    return names

def get_default_block(mesh_name):
    description = ""
    description += '\n\tion_induced_emission_model = "default";'
    description += '\n\ttype = "EMPTY_TYPE";'
    description += '\n\tmaterial = "EMPTY_MATERIAL";' 
    if mesh_name['dimension']==2:
        description += '\n\tpotential = (EMPTY_POTENTIAL ,"V");'
    if mesh_name['dimension']==3:    
        description += '\n\tepsilon=EMPTY_EPSILON;'
    default_block = "\n%s = {%s\n};\n\n" % (mesh_name['name'], description)
    return default_block


def replace_internal_structure(content, phys_names):
    int_struct = get_data_block(content, "internal_structure")
    cfg_names = get_cfg_group_names(content[int_struct[0]:int_struct[1]])
    structure = ""
    for mesh_name in phys_names:
        if mesh_name['name'] in cfg_names:
            idx = get_data_block(content, mesh_name['name'])
            structure += content[idx[0]:idx[1]] + ';\n\n'
        else:
            structure += get_default_block(mesh_name)
    new_internal_structure = 'internal_structure = {\n%s\n}' % structure
    new_content = content[:int_struct[0]] + new_internal_structure + content[int_struct[1]:]
    return new_content


def replace_mesh_file(content, mesh_file):
    fname = mesh_file.split('/')[-1]
    start = content.index('mesh')
    end = content[start:].index(';')+start
    new_mesh_string = 'mesh = "%s"' % fname
    return content[:start] + new_mesh_string + content[end:]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mesh_file", action='store', type=str, default='mesh.msh', help="mesh file name [def = 'mesh.msh'")
    parser.add_argument("-c", "--config_file", action='store', type=str, default='config.dat', help="config which will be changed [def = 'config.dat']")
    args = parser.parse_args()
    
    phys_names = get_phys_groups_names(args.mesh_file)
    content = get_file_content(args.config_file)
    content = replace_internal_structure(content, phys_names)
    content = replace_mesh_file(content, args.mesh_file)
    f = open(args.config_file, 'w')
    f.write(content)
    f.close()
    
    
