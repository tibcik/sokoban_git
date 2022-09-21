"""Mentések kezelése

A mentések egy json fájlban tároljuk melynek felépítése:
{
    'saves': [
        {
            'player_name': (str),
            'last_player': (bool)
            'current_set': (str),
            'current_level': (int),
            'done': {
                'set_name(str)': [
                    {'moves': (int), 'time': (float), 'best_moves': (int), 'best_time': (float)},
                    ...
                ]...
            }
        }
    ],
    'setup': {
        'skin': (str),
        'res': (list[int]),
        'music_volume': (int[0...10]),
        'sound_volume': (int[0...10])
    }
}
"""
from __future__ import annotations


from copy import copy
import os
import json
from . import loader

from sokoban import config

from typing import TYPE_CHECKING, NoReturn
if TYPE_CHECKING:
    pass

save_file_path = config.DATA_PATH
save_file_name = 'save.json'

saves = {'saves': [{},{},{}]}

def get_players() -> list[str]:
    """Játékosok neveinek listája

    Returns:
        list[str]: Játékosok neveinek listája, nem használt slot esetén None
    """
    players = []
    for save in saves['saves']:
        if 'player_name' in save:
            players.append(save['player_name'])
        else:
            players.append(None)

    return players

def get_last_player_id() -> int:
    """Utoljára kiválasztott játékos azonosítója

    Returns:
        int: Utoljára kiválasztott játékos azonosítója, ha nem volt még akkor -1
    """
    for id in range(len(saves['saves'])):
        if 'last_player' in saves['saves'][id]:
            return id

    return -1

def get_player(id: int | None = None) -> str | None:
    """Adott azonosítójú játékos neve

    Args:
        id (int | None, optional): Játékos azonosítója, ha None akkor előzőleg használt. Defaults to None.

    Returns:
        str | None: Játékos neve, ha nem található None
    """
    id = get_last_player_id() if id is None else id
    if 'player_name' in saves['saves'][id]:
        return copy(saves['saves'][id]['player_name'])

    return None

def get_current_set(id: int | None = None) -> str:
    """Utoljára használt pályakészlet neve egy adott játékosnál

    Args:
        id (int | None, optional): Játékos azonosítója, ha None akkor előzőleg használt. Defaults to None.

    Returns:
        str: pályakészlet neve
    """
    id = get_last_player_id() if id is None else id
    return copy(saves['saves'][id]['current_set'])

def get_current_level(id: int | None = None) -> int:
    """Utoljára játszott szint száma egy adott játékosnál

    Args:
        id (int | None, optional): Játékos azonosítója, ha None akkor előzőleg használt. Defaults to None.

    Returns:
        str: szint száma
    """
    id = get_last_player_id() if id is None else id
    return copy(saves['saves'][id]['current_level'])

def get_setup() -> dict | None:
    """Beállítások

    Returns:
        dict | None: {'skin': (str), 'res': (list[int]), 'music_volume': (int[0...10]), 'sound_volume': (int[0...10])
            ha nem létezik akkor None
    """
    if 'setup' not in saves:
        return None

    return copy(save['setup'])

def get_level_statistic(set_name: str, level: int, id: int | None = None) -> dict | None:
    """Pálya statisztikák

    Args:
        set_name (str): pályakészlet neve
        level (int): pálya száma
        id (int | None, optional): Játékos azonosítója, ha None akkor előzőleg használt. Defaults to None.

    Returns:
        dict | None: {'moves': (int), 'time': (float), 'best_moves': (int), 'best_time': (float)}
            ha még nem lett elkezdve akkor None
    """
    id = get_last_player_id() if id is None else id
    save = saves['saves'][id]

    if set_name not in save['done'] or level >= len(save['done'][set_name]):
        return None

    return copy(save['done'][set_name][level])

def get_set_statistic(set_name: str, id: int | None = None) -> dict | None:
    """Pályakészlet statisztikák

    Args:
        set_name (str): pályakészlet neve
        id (int | None, optional): Játékos azonosítója, ha None akkor előzőleg használt. Defaults to None.

    Returns:
        dict | None: {'moves': (int), 'time': (float), 'best_moves': (int), 'best_time': (float), 'done_levels': int}
            ha még nem lett elkezdve akkor None
    """
    id = get_last_player_id() if id is None else id
    save = saves['saves'][id]

    if set_name not in save['done']:
        return None

    stats = {'moves': 0, 'time': 0, 'best_moves': 0, 'best_time': 0, 'done_levels': 0}
    for level in save['done'][set_name]:
        stats['moves'] += level['moves']
        stats['time'] += level['time']
        stats['best_moves'] += level['best_moves']
        stats['best_time'] += level['best_time']
        if level['best_moves'] > 0:
            stats['done_levels'] += 1

    return stats

