from constants import *

# marker table
MARKER_TABLE = [[[[0, 1, 0, 1, 0, 0, 0, 1, 1],
                  [0, 0, 1, 1, 0, 1, 0, 1, 0],
                  [1, 1, 0, 0, 0, 1, 0, 1, 0],
                  [0, 1, 0, 1, 0, 1, 1, 0, 0]],
                 'm0'],
                [[[1, 0, 0, 0, 1, 0, 1, 0, 1],
                  [0, 0, 1, 0, 1, 0, 1, 0, 1],
                  [1, 0, 1, 0, 1, 0, 0, 0, 1],
                  [1, 0, 1, 0, 1, 0, 1, 0, 0]],
                 'm1'],
                [[[1, 0, 1, 1, 1, 0, 0, 0, 1],
                  [1, 0, 1, 0, 1, 0, 1, 1, 0],
                  [1, 0, 0, 0, 1, 1, 1, 0, 1],
                  [0, 1, 1, 0, 1, 0, 1, 0, 1]],
                 'm2'],
                [[[1, 1, 1, 1, 1, 1, 0, 0, 1],
                  [1, 1, 1, 1, 1, 0, 1, 1, 0],
                  [1, 0, 0, 1, 1, 1, 1, 1, 1],
                  [0, 1, 1, 0, 1, 1, 1, 1, 1]],
                 'm3'],
                [[[0, 0, 0, 0, 0, 0, 1, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 1],
                  [0, 0, 1, 0, 0, 0, 0, 0, 0],
                  [1, 0, 0, 0, 0, 0, 0, 0, 0]],
                 'm4'],
                [[[0, 1, 0, 1, 1, 1, 1, 0, 0],
                  [0, 1, 0, 1, 1, 0, 0, 1, 1],
                  [0, 0, 1, 1, 1, 1, 0, 1, 0],
                  [1, 1, 0, 0, 1, 1, 0, 1, 0]],
                 'm5'],
                [[[1, 1, 1, 1, 0, 1, 0, 1, 1],
                  [1, 1, 1, 1, 0, 1, 1, 1, 0],
                  [1, 1, 0, 1, 0, 1, 1, 1, 1],
                  [0, 1, 1, 1, 0, 1, 1, 1, 1]],
                 'm6'],
                [[[1, 1, 1, 0, 1, 1, 0, 0, 1],
                  [1, 1, 1, 1, 1, 0, 1, 0, 0],
                  [1, 0, 0, 1, 1, 0, 1, 1, 1],
                  [0, 0, 1, 0, 1, 1, 1, 1, 1]],
                 'm7'],
                [[[1, 1, 1, 0, 1, 0, 0, 1, 1],
                  [1, 0, 1, 1, 1, 1, 1, 0, 0],
                  [1, 1, 0, 0, 1, 0, 1, 1, 1],
                  [0, 0, 1, 1, 1, 1, 1, 0, 1]],
                 'm8'],
                [[[1, 1, 1, 1, 1, 1, 0, 1, 1],
                  [1, 1, 1, 1, 1, 1, 1, 1, 0],
                  [1, 1, 0, 1, 1, 1, 1, 1, 1],
                  [0, 1, 1, 1, 1, 1, 1, 1, 1]],
                 'm9'],
                [[[1, 1, 1, 0, 1, 0, 0, 0, 1],
                  [1, 0, 1, 1, 1, 0, 1, 0, 0],
                  [1, 0, 0, 0, 1, 0, 1, 1, 1],
                  [0, 0, 1, 0, 1, 1, 1, 0, 1]],
                 'm10']]


# match marker pattern to database record
def match_marker_pattern(marker_pattern):
    # marker_pattern is binary 3x3 array
    marker_found = False
    # store rotation (there are 4 possible rotations)
    marker_rotation = None
    # store which marker it is
    marker_name = None
    
    for marker_record in MARKER_TABLE:
        for idx, val in enumerate(marker_record[0]):    
            if marker_pattern == val: 
                marker_found = True
                marker_rotation = idx
                marker_name = marker_record[1]
                break
        if marker_found: break

    return (marker_found, marker_rotation, marker_name)