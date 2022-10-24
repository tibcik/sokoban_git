""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: exceptions.py
Verzió: 1.0.0
--------------------
utils.exceptions

Kivételkezelést elősegítő metódusok.

Metódusok:
    arg_type_exception
    arg_instance_exception
    instance_exception
    arg_attribute_exception
    arg_index_exception
    arg_constant_exception
"""

def arg_type_exception(name: str, v: any, t: any):
    """arg_type_exception Paraméter típusának ellenőrzése

    Args:
        name (str): paraméter neve
        v (any): paraméter értéke
        t (any): várt típus

    Raises:
        ValueError: Ha a paraméter nem a várt típusú
    """
    if type(v) != t: raise ValueError(f"Paraméter hiba! {name} -> Várt típus: {t}; kapott típus: {type(v)}.")

def arg_instance_exception(name: str, v: any, c: any):
    """arg_instance_exception Paraméter osztályának ellenőrzése

    Args:
        name (str): paraméter neve
        v (any): paraméter értéke
        c (any): várt osztály

    Raises:
        ValueError: Ha a paraméter nem az osztály leszármazottja
    """
    if not isinstance(v, c): raise ValueError(f"Paraméter hiba! {name} -> Várt osztály leszármazottja: {c}; kapott osztály: {type(v)}.")

def instance_exception(v: any, c: any):
    """instance_exception Osztály ősosztályainak ellenőrzése

    Args:
        v (any): ellenőrizendő osztály
        c (any): várt ősosztály

    Raises:
        TypeError: Ha az ősosztályok között nem szerepel a várt
    """
    if not isinstance(v, c): raise TypeError(f"Típus hiba! Leszármazottjána kell lennie a következő  osztálynak: {c}.")

def arg_attribute_exception(name: str, v: any, a: str):
    """arg_attribute_exception Paraméter egy attributumának ellenőrzése

    Args:
        name (str): paraméter neve
        v (any): paraméter értéke
        a (str): várt attributum

    Raises:
        ValueError: Ha a paraméter attributumai között nem szerepel a várt attributum
    """
    if not hasattr(v, a): raise ValueError(f"Paraméter hiba! {name} -> Várt {a} attrivutummal rendelkező osztály; kapott osztály: {type(v)}.")

def arg_index_exception(name: str, v: any, l: int):
    """arg_index_exception Paraméterként kapott lista hosszának ellenőrzése

    Args:
        name (str): paraméter neve
        v (any): paraméter értéke
        l (int): lista minimális hossza

    Raises:
        ValueError: Ha a paraméter attributumai között nem szerepel a várt attributum (__getitem__)
        IndexError: Ha a paraméterként kapott list nem elég hossza
    """
    arg_attribute_exception(name, v, "__getitem__")
    if len(v) < l: raise IndexError(f"Paraméter hiba! {name} -> Várt legalább {l} elemű listaszerű elem; kapott méret: {len(v)}")

def arg_constant_exeption(name: str, v: any, l: list):
    """arg_constant_exeption Paraméter ellenőrzése, hogy része-e egy listának

    Args:
        name (str): paraméter neve
        v (any): paraméter értéke
        l (list): a lista aminek része kell legyen

    Raises:
        ValueError: Ha nem része a kapott listának a paraméter
    """
    if v not in l: raise ValueError(f"Paraméter hiba! {name} -> Várt konstans érték a következők közül {l}; kapott érték: {v}")