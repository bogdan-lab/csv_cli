from typing import List, Tuple, Any, Union


def has_duplicates(data: List[Any]) -> bool:
    '''Returns true if `data` contains duplicates and false otherwise
    '''
    unique_data = {el for el in data}
    return len(data) != 0 and len(data) != len(unique_data)


def get_indexes_by_names(header: str, delimiter: str, col_names: List[int]) -> List[int]:
    '''Method will return list of indexes which corresponds to the input list of column names.
       Note that index list will be in the same order as list of names.
       Comparison is case sensitive, but ignores trailing white spaces
       ValueError will be raised if:
       * there is a name which cannot be found in the header
       * there are duplicate names in the col_names argument
       * there is more than one occurrence the name from col_names in header
       If function return successfully there is no duplicates in the result list
    '''
    req_names = [el.strip() for el in col_names]
    if has_duplicates(req_names):
        raise ValueError("there are duplicates among requested column names.")
    name_list = [el.strip() for el in header.split(delimiter)]

    res = [0]*len(req_names)
    for i, name in enumerate(req_names):
        cnt = name_list.count(name)
        if cnt == 0:
            raise ValueError(f"Cannot find {name} in the header")
        elif cnt > 1:
            raise ValueError(f"There are several columns named as f{name}")
        else:
            res[i] = name_list.index(name)

    return res


def select_from_row(row: str, delimiter: str, col_indexes: List[int]) -> str:
    '''Filters the given row in the way, that only the given column indexes are left in it.
       Columns in the row are defined by delimiter.
       Note that the result will be still string with the same delimiter but
       it will contain only the chosen columns
       Regardless to the order of indexes in col_indexes argument the value orders in the result
       will be the same as in the row.
       If col_index contains duplicate values corresponding values from row will also be also duplicated
    '''
    l = row.split(delimiter)
    res = [""]*len(col_indexes)
    for i, c in enumerate(sorted(col_indexes)):
        if c >= len(l):
            raise ValueError(
                f"There is no column with index {c} in a row {row}")
        else:
            res[i] = l[c]
    return delimiter.join(res)


def ranges_to_int_sequence(ranges: List[Tuple[int]]) -> List[int]:
    '''This function will take a list of ranges (start, end) and convert it into the sequence of integers.
        Note that ranges are semi intervals, start is included and end is not.
        For example, input [(1,2), (4,6)] will be converted into [1, 4, 5].
        Note that function expects the list of ranges to be sorted by the left edge.
        The resulting list will contain only unique integers which are present in at least one of the given ranges.
        The result sequence will be sorted.
        Method ignores empty ranges in the input list.
    '''
    res = []
    for rng in ranges:
        if rng[0] >= rng[1]:
            continue
        if len(res) == 0:
            res.extend(range(rng[0], rng[1]))
        else:
            if res[-1] < rng[0]:
                res.extend(range(rng[0], rng[1]))
            elif res[-1] >= rng[0] and res[-1] + 1 < rng[1]:
                res.extend(range(res[-1]+1, rng[1]))
            else:
                pass
    return res


def cross_ranges(lhs: Tuple[int], rhs: Tuple[int]) -> Tuple[int]:
    '''Accepts two ranges defined by semi-interval (the first value is included and the second is not),
       and returns the intersection of these two ranges as a semi-interval.
       Function assumes that input ranges are valid: first <= second
    '''
    if rhs[0] >= lhs[1] or lhs[0] >= rhs[1]:
        return tuple((lhs[0], lhs[0]))
    return tuple((max(lhs[0], rhs[0]), min(lhs[1], rhs[1])))


def build_ranges_for_singles(values: List[int]) -> List[Tuple[int]]:
    '''Returns list of ranges which corresponds to the input individual values.
       List of ranges is sorted by the left edge.
       Duplicates in the input values will result in duplicates in the range values
    '''
    return [(el, el+1) for el in sorted(values)]


def build_ranges_for_begins_ends(begins: List[int], ends: List[int]) -> List[Tuple[int]]:
    '''Build list of ranges from two list.
    The first list contains begins of ranges and the second list - ends.
    If list sizes are not equal ValueError will be raised
    The resulting list of ranges will be sorted by their left edge.
    If some ends values are smaller than corresponding begins values, they will be equated to the begins values.
    Therefore for all ranges in the result begin <= end will be fulfilled.
    Function does not filter duplicates if those exists
    '''
    if len(begins) != len(ends):
        raise ValueError("Range edges lists have different lengths.")
    return list(sorted((b, max(b, e)) for b, e in zip(begins, ends)))


def merge_ranges(*ranges: Union[Tuple[int], List[int]]) -> List[Tuple[int]]:
    '''Put all ranges from the input into one list of ranges sorted by the left edge.
    One can pass separate ranges into this function, defined by a tuple
    Or one can pass list of such tuples.
    If input cannot be represented as a range or list of ranges Type error will be raised.
    Function allows duplicate and empty ranges in the result list
    '''
    res = []
    for rng in ranges:
        if isinstance(rng, tuple):
            res.append(rng)
        elif isinstance(rng, list):
            res.extend(rng)
        else:
            raise TypeError(
                f"{rng} cannot be converted into the range or list of ranges")
    res.sort()
    return res


def invert_indexes(indexes: List, size: int) -> List[int]:
    '''Function will return all indexes from the range [0, size) which are not 
       mentioned in the indexes list. The function expects that "indexes" list
       will be sorted and contain only unique values.
       The result list will also be sorted and contain only unique values.
    '''
    res = []
    j = 0
    for i in range(size):
        if j < len(indexes) and i == indexes[j]:
            j += 1
        else:
            res.append(i)
    return res
