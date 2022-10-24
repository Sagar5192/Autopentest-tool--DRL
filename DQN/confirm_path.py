import os
import sys
sys.path.append('./learn')
from generateMap import generateMap
import numpy as np
np.set_printoptions(suppress=True)

generateMapClass = generateMap()
MAP = generateMapClass.sendMap
line = generateMapClass.line

FIELD_DICTS = {'S': 0.01, 'G': 100.0, 'U': -1.0}
MIN = 9999999999

aa = np.zeros((line, line), dtype=float)
bb = np.zeros((line, line), dtype=float)

all_paths = []

def _find_pos(field_type):
    return np.array(list(zip(*np.where(
    MAP == FIELD_DICTS[field_type]
))))

def _start_state():
    return _find_pos('S')[0]

def _end_state():
    return _find_pos('G')[0]



edgeLinks = dict()
size = 0
stack = []

def addEdge(a,b):
    global edgeLinks
    if a not in edgeLinks:
        edgeLinks[a] = set()
    if b not in edgeLinks:
        edgeLinks[b] = set()
    edgeLinks[a].add(b)


def Check(graph, s, e, path=[]):
    path = path + [s]
    if s == e:
        return [path]

    paths = []
    for node in graph[s]:
        if node not in path:
            ns = Check(graph, node, e, path)
            for n in ns:
                paths.append(n)
    return paths

def load(start, end):  
    os.system('cp ../mulval_result/ARCS.CSV ./processdata/ARCS.txt')

    with open('./processdata/ARCS.txt', 'r') as ff:
        lines = ff.readlines()
        count = len(lines)
    with open('./processdata/ARCS.txt', 'w') as n:
        n.write(str(line) + ',' + str(count) + ',-1\n')
        n.writelines(lines)
        n.writelines(str(end) + ',' + str(start) + ',-1')

    f = open('./processdata/ARCS.txt', 'r')

    global size, edgeLinks
    size, edgeCount, op = map(int, f.readline().split(','))
    for i in range(edgeCount):
        b,a,pop = f.readline().split(',')
        addEdge(a,b)
    re = f.readline()
    f.close()
    return re

def get_score(MAP, all_paths):
    score_map = MAP.copy()
    line_number = len(all_paths)
    new_MAP = -(np.ones((line_number + 2, line_number + 2), dtype=np.float))

    matrix_list = []
    for data in all_paths:
        start_score = 0
        end_score = 0
        start_score = score_map[tuple(data[0])]
        end_score = score_map[tuple(data[-1])]
        mid_score = 0

        for i in data[1:-1]:
            mid_score = mid_score + score_map[tuple(i)]

        matrix_line = [start_score, mid_score, end_score]
        matrix_list.append(matrix_line)

    for data in enumerate(matrix_list):
        new_MAP[tuple([0, 0])] = data[1][0]
        new_MAP[tuple([0, data[0] + 1])] = data[1][1]
        new_MAP[tuple([data[0] + 1, 0])] = 0
        new_MAP[tuple([data[0] + 1, line_number + 1])] = data[1][2]
        new_MAP[tuple([line_number + 1, data[0] + 1])] = 0

    return new_MAP


if __name__ == '__main__':

    start_state = _start_state()
    end_state = _end_state()
    start = start_state[0]
    end = 1
    maze = MAP
    all_path=[]
    aa={}

    b,a,po=load(start+1, end).split(',')
    patth=[]
    allpath = Check(edgeLinks,a,b)
    for p in allpath:
        bb = []
        for i in p:
            if int(i) != 1:
                bb.append([int(i)-1,int(p[p.index(i)+1])-1])
        all_path.append(bb)
    result = get_score(maze, all_path)

    np.save('./processdata/path_num.npy', len(result))
    np.savetxt('./processdata/newmap.txt', result)
    all_path = np.array(all_path, dtype=object)

    file_name="processdata/all_paths.npy"
    np.save("./"+file_name, all_path)
    #print("Attack matrix saved in 'DQN/{}'".format(file_name))
