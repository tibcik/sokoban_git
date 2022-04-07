import os
import json
import numpy as np

SOKOBAN_EMPTY = 1
SOKOBAN_FLOOR = 2
SOKOBAN_WALL = 4
SOKOBAN_GOAL = 8
SOKOBAN_BOX = 16
SOKOBAN_PLAYER = 32

SPACE_TYPES = {
                '_': SOKOBAN_EMPTY,
                ' ': SOKOBAN_FLOOR,
                '#': SOKOBAN_WALL,
                '.': SOKOBAN_FLOOR | SOKOBAN_GOAL,
                '$': SOKOBAN_FLOOR | SOKOBAN_BOX,
                '@': SOKOBAN_FLOOR | SOKOBAN_PLAYER,
                '+': SOKOBAN_FLOOR | SOKOBAN_GOAL | SOKOBAN_PLAYER,
                '*': SOKOBAN_FLOOR | SOKOBAN_GOAL | SOKOBAN_BOX
                }

SETS_DIR = './sets/'
DEFAULT_SET = 'default'

_selected_set = ''

import unicodedata
import re

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def _jload_set(set_name):
    global SETS_DIR, _selected_set
    set_name = set_name or _selected_set
    set_name = slugify(set_name)
    path = f"{SETS_DIR}{set_name}.jset"
    if not os.path.exists(path) or not os.path.isfile(path):
        return None

    _selected_set = set_name
    
    with open(path, 'r', encoding='UTF-8') as f:
        raw_data = f.read()
        data = json.JSONDecoder(strict=False).decode(raw_data)
    return data

def jget_info(level = None, set_name = None):
    data = _jload_set(set_name)
    if data is None:
        return
    
    if level is None:
        return data['set']['info']
    else:
        if level >= 0 and level < len(data['set']['levels']):
            return data['set']['levels'][level]['info']

    return None

def _jget_data(data):
    global SPACE_TYPES

    level = None
    cols = 0

    for line in data:
        row = []
        for char in line:
            if char in SPACE_TYPES:
                row.append(SPACE_TYPES[char])
        
        if cols == 0:
            cols = len(row)
        elif cols != len(row) or len(row) == 0:
            print(level)
            return None #TODO hibakezelés

        if level is None:
            level = np.array([row], np.byte)
        else:
            level = np.r_[level, np.array([row], np.byte)]

    return level

def jget_data(level, set_name = None):
    data = _jload_set(set_name)
    if data is None:
        return

    if level >= 0 and level < len(data['set']['levels']):
        return _jget_data(data['set']['levels'][level]['data'])

    return None

def jget_levels(set_name = None):
    data = _jload_set(set_name)
    if data is None:
        return

    return len(data['set']['levels'])

def _jsave_set(set_name, data):
    global SETS_DIR, _selected_set
    set_name = set_name or _selected_set
    set_name = slugify(set_name)
    path = f"{SETS_DIR}{set_name}.jset"

    _selected_set = set_name

    json.dump(data, open(path, "w", encoding="UTF-8"))

def jset_info(level, name = '', dificulty = 1, description = '', set_name = None):
    data = _jload_set(set_name)
    if data is None:
        data = {'set': {'info': {'name': '', 'dificulty': 1, 'description': ''}, 'levels': []}}

    if level is None:
        info = data['set']['info']
    else:
        if level not in range(len(data['set']['levels']) + 1):
            return None
        if level == len(data['set']['levels']):
            data['set']['levels'].append({'info': {'name': str(len(data['set']['levels'])), 'dificulty': 1, 'description': ''}, 'data': ''})
        
        info = data['set']['levels'][level]['info']

    info['name'] = name if name else info['name']
    info['dificulty'] = dificulty if dificulty else info['dificulty']
    info['description'] = description if description else info['description']

    _jsave_set(set_name, data)

    return level

