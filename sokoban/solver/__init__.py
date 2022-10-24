""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: __init__.py
Verzió: 1.0.0
--------------------
sokoban.solver

Sokoban megoldó csomag

Objektumok:
    SolverThread
"""

from __future__ import annotations

from threading import Thread
from subprocess import Popen, PIPE, STARTUPINFO, STARTF_USESHOWWINDOW

from sokoban import config
from . import festival
from . import solver
from .win_key_press import write_key_to_console

from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from sokoban import Space

class SolverThread(Thread):
    """SolverThread A sokoban megoldó futtatását elvégző osztály ami mindig külön szálon fut.
    
    Class arguments:
        explored_states (set): már megoldott állások listája
        
    Arguments:
        space (Space): pályaadatokat tartalmazó osztály
        callback (Callable): a megoldás megtalálásakor meghívandó metódus
        solved (bool): a megoldás meg van-e találva
        timeout (int): a megoldás keresésének maximális ideje
        timeout_handler (Callable): időtúllépést lekezelő metódus"""
    explored_states = set()

    def __init__(self, space: Space, callback: Callable, timeout = 30, timeout_handler: Callable = None):
        """SolverThread

        Args:
            space (Space): pályaadatokat tartalmazó osztály
            callback (Callable): a megoldás megtalálásakor meghívandó metódus
            timeout (int, optional): a megoldás keresésének maximális ideje. Defaults to 30.
            timeout_handler (Callable, optional): időtúllépést lekezelő metódus. Defaults to None.
        """
        Thread.__init__(self)

        self.space = space
        self.callback = callback
        self.solved = False
        self.timeout = timeout
        self.timeout_handler = timeout_handler

    def reset_states(self):
        """reset_states Megoldott pályáállások törlése
        """
        SolverThread.explored_states = set()

    def checkState(self, state: tuple) -> bool:
        """checkState állás keresése a megoldottak között

        Args:
            state (tuple): vizsgált állás

        Returns:
            bool: az állás benne van-e a megoldott állásokban
        """
        for tmp_state in SolverThread.explored_states:
            if state[0] in tmp_state[1] and sorted(state[1]) == sorted(tmp_state[2]):
                return tmp_state

        return False

    def getSolution(self, space: Space) -> str | None:
        """getSolution Megoldás lekérése

        Args:
            space (Space): Játéktér objektum

        Returns:
            str | None: a megoldás karakterlánca
        """
        if len(SolverThread.explored_states) == 0:
            return None

        layout = festival.space_to_level_str(space)
        state = solver.getState(layout, True if len(SolverThread.explored_states) == 0 else False)

        explored_state = self.checkState(state)
        if explored_state is not False:
            return solver.getSolutionFromExist(state[0], state[1], explored_state)

        return None

    def run(self):
        """run
        """

        layout = festival.space_to_level_str(self.space)
        state = solver.getState(layout, True if len(SolverThread.explored_states) == 0 else False)

        if state is None:
            self.callback(None)
            return

        explored_state = self.checkState(state)
        if explored_state is not False:
            self.callback(solver.getSolutionFromExist(state[0], state[1], explored_state))
            # print("SOLVED")
            return

        festival.clear()

        festival.save_level(layout)

        startupinfo = STARTUPINFO()
        startupinfo.dwFlags |= STARTF_USESHOWWINDOW

        proc = Popen(f"{config.FESTIVAL_EXECUTABLE} {config.FESTIVAL_PATH}tmp.sok -out_dir {config.FESTIVAL_PATH}",
            stdout=PIPE, stderr=PIPE, text=True, startupinfo=startupinfo)

        #write_key_to_console()

        run_time = 0
        res = None
        while True:
            try:
                res = proc.communicate(None, 0.5)
                break
            except:
                None

            if run_time >= self.timeout:
                proc.terminate()
                break
            run_time += 0.5

        solution = None
        if res is not None:
            if res[0][-8:-1] == "SOLVED!":
                solution = festival.get_solution()
                SolverThread.explored_states.update(solver.getSolvedStates(state[0], state[1], solution))
                self.solved = True
        else:
            if callable(self.timeout_handler):
                self.timeout_handler(self.timeout)

        festival.clear()

        self.callback(solution)