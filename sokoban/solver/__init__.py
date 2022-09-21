from __future__ import annotations
import sys

from threading import Thread
import os
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
import signal
from time import sleep
import psutil

from sokoban import config
from . import festival
from . import solver

from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from sokoban import Space

class SolverThread(Thread):
    explored_states = set()

    def __init__(self, space: Space, callback: Callable):
        Thread.__init__(self)

        self.space = space
        self.callback = callback
        self.solved = False

    def reset_states(self):
        SolverThread.explored_states = set()

    def checkState(self, state):
        for tmp_state in SolverThread.explored_states:
            if state[0] in tmp_state[1] and sorted(state[1]) == sorted(tmp_state[2]):
                return tmp_state

        return False

    def getSolution(self, space):
        if len(SolverThread.explored_states) == 0:
            return None

        layout = festival.space_to_level_str(space)
        state = solver.getState(layout, True if len(SolverThread.explored_states) == 0 else False)

        explored_state = self.checkState(state)
        if explored_state is not False:
            return solver.getSolutionFromExist(state[0], state[1], explored_state)

        return None

    def run(self):
        layout = festival.space_to_level_str(self.space)
        state = solver.getState(layout, True if len(SolverThread.explored_states) == 0 else False)

        if state is None:
            self.callback(None)
            return

        explored_state = self.checkState(state)
        if explored_state is not False:
            self.callback(solver.getSolutionFromExist(state[0], state[1], explored_state))
            print("SOLVED")
            return

        festival.clear()

        festival.save_level(layout)

        proc = Popen(f"{config.FESTIVAL_EXECUTABLE} {config.FESTIVAL_PATH}tmp.sok -out_dir {config.FESTIVAL_PATH}", stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)

        solution = None
        
        try:
            proc.communicate('.', 5)
            solution = festival.get_solution()
            SolverThread.explored_states.update(solver.getSolvedStates(state[0], state[1], solution))
            self.solved = True
        except TimeoutExpired:
            proc.terminate()


        festival.clear()

        self.callback(solution)