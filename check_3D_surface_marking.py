
def find_in_brackets(line, brackets):
    open_idx = -1
    for i in range(len(line)):
        if line[i]==brackets[0]:
            open_idx = i
    end_idx = -1
    for i in range(len(line)):
        if line[i]==brackets[1]:
            end_idx = i
    return line[open_idx+1:end_idx].replace('"', '')




if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--geo_file", action="store", type=str, default="rme_gmsh.geo", 
                        help="name of the geometry file which you want to check [def='rme_gmsh.geo']")
    args = parser.parse_args()
    
    f = open(args.geo_file, 'r')
    surface_names = []
    surface_lines = []
    for line in f:
        if 'Physical Surface' in line:
            name = find_in_brackets(line, '()')
            surface_names.append(name)
            surface_lines.append(line)
            
    group_dict = {}
    names_set = set(surface_names)
    for el in names_set:
        group_dict[el] = []
            
    for i in range(len(surface_names)):
        surface_id = find_in_brackets(surface_lines[i], "{}")
        surface_id = surface_id.split(',')
        for j in range(len(surface_id)):
            group_dict[surface_names[i]].append(int(surface_id[j]))
            
    error_flag = 0
    for k1 in group_dict.keys():
        for k2 in group_dict.keys():
            if k1 != k2:
                for i in range(len(group_dict[k1])):
                    for j in range(len(group_dict[k2])):
                        if group_dict[k1][i] == group_dict[k2][j]:
                            error_flag+=1
                            print("%d is in %s and %s\n" % (group_dict[k2][j], k1, k2))
    
    if error_flag == 0:
        print("\nNO SURFACE MATHCES WERE FOUND\n")
    
    