def get_statistic(id: int | None = None) -> dict:
    """Játékos összesített statisztikák

    Args:
        id (int | None, optional): Játékos azonosítója, ha None akkor előzőleg használt. Defaults to None.

    Returns:
        dict: {'moves': (int), 'time': (float), 'best_moves': (int), 'best_time': (float), 'done_levels': int}
    """
    id = get_last_player_id() if id is None else id
    save = saves['saves'][id]

    stats = {'moves': 0, 'time': 0, 'best_moves': 0, 'best_time': 0, 'done_levels': 0}
    for set_name in save['done']:
        set_stat = get_set_statistic(id, set_name)
        stats['moves'] += set_stat['moves']
        stats['time'] += set_stat['time']
        stats['best_moves'] += set_stat['best_moves']
        stats['best_time'] += set_stat['best_time']
        stats['done_levels'] += set_stat['done_levels']

    return stats

def save(id: int):
    """Adatok mentése

    Args:
        id (int): Játékos azonosítója
    """
    for i in range(3):
        if 'last_player' in saves['saves'][i] and i != id:
            del(saves['saves'][i]['last_player'])
        elif i == id:
            saves['saves'][i]['last_player'] = True
    
    with open(f"{save_file_path}{save_file_name}", 'w', encoding="utf8") as f:
        json.dump(saves, f, indent=4)

def set_last_player(id: int):
    """Utoljára kiválasztott játékos beállítása

    Args:
        id (int): Játékos azonosítója
    """
    save(id)

def remove_player(id: int | None = None):
    """Játékos eltávolítása

    Args:
        id (int | None, optional): Játékos azonosítója, ha None akkor előzőleg használt. Defaults to None.
    """
    id = get_last_player_id() if id is None else id
    saves['saves'][id] = {}

    save(-1)

def add_player(player: str, id: int | None = None):
    """Új játékos hozzáadása, vagy játékos nevének megváltoztatása

    Args:
        player (str): játékos neve
        id (int | None, optional): Játékos azonosítója, ha None akkor előzőleg használt. Defaults to None.
    """
    id = get_last_player_id() if id is None else id
    if 'player_name' in saves['saves'][id]: # létező mentés, csak átnevezés
        saves['saves'][id]['player_name'] = player
    else: # új játékos
        saves['saves'][id] = {'player_name': player, 'current_set': loader.DEFAULT_SET, 'current_level': 0, 'current_setup': {}, 'done': {}}

    save(id)

def set_current_set(set_name: str, id: int | None = None):
    """Aktuális pályakészlet beállítása

    Args:
        set_name (str): Pályakészlet neve
        id (int | None, optional): Játékos azonosítója, ha None akkor előzőleg használt. Defaults to None.
    """
    id = get_last_player_id() if id is None else id
    saves['saves'][id]['current_set'] = set_name

    save(id)

def set_current_level(level: int, id: int | None = None):
    """Aktuális pálya beállítása

    Args:
        level (int): pálya száma
        id (int | None, optional): Játékos azonosítója, ha None akkor előzőleg használt.. Defaults to None.
    """
    id = get_last_player_id() if id is None else id
    saves['saves'][id]['current_level'] = level

    save(id)

def set_setup(skin: str, music_volume: int, sound_volume: int, res: tuple[int],
    id: int | None = None):
    """Beállítások mentése

    Args:
        skin (str): Kinézet neve
        music_volume (int): zene hangereje
        sound_volume (int): hangok hangereje
        res (tuple[int]): felbontás
        id (int | None, optional): Játékos azonosítója, ha None akkor előzőleg használt. Defaults to None.
    """
    id = get_last_player_id() if id is None else id

    data = {'skin': skin, 'music_volume': music_volume, 'sound_volume': sound_volume,
        'res': res}
    saves['setup'] = data

    save(id)

def done_level(set_name: str, level: int, moves: int, time: float, done: bool,
    id: int | None = None):
    """Pálya statisztikák mentése

    Args:
        set_name (str): pályakészlet neve
        level (int): pálya száma
        moves (int): lépések száma
        time (float): eltelt idő
        done (bool): befejezett-e
        id (int | None, optional): Játékos azonosítója, ha None akkor előzőleg használt. Defaults to None.
    """
    id = get_last_player_id() if id is None else id
    if set_name not in saves['saves'][id]['done']:
        saves['saves'][id]['done'][set_name] = []
    if len(saves['saves'][id]['done'][set_name]) == level:
        saves['saves'][id]['done'][set_name].append({'moves': 0, 'time': 0, 'best_moves': 0, 'best_time': 0})
    
    level_stat = get_level_statistic(set_name, level, id)
    if level_stat is None:
        level_stat = {'moves': 0, 'time': 0, 'best_moves': 0, 'best_time': 0}
    if done:
        if moves < level_stat['best_moves'] or level_stat['best_moves'] == 0:
            level_stat['best_moves'] = moves
        if time < level_stat['best_time'] or level_stat['best_time'] == 0:
            level_stat['best_time'] = time

    level_stat['moves'] += moves
    level_stat['time'] += time

    saves['saves'][id]['done'][set_name][level] = level_stat

    save(id)

# modul init
# mentések betöltése
if not os.path.exists(f"{save_file_path}{save_file_name}"):
    os.makedirs(save_file_path, exist_ok = True)
    with open(f"{save_file_path}{save_file_name}", 'x', encoding="utf8") as f:
        json.dump(saves, f, indent=4)

with open(f"{save_file_path}{save_file_name}", 'r', encoding="utf8") as f:
    saves = json.load(f)