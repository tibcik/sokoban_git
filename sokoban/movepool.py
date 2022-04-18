"""Játékhoz szükséges MovePool osztály modulja"""
import log.log
logger = log.log.init("MovePool")

from .objects import Box, Player
from utils import Pair

class MovePool:
    """Mozgások elmentését és a visszalépésért felelős osztály

    Attributes:
        player(sokoban.objects.Player): a játékos karaktere
        pool(list): a mozgás adatai tartalmazó lista
        current_move(int): a jelenlegi mozgások száma(visszalépések nélkül)
        sum_moves(int): az összes mozgások száma(visszalépésekkel)
    """
    def __init__(self, player : Player):
        """belépési pont
        
        Args:
            player: a játékos karaktere"""
        self.player = player

        self.pool = []
        self.current_move = 0
        self.sum_moves = 0

    def add(self, item):
        """Mozgás hozzáadása a listához
        
        Ha az argumentum egy Box objektum akkor az előző lépéshez adjuk hozzá
        mint kiegészítő információ
        
        Args:
            item(Pair|Box): ha Pair objektum akkor a karakter mozgását rögzítjük,
                ha Box objektum akkor az előző mozgáshoz hozzáadjuk a dobozt is"""
        if isinstance(item, Pair):
            if len(self.pool) != self.current_move:
                self.pool = self.pool[0:self.current_move]
            self.pool.append((item, None))
            self.current_move += 1
        elif isinstance(item, Box):
            self.pool[self.current_move - 1] = (self.pool[self.current_move - 1][0], item)

        self.sum_moves += 1

    def back(self):
        """Visszalépés"""
        ret = {'player_pos': None, 'box_pos': None, 'move': None}

        if self.current_move == 0:
            return None
        self.current_move -= 1
        bmove = self.pool[self.current_move][0] * -1
        ret['move'] = bmove
        ret['player_pos'] = Pair(self.player.pos)
        self.player.move(bmove)
        if self.pool[self.current_move][1] is not None:
            ret['box_pos'] = Pair(self.pool[self.current_move][1].pos)
            self.pool[self.current_move][1].move(bmove)

        self.sum_moves -= 1

        return ret