def jset_data(level, raw_data, set_name = None):
    data = _jload_set(set_name)
    if data is None or level not in range(len(data['set']['levels'])):
        return None

    val_types = list(SPACE_TYPES.values())
    key_types = list(SPACE_TYPES.keys())

    data_array = []
    for line in raw_data:
        row = ''
        for obj in line:
            i = val_types.index(obj) if obj in val_types else -1
            if i != -1:
                row += key_types[i]
        data_array.append(row)

    data['set']['levels'][level]['data'] = data_array

    _jsave_set(set_name, data)

def _get_set_info(f):
    info = {'Name': '', 'Levels': '', 'Dificulty': '', 'Description': ''}

    data_name = None

    while True:
        line = f.readline()
        if not line:
            return None #TODO hibakezelés

        if line[0] != '+':
            data_name = [x for x in info if not info[x]]
            data_name = data_name[0] if len(data_name) > 0 else None
            
        if data_name is None:
            if line.strip() == 'LEVELS':
                return info
            else:
                return None #TODO hibakezelés

        jump = len('+' if line[0] == '+' else f"{data_name}: ")
        if line[0] != '+' and line[0:jump-2] != data_name:
            return None #TODO hibakezelés
        info[data_name] += ('\n' if line[0] == '+' else '') + line[jump:].strip()
        if data_name == 'Levels':
            info[data_name] = int(info[data_name])

    return None #TODO hibakezelés

def _get_level_info(f):
    info = {'Name': '', 'Dificulty': '', 'Description': ''}
    data_name = None

    while True:
        line = f.readline()
        if not line:
            return #TODO hibakezelés

        if line[0] != '+':
            data_name = [x for x in info if not info[x]]
            data_name = data_name[0] if len(data_name) > 0 else None
            
        if data_name is None:
            if line.strip() == 'LEVEL':
                return info
            else:
                return None #TODO hibakezelés

        jump = len('+' if line[0] == '+' else f"{data_name}: ")
        if line[0] != '+' and line[0:jump-2] != data_name:
            return None #TODO hibakezelés
        info[data_name] += ('\n' if line[0] == '+' else '') + line[jump:].strip()

def _get_level(f):
    global SPACE_TYPES

    level = None
    cols = 0

    while True:
        line = f.readline()
        if not line:
            return #TODO hibakezelés
            
        if line.strip() == "END":
            return level

        row = []
        for char in line:
            if char in SPACE_TYPES:
                row.append(SPACE_TYPES[char])
        
        if cols == 0:
            width = len(row)
        elif cols != len(row) or len(row) == 0:
            return None #TODO hibakezelés

        if level is None:
            level = np.array([row], np.byte)
        else:
            level = np.r_[level, np.array([row], np.byte)]

def _jump_level(f):
    while True:
        line = f.readline()
        if not line:
            return False#TODO hibakezelés
            
        if line.strip() == "END":
            return True

def jget_sets():
    global SETS_DIR
    set_names = []
    files = os.listdir(SETS_DIR)
    for file in files:
        if os.path.isfile(f"{SETS_DIR}{file}") and file[-5:] == ".jset":
            set_name = file[:-5]
            set_names.append(set_name)

    return set_names

def get_info(set_name, level = None):
    global SETS_DIR
    path = f"{SETS_DIR}{set_name}.set"
    if not os.path.exists(path) or not os.path.isfile(path):
        return

    info = None
    l_info = None

    with open(path, 'r', encoding = 'UTF-8') as f:
        info = _get_set_info(f)

        if level is not None:
            if level < 0 or level >= info['Levels']:
                return None #TODO hibakezelés
            for i in range(info['Levels']):
                l_info = _get_level_info(f)
                if i == level:
                    break
                _jump_level(f)

    if l_info is not None:
        return l_info
    
    return info

