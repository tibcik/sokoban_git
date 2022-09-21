from copy import copy
from queue import PriorityQueue

validSpaces = set()
walls = None
goals = None
moves = None

def initialize(layout):
    global walls, goals, moves

    _goals = set()
    _walls = set()

    height = len(layout)
    width = max([len(x) for x in layout])

    for y in range(height):
        for x in range(width):
            if x < len(layout[y]):
                if layout[y][x] == ' ': pass                        # free space
                elif layout[y][x] == '#': _walls.add(x*height+y)     # wall
                elif layout[y][x] == '.': _goals.add(x*height+y)     # goal
                elif layout[y][x] == '*':                           # box on goal
                    _goals.add(x*height+y)
                elif layout[y][x] == '+':                           # player on goal
                    _goals.add(x*height+y)

    walls = tuple(_walls)
    goals = tuple(_goals)
    
    moves = (-1,height,1,-height) # up, right, down, left

    setValidSpaces()

def getState(layout, get_initialize = False):
    global walls, goals, moves

    if goals is None or get_initialize:
        initialize(layout)

    _boxes = set()
    _player = 0

    height = len(layout)
    width = max([len(x) for x in layout])

    for y in range(height):
        for x in range(width):
            if x < len(layout[y]):
                if layout[y][x] == ' ': pass                        # free space
                elif layout[y][x] == '@': _player = x*height+y       # player
                elif layout[y][x] == '$': _boxes.add(x*height+y)     # box
                elif layout[y][x] == '*':                           # box on goal
                    box = x*height+y
                    if box not in validSpaces:
                        return None
                    _boxes.add(box)
                elif layout[y][x] == '+':                           # player on goal
                    _player = x*height+y

    return (_player, tuple(sorted(_boxes)))

def getSolvedStates(player, boxes: tuple, solution: list[str]):
    global moves, walls

    boxes = list(boxes)

    states = []

    if solution[0].islower():
        states.append((player, getPlayerPos(player, boxes), tuple(boxes), solution))

    step = 0

    for move_char in solution:
        move = moves[0]
        if move_char.lower() == 'u':
            move = moves[0]
        elif move_char.lower() == 'r':
            move = moves[1]
        elif move_char.lower() == 'd':
            move = moves[2]
        elif move_char.lower() == 'l':
            move = moves[3]

        player += move
        if player in boxes:
            boxes[boxes.index(player)] += move
            states.append((player, getPlayerPos(player, boxes), tuple(boxes), solution[step+1:]))

        step += 1

    return tuple(states)

def getSolutionFromExist(player, boxes, solution_state):
    global moves, walls

    #if solution_state[3][0].isupper() and player == solution_state[0]:
    #    return solution_state[3]

    step = 0

    iplayer = solution_state[0]

    for move_char in solution_state[3]:
        if move_char.isupper():
            break

        move = moves[0]
        if move_char.lower() == 'u':
            move = moves[0]
        elif move_char.lower() == 'r':
            move = moves[1]
        elif move_char.lower() == 'd':
            move = moves[2]
        elif move_char.lower() == 'l':
            move = moves[3]

        iplayer += move

        step += 1

    if player == iplayer:
        return solution_state[3][step:]

    visited = set()
    visited.add(player)
    trans_table = {moves[0]: 'u', moves[1]: 'r', moves[2]: 'd', moves[3]: 'l'}
    actions = PriorityQueue()
    for move in moves:
        actions.put((1, (player+move, trans_table[move])))
    pre_moves = ""
    while True:
        _, (action, sol_moves) = actions.get()

        if action in visited or action in walls or action in boxes:
            continue

        if action == iplayer:
            pre_moves = sol_moves
            break

        visited.add(action)
        for move in moves:
            actions.put((len(sol_moves) + 1, (action+move, sol_moves+trans_table[move])))

        if actions.qsize() == 0:
            break

    return pre_moves + solution_state[3][step:]

def getPlayerPos(player, boxes):
    global moves, walls

    playerSpace = set()
    actions = [player+move for move in moves]
    while actions:
        action = actions.pop()

        if action in playerSpace or action in walls or action in boxes:
            continue

        playerSpace.add(action)
        actions.extend([action+move for move in moves])

    return tuple(sorted(playerSpace))

def setValidSpaces():
    global validSpaces, goals, walls, moves

    validSpaces = set()
    for goal in goals:
        visited = set()
        visited.add(goal)

        actions = [(goal+move, goal+move+move) for move in moves]
        while actions:
            action = actions.pop()

            if action[0] in visited:
                continue
            if action[0] in walls:
                continue
            if action[1] in walls:
                continue

            visited.add(action[0])
            actions.extend([(action[0]+move, action[0]+move+move) for move in moves])

        validSpaces.update(visited)