""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: pair.py
Verzió: 1.0.0
--------------------
utils.pair

Egy osztályos modul ami a Pair osztályt tartalmazza

A Pair osztály egy számpárt tartalmazó osztály,
használatával lehetőség van számpárokon végzett matematikai
műveletek végrehajtására.

    Használata:

    a = Pair(1, 1)
    b = Pair((2,6))
    c = Pair([7,6,8,1])
    d = a + b / c - 6

Osztályok:
    Pair
"""
from __future__ import annotations

class Pair:
    """p1, p2 számpárt tartalmazó osztály

    Összeadás, kivánás, szorzás, osztás, összehasonlítás
    művelet végezhető el az osztályon ami a számpárra lesz
    érvényes.

    Attributes:
        p1: Első szám
        p2: Második szám
    """
    def __init__(self, p1c: Pair | list[int | float] | int | float = 0, p2: int | float = 0):
        """Pair osztály belépési pont.
        
        Args:
            p1c: szám vagy minumum kételemű listaszerű objektum
                amennyiben lista csak az első két elem kerül felhasználásra,
                és a p2 számot nem vesszük figyelembe
            p2: szám"""
        if isinstance(p1c, (int, float)):
            p1 = p1c
            assert isinstance(p2, (int, float)), ("Várt szám vagy minimum "
                f"kételemű listaszerű elem, kapott: {type(p1c)}")
            p2 = p2
        elif isinstance(p1c, Pair):
            p1 = p1c.p1
            p2 = p1c.p2
        elif hasattr(p1c, "__getitem__") and len(p1c) >= 2:
            p1 = p1c[0]
            p2 = p1c[1]
        else:
            raise TypeError(f"Várt szám vagy minimum kételemű listaszerű elem, kapott: {type(p1c)}")
        self.p1 = p1
        self.p2 = p2

    def __get_pair(self, obj: Pair | list[int | float] | int | float):
        """Objektum vizsgálata
        
        Objektum vizsgálata, hogy az szám-e vagy listaszerű
        elem.
        
        """
        if isinstance(obj, (int, float)):
            return (obj, obj)
        elif isinstance(obj, Pair):
            return (obj.p1, obj.p2)
        elif hasattr(obj, "__getitem__"):
            assert len(obj) >= 2, ("A kapott lista nem kételemű!")
            return (obj[0], obj[1])

        raise TypeError(f"Várt szám vagy minimum kételemű listaszerű elem, kapott: {type(obj)}")

    def __add__(self, other):
        """Összeadás
        
        A számpárral összeadandó érték egy szám, egy másik számpár
        vagy egy minimum kételemű listaszerű objektum lehet.
        """
        pair = self.__get_pair(other)
        
        return Pair(self.p1 + pair[0], self.p2 + pair[1])

    def __sub__(self, other):
        """Kivonás

        A számpárból kivonandó érték egy szám, egy másik számpár
        vagy egy minimum kételemű listaszerű objektum lehet.
        """
        return self + other * -1

    def __mul__(self, other):
        """Szorzás

        A számpárt megszorzó érték egy szám, egy másik számpár
        vagy egy minimum kételemű listaszerű objektum lehet.
        """
        pair = self.__get_pair(other)

        return Pair(self.p1 * pair[0], self.p2 * pair[1])

    def __truediv__(self, other):
        """Osztás
        
        A számpárt elosztó érték egy szám, egy másik számpár
        vagy egy minimum kételemű listaszerű objektum lehet.
        Nulla nem lehet...
        """
        pair = self.__get_pair(other)
        if 0 in pair:
            raise ZeroDivisionError

        return self * (1/pair[0], 1/pair[1])

    def __iadd__(self, other):
        """Összead és beállít
        
        A számpárral összeadandó érték egy szám, egy másik számpár
        vagy egy minimum kételemű listaszerű objektum lehet.
        """
        pair = self.__get_pair(other)

        self.p1 += pair[0]
        self.p2 += pair[1]

        return self

    def __isub__(self, other):
        """Kivon és beállít

        A számpárból kivonandó érték egy szám, egy másik számpár
        vagy egy minimum kételemű listaszerű objektum lehet.
        """
        self += other * -1

        return self

    def __imul__(self, other):
        """Szoroz és beállít

        A számpárt megszorzó érték egy szám, egy másik számpár
        vagy egy minimum kételemű listaszerű objektum lehet.
        """
        pair = self.__get_pair(other)

        self.p1 *= pair[0]
        self.p2 *= pair[1]

        return self

    def __itruediv__(self, other):
        """Oszt és beállít
        
        A számpárt elosztó érték egy szám, egy másik számpár
        vagy egy minimum kételemű listaszerű objektum lehet.
        Nulla nem lehet...
        """
        pair = self.__get_pair(other)
        if 0 in pair:
            raise ZeroDivisionError

        self *= (1/pair[0], 1/pair[1])

        return self

    def __eq__(self, other):
        """Összehasonlítás
        
        Számpár összehasonlítása másik számpárral vagy minimum
        kételemű listaszerű objektummal vagy számmal.
        """
        pair = self.__get_pair(other)

        return self.p1 == pair[0] and self.p2 == pair[1]

    def __lt__(self, other):
        """Összehasonlítás
        
        Számpár összehasonlítása másik számpárral vagy minimum
        kételemű listaszerű objektummal vagy számmal.
        """
        pair = self.__get_pair(other)

        return self.p1 < pair[0] and self.p2 < pair[1]

    def __le__(self, other):
        """Összehasonlítás
        
        Számpár összehasonlítása másik számpárral vagy minimum
        kételemű listaszerű objektummal vagy számmal.
        """
        pair = self.__get_pair(other)

        return self.p1 <= pair[0] and self.p2 <= pair[1]

    def __gt__(self, other):
        """Összehasonlítás
        
        Számpár összehasonlítása másik számpárral vagy minimum
        kételemű listaszerű objektummal vagy számmal.
        """
        pair = self.__get_pair(other)

        return self.p1 > pair[0] and self.p2 > pair[1]

    def __ge__(self, other):
        """Összehasonlítás
        
        Számpár összehasonlítása másik számpárral vagy minimum
        kételemű listaszerű objektummal vagy számmal.
        """
        pair = self.__get_pair(other)

        return self.p1 >= pair[0] and self.p2 >= pair[1]

    def __abs__(self): #TODO: Test
        """Abszolut érték
        
        Számpár absolut értékként."""

        pabs = Pair(self)
        pabs.p1 = abs(pabs.p1)
        pabs.p2 = abs(pabs.p2)

        return pabs

    def __getitem__(self, key):
        """Érték visszaadása listaszerű lekérdezésnél
        
        Az érték intre konvertálva adódik vissza."""
        if key == 0:
            return int(self.p1)
        elif key == 1:
            return int(self.p2)

        raise KeyError

    def __setitem__(self, key, value):
        """Érték beállítása listaszerűen"""
        if key < 0 or key > 1:
            raise KeyError

        if key == 0:
            self.p1 = value
        elif key == 1:
            self.p2 = value

    def __len__(self):
        return 2

    def __repr__(self):
        return (f"Pair(p1,p2)({int(self.p1)}[{self.p1}], "
            f"{int(self.p2)}[{self.p2}])")