def get_level(set_name, level):
    global SETS_DIR
    path = f"{SETS_DIR}{set_name}.set"
    if not os.path.exists(path) or not os.path.isfile(path):
        return

    with open(path, 'r', encoding = 'UTF-8') as f:
        info = _get_set_info(f)

        if level < 0 or level >= info['Levels']:
            return None #TODO hibakezelés

        for i in range(info['Levels']):
            _get_level_info(f)
            if i == level:
                return _get_level(f)
            _jump_level(f)

def set_info(set_name, name, dificulty, description):
    global SETS_DIR
    path = f"{SETS_DIR}{set_name}.set"
    if not os.path.exists(path) or not os.path.isfile(path):
        return

    i = get_info(set_name)
    infos = {'Name': name, 'Levels': str(i['Levels']), 'Dificulty': dificulty, 'Description': description}

    with open(path, 'r+', encoding = "UTF-8") as f:
        with open(f"{SETS_DIR}set.tmp", "a", encoding='UTF-8') as tmp_f:
            while True:
                line = f.readline()
                if not line:
                    return #TODO hibakezelés
                if line.strip() == "LEVELS":
                    #f.truncate(f.tell())
                    for info in infos:
                        lines = infos[info].split('\n')
                        first = True
                        for l in lines:
                            if first:
                                tmp_f.write(f"{info}: {l}\n")
                                first = False
                            else:
                                tmp_f.write(f"+{l}\n")
                    tmp_f.write('LEVELS\n')
                    tmp_f.write(f.read())
                    break
    
    os.unlink(path)
    os.rename(f"{SETS_DIR}set.tmp", path)

def _add_level_info(f, name, dificulty, description):
    global SPACE_TYPES
    infos = {'Name': name, 'Dificulty': dificulty, 'Description': description}
    for info in infos:
        lines = infos[info].split('\n')
        first = True
        for l in lines:
            if first:
                f.write(f"{info}: {l}\n")
                first = False
            else:
                f.write(f"+{l}\n")
    f.write("LEVEL\n")

def _add_level_data(f, data):
    global SPACE_TYPES

    val_types = list(SPACE_TYPES.values())
    key_types = list(SPACE_TYPES.keys())

    for row in data:
        for obj in row:
            i = val_types.index(obj) if obj in val_types else -1
            if i != -1:
                f.write(key_types[i])
        f.write('\n')
    f.write("END\n")

def set_level_info(set_name, level, name, dificulty, description):
    global SETS_DIR
    path = f"{SETS_DIR}{set_name}.set"
    if not os.path.exists(path) or not os.path.isfile(path):
        return

    cur_level = 0

    with open(path, 'r', encoding = 'UTF-8') as f:
        with open(f"{SETS_DIR}set.tmp", "a", encoding='UTF-8') as tmp_f:
            while True:
                line = f.readline()
                if not line:
                    break

                tmp_f.write(line)
                
                if line.strip() == 'LEVELS' or line.strip() == 'END':
                    if cur_level == level:
                        while True:
                            line = f.readline()
                            if not line or line.strip() == 'LEVEL':
                                break
                        _add_level_info(tmp_f, name, dificulty, description)
                    cur_level += 1

    os.unlink(path)
    os.rename(f"{SETS_DIR}set.tmp", path)

def set_level_data(set_name, level, data):
    global SETS_DIR
    path = f"{SETS_DIR}{set_name}.set"
    if not os.path.exists(path) or not os.path.isfile(path):
        return

    cur_level = 0

    with open(path, 'r', encoding = 'UTF-8') as f:
        with open(f"{SETS_DIR}set.tmp", "a", encoding='UTF-8') as tmp_f:
            while True:
                line = f.readline()
                if not line:
                    break

                tmp_f.write(line)
                
                if line.strip() == 'LEVEL':
                    if cur_level == level:
                        while True:
                            line = f.readline()
                            if not line or line.strip() == 'END':
                                break
                        _add_level_data(tmp_f, data)
                    cur_level += 1

    os.unlink(path)
    os.rename(f"{SETS_DIR}set.tmp", path)