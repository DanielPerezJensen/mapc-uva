from .helpers import Agent
from .helpers import BDIAgent
from collections import defaultdict
import numpy as np


class Builder(Agent, BDIAgent):
    def __init__(self, user, pw, print_json=False):
        Agent.__init__(self, user, pw, print_json)
        BDIAgent.__init__(self)

    def get_intention(self):
        if not hasattr(self, 'ready'):
            self.debug()

        if len(self.beliefs.tasks):
            # TODO: do actual task selection
            task = self.select_task()
            return self.do_task(task)

        return tuple()

    def debug(self):
        self.beliefs.things['dispensers']['b0'] = [(5, -4)]
        self.beliefs.things['dispensers']['b1'] = [(6, 9)]
        self.beliefs.things['taskboards'].append((4, 11))
        self.beliefs.things['goals'].append((-7, 2))
        self.ready = True

    def select_task(self):
        """
        Selects a task from the active tasks and returns it.
        """
        return self.beliefs.tasks[0]

    def do_task(self, task):
        """
        Returns the intentions to complete a given task.

        Arguments
        ----------
        task: dict
            The selected task.
        """
        # TODO: Find the most efficient path going past
        # the taskboard and dispensers to the goal.

        # Get the required blocks from the task.
        required = self._required_blocks(task)

        # Check if it is known where taskboards,
        # required dispensers and goal nodes are.
        for thing, options in self.beliefs.things.items():
            if thing == 'dispensers':
                for block_type in required:
                    if block_type not in options:
                        return tuple()
            elif not options:
                return tuple()

        # Create and return the new intentions
        intentions = [self.get_task, self.get_blocks, self.submit_task]
        args = [(task['name'],), (required,), (task['name'], required)]
        contexts = [tuple(), tuple(), tuple()]
        descriptions = ["getTask", "getBlocks", "submitTask"]
        primitives = [False, False, False]

        return intentions, args, contexts, descriptions, primitives

    def get_task(self, task_name):
        """
        Return intentions to navigate to the nearest
        taskboard and accept the given task.
        """
        # Find the nearest taskboard.
        taskboard = self._get_nearest_taskboard()
        if not taskboard:
            return tuple()

        # Return new intentions.
        return ([self.nav_to, self.accept],
                [(taskboard, self._user_id, True), (task_name,)],
                [tuple(), tuple()],
                ["navToTask", "acceptTask"],
                [True, True])

    def get_blocks(self, required):
        """
        Return intentions to navigate to the nearest
        required dispensers and request required blocks.
        """
        intentions, args, contexts, \
            descriptions, primitives = [], [], [], [], []
        for block_type, required_blocks in required.items():
            # Find the nearest dispensers.
            dispenser = self._get_nearest_dispenser(block_type)

            if not dispenser:
                return tuple()

            n_blocks = len(required_blocks)
            # Add navigation to dispenser and
            # retrieval of blocks to intentions.
            intentions += [self.nav_to] + \
                [self.orient_and_request] * n_blocks
            args += [(dispenser, self._user_id, True)] + \
                    [(dispenser,)] * n_blocks
            contexts += [tuple()] + [tuple()] * n_blocks
            descriptions += ["navToDispenser"] + \
                ["OrientRequestBlock"] * n_blocks
            primitives += [True] + [False] * n_blocks

        return intentions, args, contexts, descriptions, primitives

    def submit_task(self, task_name, pattern):
        """
        Return intentions to navigate to the nearest goal state
        and submit the attached blocks.
        """
        goal = self._get_nearest_goal()
        if not goal:
            return tuple()

        return (
            [self.nav_to, self.turn_and_submit],
            [(goal, self._user_id), (task_name, pattern,)],
            [tuple(), tuple()],
            ["navToGoal", "turnAndSubmit"],
            [True, False]
            )

    def turn_and_submit(self, task_name, pattern):
        """
        Turn the agent to have the correct orientation and submit the task.
        """
        # TODO: make it work for more than one attached block

        turns = self._required_turns(self.beliefs.attached[0],
                                     list(pattern.values())[0][0])
        n_turns = len(turns)
        return (
            [self.rotate] * n_turns + [self.submit],
            turns + [(task_name,)],
            [tuple()] * n_turns + [tuple()],
            ["rotate"] * n_turns + ["submitTask"],
            [True, True]
            )

    def orient_and_request(self, dispenser):
        """
        Find the direction of the adjacent
        dispenser and return a block request.
        """
        # TODO: turn the agent if there's already
        # a block attached on the side of the dispenser.
        direction = self.beliefs.get_direction(self._user_id, dispenser)

        return ([self.request, self.attach], [(direction,), (direction,)],
                [tuple(), tuple()], ["requestBlock", "attachBlock"],
                [True, True])

    # HELPER FUNCTIONS #

    @staticmethod
    def _required_turns(rel_from, rel_to):
        """
        Return the directions of the required turns for completing the task.

        Parameters
        -----------
        rel_from: tuple
            The relative location the agent wants to turn from.
        rel_to: tuple
            The relative location the agent wants the rel_from to turn to.
        """

        if rel_from == rel_to:
            # No rotation needed.
            return []
        elif abs(rel_from[0] - rel_to[0]) == 2 or \
                abs(rel_from[1] - rel_to[1]) == 2:
            # Block is on opposite side, rotate twice.
            return [('cw',), ('cw',)]
        elif rel_from[0] == 0:
            if sum(np.array(rel_from) +
                   np.array(rel_to[::-1])):
                return [('ccw',)]
            else:
                return [('cw',)]
        else:
            if sum(np.array(rel_from) +
                   np.array(rel_to[::-1])):
                return [('cw',)]
            else:
                return [('ccw')]

    @staticmethod
    def _required_blocks(task):
        required = defaultdict(list)
        for requirement in task['requirements']:
            required[requirement['type']].append(
                (requirement['x'], requirement['y']))
        return required

    def _get_nearest_dispenser(self, block_type):
        """
        Returns the nearest dispenser (using manhattan distance)
        or None if there is no known dispenser of the given type.

        Arguments
        ---------
        block_type: str
            The type of blocks the dispenser dispenses, e.g. 'b0'.
        """
        if block_type in self.beliefs.things['dispensers'] and \
                self.beliefs.things['dispensers'][block_type]:
            return min(self.beliefs.things['dispensers'][block_type],
                       key=lambda x: self._manhattan_distance(x,
                       self.beliefs.get_current(self._user_id).location))
        return None

    def _get_nearest_taskboard(self):
        """
        Returns the nearest taskboard (using manhattan distance)
        or None if there is no known taskboard.
        """

        if self.beliefs.things['taskboards']:
            return min(self.beliefs.things['taskboards'],
                       key=lambda x: self._manhattan_distance(x,
                       self.beliefs.get_current(self._user_id).location))
        return None

    def _get_nearest_goal(self):
        """
        Returns the nearest taskboard (using manhattan distance)
        or None if there is no known taskboard.
        """

        if self.beliefs.things['goals']:
            return min(self.beliefs.things['goals'],
                       key=lambda x: self._manhattan_distance(x,
                       self.beliefs.get_current(self._user_id).location))
        return None

    @staticmethod
    def _manhattan_distance(coords1, coords2):
        return sum(abs(np.array(coords1, dtype=int) -
                       np.array(coords2, dtype=int)))


if __name__ == "__main__":
    a_list = []
    for i in range(1, 2):
        a_list.append(Builder(f"agentA{i}", "1"))
        a_list[-1].start()
