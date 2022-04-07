import os
import json
from datetime import datetime
import game.game.loader as loader

save_file_path = './saves/'
save_file_name = 'save.json'

saves = {'saves': [{},{},{}]}
"""
JSON struct
{
    'saves': [
        {
            'player_name': 'player_name',
            'last_player': true
            'current_set': 'set_name',
            'current_level': level_num,
            'current_setup': {
                'boxes': [[x,y],[x,y],...]
                'player': [x,y]
            },
            'done': {
                'set_name': [
                    {'moves': moves_num, 'time': 'time', 'best_moves': moves_num, 'best_time': 'time'},
                    ...
                ]
            }
        }
    ]
}
"""

def get_players():
    players = []
    for save in saves['saves']:
        if 'player_name' in save:
            players.append(save['player_name'])
        else:
            players.append(None)

    return players

def get_last_player_id():
    for id in range(len(saves['saves'])):
        if 'last_player' in saves['saves'][id]:
            return id

    return -1

def get_player(id: int = None):
    id = get_last_player_id() if id is None else id
    if 'player_name' in saves['saves'][id]:
        return saves['saves'][id]['player_name']

    return None

def get_current_set(id = None):
    id = get_last_player_id() if id is None else id
    return saves['saves'][id]['current_set']

def get_current_level(id = None):
    id = get_last_player_id() if id is None else id
    return saves['saves'][id]['current_level']

def get_current_setup(id = None):
    id = get_last_player_id() if id is None else id
    if len(saves['saves'][id]['current_setup']) == 0:
        return None

    return save['current_setup']

def get_level_statistic(set_name, level, id = None):
    id = get_last_player_id() if id is None else id
    save = saves['saves'][id]

    if set_name not in save['done'] or level >= len(save['done'][set_name]):
        return None

    return save['done'][set_name][level]

def get_set_statistic(set_name, id = None):
    id = get_last_player_id() if id is None else id
    save = saves['saves'][id]

    if set_name not in save['done']:
        return None

    stats = {'moves': 0, 'time': 0, 'best_moves': 0, 'best_time': 0, 'done_levels': len(save['done'][set_name])}
    for level in save['done'][set_name]:
        stats['moves'] += level['moves']
        stats['time'] += datetime.strptime(level['time'], '%d %H%M%S')
        stats['best_moves'] += level['best_moves']
        stats['best_time'] += datetime.strptime(level['best_time'], '%H:%M:%S')

    return stats

def get_statistic(id = None):
    id = get_last_player_id() if id is None else id
    save = saves['saves'][id]

    stats = {'moves': 0, 'time': 0, 'best_moves': 0, 'best_time': 0}
    for set_name in save['done']:
        set_stat = get_set_statistic(id, set_name)
        stats['moves'] += set_stat['moves']
        stats['time'] += set_stat['time']
        stats['best_moves'] += set_stat['best_moves']
        stats['best_time'] += set_stat['best_time']

    return stats

def save(id):
    for i in range(3):
        if 'last_player' in saves['saves'][i] and i != id:
            del(saves['saves'][i]['last_player'])
        elif i == id:
            saves['saves'][i]['last_player'] = True
    
    with open(f"{save_file_path}{save_file_name}", 'w', encoding="utf8") as f:
        json.dump(saves, f)

def set_last_player(id):
    save(id)

def remove_player(id = None):
    id = get_last_player_id() if id is None else id
    saves['saves'][id] = {}

    save(-1)

def add_player(player, id = None):
    id = get_last_player_id() if id is None else id
    if 'player_name' in saves['saves'][id]: # létező mentés, csak átnevezés
        saves['saves'][id]['player_name'] = player
    else: # új játékos
        saves['saves'][id] = {'player_name': player, 'current_set': loader.DEFAULT_SET, 'current_level': 0, 'current_setup': {}, 'done': {}}

    save(id)

def set_current_set(set_name, id = None):
    id = get_last_player_id() if id is None else id
    saves['saves'][id]['current_set'] = set_name

    save(id)

def set_current_level(level, id = None):
    id = get_last_player_id() if id is None else id
    saves['saves'][id]['current_level'] = level

    save(id)

def set_current_setup(boxes, player, id = None):
    id = get_last_player_id() if id is None else id
    if boxes is None:
        saves['saves'][id]['current_setup'] = {}
    else:
        boxes_pos = []
        for box in boxes:
            boxes_pos.append([box.pos.p1, box.pos.p2])
        player_pos = [player.pos.p1, player.pos.p2]
        saves['saves'][id]['current_setup']['boxes'] = boxes_pos
        saves['saves'][id]['current_setup']['player'] = player_pos

    save(id)

def done_level(set_name, level, moves, time, id = None):
    id = get_last_player_id() if id is None else id
    if set_name not in saves['saves'][id]['done']:
        saves['saves'][id]['done'][set_name] = []
    if len(saves['saves'][id]['done'][set_name]) == level:
        saves['saves'][id]['done'][set_name].append({'moves': 0, 'time': '00 00:00:00'})
    
    level_stat = get_level_statistic(id, set_name, level)
    if moves < level_stat['best_moves']:
        level_stat['best_moves'] = moves
    if time < level_stat['best_time']:
        level_stat['best_time'] = time

    level_stat['moves'] += moves
    level_stat['time'] += time
    level_stat['time'] = datetime.strftime(level_stat['time'], '%d %H:%M:%S')
    level_stat['best_time'] = datetime.strftime(level_stat['time'], '%H:%M:%S')

    saves['saves'][id]['done'][set_name][level] = level_stat

    save(id)

##### module init #####
if not os.path.exists(f"{save_file_path}{save_file_name}"):
    os.makedirs(save_file_path, exist_ok = True)
    with open(f"{save_file_path}{save_file_name}", 'x', encoding="utf8") as f:
        json.dump(saves, f)

with open(f"{save_file_path}{save_file_name}", 'r', encoding="utf8") as f:
    saves = json.load(f)