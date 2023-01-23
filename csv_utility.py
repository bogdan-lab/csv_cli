from typing import List, Tuple


def get_col_indexes(col_indexes: List[int], header: str, col_names: List[str],
                    delimiter: str) -> List[int]:
    '''Returns column indexes selected by user either directly or according to
    column names in the header'''
    if col_indexes is not None:
        return col_indexes
    name_list = [el.strip() for el in header.casefold().split(delimiter)]
    return [name_list.index(cn.casefold()) for cn in col_names]


def select_from_row(row: str, delimiter: str, col_indexes: List[int]):
    '''Filters the given row in the way, that only the given column indexes are left in it.
       Columns in the row are defined by delimiter.
       Note that the result will be still string with the same delimiter but
       it will contain only the chosen columns
    '''
    l = row.split(delimiter)
    return delimiter.join(l[i] for i in col_indexes)


def selected_rows_generator(content: Tuple[str], delimiter: str,
                            col_indexes: List[int], row_indexes: List[int]):
    '''This generator yields rows with row_indexes, which are already filtered
       and contain only col_indexes columns
    '''
    for i in row_indexes:
        l = content[i].split(delimiter)
        res = delimiter.join(l[j] for j in col_indexes)
        if res:
            yield res


def expand_int_ranges(ranges: List[Tuple[int]]) -> List[int]:
    '''This function will take a list of ranges (start, end) and expend those into the actual range of integers.
        Note that ranges are semi intervals, start is included and end is not.
        For example, input [(1,2), (4,6)] will be converted into [1, 4, 5].
        Note that function expects the list of ranges to be sorted by the left edge.
        The resulting list will contain only unique integers which are present in at least one of the given ranges.
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


def get_row_indexes(total_row_count: int, head: int, tail: int,
                    from_index: List[int], to_index: List[int],
                    r_index: List[int]) -> List[int]:
    '''This function will return list of row indexes based of head and tail counters,
       ranges defined by from_index and to_index arrays and list of exact indexes -
       r_index.
       Returned values will be normalized to the size of the table and in case when
       they should be combined function will guarantee that indexes in the returned 
       list will be unique and will not crossect.
    '''
    if head is None and tail is None and from_index is None and r_index is None:
        return expand_int_ranges([(0, total_row_count)])

    ranges = []
    if head is not None:
        ranges.append((0, min(head, total_row_count)))
    if tail is not None:
        ranges.append((max(0, total_row_count - tail), total_row_count))
    if from_index is not None:
        ranges.extend(map(
            lambda x: (min(x[0], total_row_count), min(x[1], total_row_count)),
            zip(from_index, to_index)))
    if r_index is not None:
        ranges.extend((min(x, total_row_count), min(
            x+1, total_row_count)) for x in r_index)
    ranges.sort(key=lambda x: x[0])
    return expand_int_ranges(ranges)


def merge_particular_c_indexes(c_index: List[int], c_name: List[str],
                               header: str, delimiter: str) -> List[int]:
    '''Function takes as an input two lists which define particular columns in the table.
       The first list contains columns indexes, the second - columns names.
       Function converts name list into the one with indexes and merges
       it with the initial index list (without sorting).
       The merge result is returned.
    '''
    if c_index is None and c_name is None:
        return None
    res = []
    if c_index is not None:
        res.extend(c_index)
    if c_name is not None:
        res.extend(get_col_indexes(None, header, c_name, delimiter))
    return res


def invert_indexes(indexes: List, size: int) -> List[int]:
    '''Function will return all indexes from the range [0, size) which are not 
       mentioned in the indexes list. The function expects that "indexes" list
       will be sorted
    '''
    res = []
    j = 0
    for i in range(size):
        if j < len(indexes) and i == indexes[j]:
            j += 1
        else:
            res.append(i)
    return res
