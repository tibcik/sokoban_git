""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: solver.py
Verzió: 1.0.0
--------------------
sokoban.solver.solver

Sokoban megoldó kiegészítő metódusok

Metódusok:
    initialize
    getState
    getSolvedState
    getSolutionFromExist
    getPlayerPos
    setValidSpace
    validate
    setFloors
"""
from __future__ import annotations

from math import floor
from queue import PriorityQueue

from utils import between
from sokoban.data import loader

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sokoban import Space

validSpaces = set()
walls = None
goals = None
moves = None
max_obj = 0

def initialize(layout: str, editor: bool = False):
    """initialize Csomag betöltése

    Args:
        layout (str): Játéktér karakterlánc reprezentációja
        editor (bool, optional): Az inicializálást az Editor osztály kérte. Defaults to False.
    """
    global walls, goals, moves, max_obj

    _goals = set()
    _walls = set()

    height = len(layout)
    width = max([len(x) for x in layout])

    max_obj = height * width

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

    if not editor:
        setValidSpaces()

def getState(layout: str, get_initialize: bool = False, validate: bool = False) -> tuple:
    """getState Aktuális állás lekérése

    Args:
        layout (str): Játéktér karakterlánc reprezentációja
        get_initialize (bool, optional): A csomag újratöltésének jelzése. Defaults to False.
        validate (bool, optional): A betöltött állás ellenőrzése. Defaults to False.

    Returns:
        tuple: Az állást reprezentáló tuple objektum
            (Játékos, (Doboz,Doboz,...))
    """
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
                    if not validate and box not in validSpaces:
                        return None
                    _boxes.add(box)
                elif layout[y][x] == '+':                           # player on goal
                    if validate and _player != 0:
                        return 'MorePlayer'
                    _player = x*height+y

    if validate:
        if len(goals) != len(_boxes):
            return "NotEqualBoxGoal"
        if _player == 0:
            return "NoPlayer"

    return (_player, tuple(sorted(_boxes)))

def getSolvedStates(player: int, boxes: tuple, solution: str) -> tuple:
    """getSolvedStates Egy megoldásból a lehetséges állások felderítése

    Args:
        player (int): játékos pozíciója
        boxes (tuple): dobozok pozícióji
        solution (str): megoldás karakterlánca

    Returns:
        tuple: lehetséges állások a megoldáshoz
    """
    global moves, walls

    boxes = list(boxes)

    states = []

    #if solution[0].islower():
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

def getSolutionFromExist(player: int, boxes: tuple, solution_state: tuple) -> str:
    """getSolutionFromExist Megtalált mefoldás lekérdezése

    Args:
        player (int): játékos pozíciója
        boxes (tuple): dobozok pozíciói
        solution_state (tuple): keresett állás

    Returns:
        str: megoldás
    """
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

def getPlayerPos(player: int, boxes: tuple) -> tuple:
    """getPlayerPos A játékos által elérhető pozíciók lekérdezése

    Args:
        player (int): játékos pozíciója
        boxes (tuple): dobozok pozíciói

    Returns:
        tuple: elérhető pozíciók
    """
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
    """setValidSpaces Nem static deadlock pozíciók beállítása
    """
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

def validate(player: int, boxes: tuple) -> str | bool:
    """validate Állás ellenőrzése

    Args:
        player (int): játékos pozíciója
        boxes (tuple): dobozok pozíciói

    Returns:
        str | bool: megoldható-e, vagy a megoldás akadálya
    """
    global goals, walls, moves, max_obj

    visited = set()
    visited.add(player)
    visited_box = 0
    visited_goal = 0
    actions = [player+move for move in moves]
    while actions:
        pos = actions.pop()

        if not between(pos, 0, max_obj):
            return 'NotClosed'

        if pos in visited or pos in walls:
            continue
        if pos in boxes:
            visited_box += 1
        if pos in goals:
            visited_goal += 1

        visited.add(pos)
        actions.extend([pos+move for move in moves])

    if visited_box != len(boxes) or visited_goal != len(goals):
        return 'NotReachableBoxGoal'

    return True

def setFloors(space: Space, player: int):
    """setFloors Padlók beállítása, az elérhető helyek alapján

    Args:
        space (Space): Játéktér objektum
        player (int): Játékos pozíciója
    """
    global walls, moves

    visited = set()
    actions = [player+move for move in moves]

    for x in range(space.size[0] - 1):
        for y in range(space.size[1] - 1):
            if space[x,y] == loader.SOKOBAN_FLOOR:
                space[x,y] = loader.SOKOBAN_EMPTY

    while actions:
        pos = actions.pop()

        if pos in visited or pos in walls:
            continue

        x = floor(pos / (space.size[1] + 1))
        y = pos % (space.size[1] + 1)

        if space[x,y] & loader.SOKOBAN_EMPTY:
            space[x,y] = loader.SOKOBAN_FLOOR

        visited.add(pos)
        actions.extend([pos+move for move in moves])