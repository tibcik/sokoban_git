"""Sokoban pályakészletek betöltése, módosítása, mentése

A sokoban pályakészletek json objektumként vannak tárolva melynek felépítése:
{
	"set": {
		"info": {
			"name": (str),
			"dificulty": (int),
			"description": (str)
		},
		"levels": [
			{
				"info": {
					"name": (str),
					"dificulty": (int),
					"description": (str)
				},
				"data": [
					(str[_ #.$@+*]),...
				]
			}...
        ]
    }
}"""
from __future__ import annotations

import os
import json
import numpy as np
from utils.asserts import *

import unicodedata
import re

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass

# Sokoban pálya elemei
SOKOBAN_EMPTY = 1
SOKOBAN_FLOOR = 2
SOKOBAN_WALL = 4
SOKOBAN_GOAL = 8
SOKOBAN_BOX = 16
SOKOBAN_PLAYER = 32

# Szövegként reprezentált pálya elemeinek megfelelői
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

# Modul változó az éppen használt set tárolására
_selected_set = ''

def slugify(value: str, allow_unicode: bool = False) -> str:
    """Szöveg átalakítása útvonalban használhatóvá
    [Felhasznált metódus: eredeti leírás:
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.]

    Args:
        value (str): átalakítandó szöveg
        allow_unicode (bool, optional): az átalakított szöveg tarlamazzon-e unocode karaktereket. Defaults to False.

    Returns:
        str: útvonalban használható szöveg
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def __jload_set(set_name: str | None) -> dict | None:
    """Pályakészletet beolvasása[modulon belüli használatra]

    Args:
        set_name (str | None): Pályakészlet neve, ha None akkor előzőleg használt

    Returns:
        dict | None: pályakészlet objektuma, vagy ha nem található akkor None
    """
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

def jget_info(level: int | None = None, set_name: str | None = None) -> dict | None:
    """Információ pályakészletről vagy szintről

    Args:
        level (int | None, optional): Szint száma, ha nem None akkor a szintről ad vissza információt. Defaults to None.
        set_name (str | None, optional): Pályakészlet neve, ha None akkor előzőleg használt. Defaults to None.

    Returns:
        dict | None: ha nem található a pályakészlet vagy a szint: None
            egyébként: {"name": str, "dificulty": int, "description": str}
    """
    data = __jload_set(set_name)
    if data is None:
        return None
    
    if level is None:
        return data['set']['info']
    else:
        if level >= 0 and level < len(data['set']['levels']):
            return data['set']['levels'][level]['info']

    return None

def __jget_data(data: list) -> np.ndarray | None:
    """Pálya errenőrzése és betöltése[modulon belüli használatra]

    Args:
        data (list): Pálya adata: [line(str),line(str),...]

    Returns:
        numpy.ndarray | None: pálya kérdimenziós tömb ábrázolása, hiba esetén None
    """
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
            return None #TODO hibakezelés

        if level is None:
            level = np.array([row], np.byte)
        else:
            level = np.r_[level, np.array([row], np.byte)]

    return level

def jget_data(level: int, set_name: str = None) -> np.ndarray | None:
    """Pálya errenőrzése és betöltése

    Args:
        level (int): szint száma
        set_name (str, optional): Pályakészlet neve, ha None akkor előzőleg használt. Defaults to None.

    Returns:
        numpy.ndarray | None: pálya kérdimenziós tömb ábrázolása, hiba esetén None
    """
    data = __jload_set(set_name)
    if data is None:
        return None

    if level >= 0 and level < len(data['set']['levels']):
        return __jget_data(data['set']['levels'][level]['data'])

    return None

def jget_levels(set_name: str = None) -> int:
    """A pályakészletben található pályák száma

    Args:
        set_name (str, optional): Pályakészlet neve, ha None akkor előzőleg használt. Defaults to None.

    Returns:
        int: A pályakészletben található pályák száma
    """
    data = __jload_set(set_name)
    if data is None:
        return None

    return len(data['set']['levels'])

def jget_sets() -> list[str]:
    """Elérhető pályakészletek nevei

    Returns:
        list[str]: Elérhető pályakészletek nevei
    """
    global SETS_DIR
    set_names = []
    files = os.listdir(SETS_DIR)
    for file in files:
        if os.path.isfile(f"{SETS_DIR}{file}") and file[-5:] == ".jset":
            set_name = file[:-5]
            set_names.append(set_name)

    return set_names

def __jsave_set(set_name: str, data: dict):
    """Pályakészlet mentése[modulon belüli használatra]

    Args:
        set_name (str): Pályakészlet neve.
        data (dict): pályakészlet adatai
    """
    global SETS_DIR, _selected_set
    
    assert type(set_name) == str, type_assert('set_name', set_name, str)
    assert len(set_name) > 0, f"'set_name' argumentum hossza legalább egy kell legyen"

    set_name = slugify(set_name)
    path = f"{SETS_DIR}{set_name}.jset"

    _selected_set = set_name

    json.dump(data, open(path, "w", encoding="UTF-8"))

def jset_info(level: int | None, name: str = '', dificulty: int = 1, description: str = '',
    set_name: str | None = None):
    """Pálya vagy pályakészlet adatainak mentése

    Args:
        level (int, None): Szint száma, ha None akkor az adatok a pályakészletre vonatkoznak
        name (str, optional): Pálya vagy pályakészlet neve. Defaults to ''.
        dificulty (int, optional): Pálya vagy pályakészlet nehézsége. Defaults to 1.
        description (str, optional): Pálya vagy pályakészlet leírása. Defaults to ''.
        set_name (str | None, optional): Pályakészlet neve, ha None akkor előzőleg használt. Defaults to None.
    """
    data = __jload_set(set_name)
    if data is None:
        data = {'set': {'info': {'name': '', 'dificulty': 1, 'description': ''}, 'levels': []}}

    if level is None:
        info = data['set']['info']
    else:
        if level not in range(len(data['set']['levels']) + 1):
            return #TODO: hibakezelés
        if level == len(data['set']['levels']):
            data['set']['levels'].append({'info': {'name': str(len(data['set']['levels'])), 'dificulty': 1, 'description': ''}, 'data': ''})
        
        info = data['set']['levels'][level]['info']

    info['name'] = name if name else info['name']
    info['dificulty'] = dificulty if dificulty else info['dificulty']
    info['description'] = description if description else info['description']

    __jsave_set(set_name, data)

def jset_data(level: int, raw_data: np.ndarray, set_name: str | None = None):
    """Pályakészlet egy szintjének mentése

    Args:
        level (int): Szint száma
        raw_data (np.ndarray): pálya kérdimenziós tömb ábrázolása
        set_name (str | None, optional): Pályakészlet neve, ha None akkor előzőleg használt. Defaults to None.
    """
    data = __jload_set(set_name)
    if data is None or level not in range(len(data['set']['levels'])):
        return #TODO: hibakezelés

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

    __jsave_set(set_name, data)