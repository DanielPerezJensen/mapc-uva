from .helpers import Agent
from .helpers import BDIAgent
from collections import defaultdict
import numpy as np


class Builder(Agent, BDIAgent):
    def __init__(self, user, pw, print_json=False):
        Agent.__init__(self, user, pw, print_json)
        BDIAgent.__init__(self)

    def get_intention(self):
        # if not hasattr(self, 'ready'):
        #     self.debug()
        
        intentions, args, contexts, \
            descriptions, primitives = [], [], [], [], []

        for var in self.drain_output_queue():
            if var[0] == 'mergedBeliefs':
                continue
            intentions += (list(map(eval, var[0])))
            args += var[1]
            contexts += var[2]
            descriptions += var[3]
            primitives += var[4]

        # if len(self.beliefs.tasks):
        #     # TODO: do actual task selection
        #     task = self.select_task()
        #     return self.do_task(task)

        if intentions:
            return (intentions, args, contexts, descriptions, primitives)
        return tuple()

    def debug(self):
        if self._user_id == 1:
            self.beliefs.things['goals'].append((2, -6))
            self.beliefs.things['taskboards'].append((2, 3))
            self.beliefs.things['dispensers']['b0'] = [(-7, -1)]
        if self._user_id == 2:
            self.beliefs.things['goals'].append((-2, -6))
            self.beliefs.things['taskboards'].append((-2, 3))
            self.beliefs.things['dispensers']['b0'] = [(-11, -1)]
        self.ready = True

    def select_task(self):
        """
        Selects a task from the active tasks and returns it.
        """
        return self.beliefs.tasks[0]

    def do_task(self, task, with_agents=[]):
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
        args = [(task['name'],), required, (task['name'], required)]
        contexts = [tuple(), tuple(), tuple()]
        descriptions = ["getTask", "getBlocks", "submitTask"]
        primitives = [False, False, False]

        return (intentions, args, contexts, descriptions, primitives)

    def get_task(self, task_name, comm_queue=None):
        """
        Return intentions to navigate to the nearest
        taskboard and accept the given task.

        Arguments
        ----------
        task_name: str
            The name of the task that needs to be accepted.
        comm_queue: object
            A queue object in which to communicate the goal location of
            the agent.
        """
        # Find the nearest taskboard.
        taskboard = self._get_nearest_taskboard()
        if not taskboard:
            return tuple()

        if self.beliefs.things['goals']:
            self.goal = min(self.beliefs.things['goals'],
                            key=lambda x:
                            self._manhattan_distance(x, task_board))
        else:
            self.goal = None

        if comm_queue:
            comm_queue.put(('goal_loc', goal))

        # Return new intentions.
        return ([self.nav_to, self.accept],
                [(taskboard, self._user_id, True), (task_name,)],
                [tuple(), tuple()],
                ["navToTask", "acceptTask"],
                [True, True])

    def pos_at_goal(self, comm_queue):
        if not self.goal:
            if self.beliefs.things['goals']:
                self.goal = min(self.beliefs.things['goals'],
                                key=lambda x:
                                self._manhattan_distance(x,
                                self.beliefs.get_current(self._user_id)))
                if comm_queue:
                    comm_queue.put(('goal_loc', self.goal))
            else:
                return tuple()

        return (
            [self.nav_to, self.broadcast_msg],
            [(self.goal, self._user_id), (comm_queue, ('0 ready',))],
            [tuple(), tuple()],
            ["navToGoal", "communicateAtGoal"],
            [True, False]
            )

    def broadcast_msg(self, comm_queue, msg):
        """
        Broadcast a given message to the given communication queue. 
        """
        comm_queue.put(msg)
        return [self.skip], [tuple()], [tuple()], ["communicateAtGoal"], [True]

    def get_block(self, block_type):
        dispenser = self._get_nearest_dispenser(block_type)

        if dispenser:
            intentions = [self.nav_to, self.orient_and_request]
            args = [(dispenser, self._user_id, True), (dispenser,)]
            contexts = [tuple(), tuple()]
            descriptions = ["navToDispenser", "orientRequestBlock"]
            primitives = [True, False]
        else:
            return tuple()

        return intentions, args, contexts, descriptions, primitives

    def get_blocks(self, required):
        """
        Return intentions to navigate to the nearest
        required dispensers and request required blocks.

        Arguments
        ----------
        required: dict
            A dictionary block_type as keys and the list of
            relative locations where the blocks have to be attached.
        """
        intentions, args, contexts, \
            descriptions, primitives = [], [], [], [], []

        sorted_required = sorted(required.items(), key=lambda x: min(x[1],
                                 key=lambda x: self._manhattan_distance(
                                 (0, 0), x)))

        for block_type, required_blocks in sorted_required:
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
                ["orientRequestBlock"] * n_blocks
            primitives += [True] + [False] * n_blocks

        return intentions, args, contexts, descriptions, primitives

    def connect_to_agent(self, comm_queue, rel_attach_locs):
        """
        Connect the attached blocks to the given attached coordinates.
        """
        attach_locs = sorted([(self.goal[0] + loc[0], self.goal[1] + loc[1])
                             for loc in rel_attach_locs], key=lambda x:
                             self._manhattan_distance(x, self.goal))

        rel_surr_nodes = [(0, 1), (1, 0), (0, -1),  (-1, 0)]

        intentions, args, contexts, descriptions, primitives = ([], [], [],
                                                                [], [])

        curr_loc = self.beliefs.get_current(self._user_id)

        for attach_loc in attach_locs:
            nav_loc = attach_loc

            for rel_surr in rel_surr_nodes:
                surr_node = (attach_loc[0] + rel_surr[0],
                             attach_loc[1] + rel_surr[1])
                if surr_node in self.beliefs.nodes and \
                        self.beliefs.nodes[surr_node]._is_things(
                        self.beliefs.step):
                    nav_loc[0] -= rel_surr[0]
                    nav_loc[1] -= rel_surr[1]
            intentions += [self.nav_to, self.turn_and_connect]
            args += [(nav_loc, self._user_id), 
                     (nav_loc[0] - curr_loc[0], nav_loc[1] - curr_loc[1])]
            contexts += [tuple()]
            descriptions += ["navToAttachLocation"]
            primitives += [True]

        return intentions, args, contexts, descriptions, primitives

    def turn_and_connect(self, rel_attach_loc):
        intentions, args, contexts, descriptions, primitives = ([], [], [],
                                                                [], [])
        # compute turns
        rel_from = min(self.beliefs.attached[self._user_id], key=lambda x:
                       self._manhattan_distance(x, rel_attach_loc))
        rel_to = min([(1, 0), (0, 1), (-1, 0), (0, -1)], key=lambda x:
                     self._manhattan_distance(x, rel_attach_loc))
        turns = self._required_turns(rel_from, rel_to)

        # compute moves
        moves = self._required_moves(rel_to, rel_attach_loc)

        for new_args, func, desc in \
                [(turns, self.rotate, "turningBlockToAttachLoc"), 
                 (moves, self.move, "movingToAttachLoc")]:
            n_args = len(args)
            args += new_args
            intentions += n_args * [func]
            contexts += n_args * [tuple()]
            descriptions += n_args * [desc]
            primitives += n_args * [True]

        return intentions, args, contexts, descriptions, primitives

    def prepare_build(self, comm_queue, queue_index, attach_locs):
        local_queue = []
        msg = comm_queue.get(timeout=3)

        while msg and msg[0] != 'goal_loc':
            local_queue.append(msg)
            msg = comm_queue.get(timeout=3)

        for return_msg in local_queue:
            comm_queue.put(return_msg)

        if not msg:
            return ([self.skip, self.prepare_build],
                    [tuple(), (comm_queue, queue_index, attach_locs)],
                    [tuple(), tuple()],
                    ["waitForGoalMsg", "prepareForBuild"],
                    [True, False])

        local_queue.put(msg)

        rel_prep_loc = [(-4, -4), (4, -4), (-4, 4), (4, 4)][queue_index]

        prep_loc = msg[1][0] + rel_prep_loc[0], msg[1][1] + rel_prep_loc[1]

        self.goal = msg[1]

        return ([self.nav_to, self.wait_for_turn],
                [(prep_loc, self._user_id),
                 (comm_queue, queue_index, attach_locs)],
                [tuple(), tuple()],
                ["navToGoal", "waitForTurn"],
                [True, False])

    def wait_for_turn(self, comm_queue, turn, attach_locs):
        """
        Wait until ready for building.
        """
        local_queue = []
        msg = comm_queue.get(timeout=3)

        while msg and not msg[0][0] == str(turn):
            local_queue.append(msg)
            msg = comm_queue.get(timeout=3)

        for return_msg in local_queue:
            comm_queue.put(return_msg)

        if not msg:
            return ([self.skip, self.wait_for_turn],
                    [tuple(), (comm_queue, turn, attach_locs)],
                    [tuple(), tuple()],
                    ["skipThisStep", "waitForTurn"],
                    [True, False])

        return ([self.connect_to_agent], [(comm_queue, rel_attach_locs,)],
                [tuple()], ["connectBlocksToAgent"], [False])

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

        turns = self._required_turns(self.beliefs.attached[self._user_id][0],
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

        current_loc = self.beliefs.get_current(self._user_id).location
        for rel_location in self.beliefs.attached[self._user_id]:
            if (rel_location[0] + current_loc[0],
                    rel_location[1] + current_loc[1]) == dispenser:
                return ([self.rotate_to_free_spot, self.request, self.attach],
                        [(rel_location,), (direction,), (direction,)],
                        [tuple(), tuple(), tuple()],
                        ["findFreeSpot", "requestBlock", "attachBlock"],
                        [False, True, True])

        return ([self.request, self.attach], [(direction,), (direction,)],
                [tuple(), tuple()], ["requestBlock", "attachBlock"],
                [True, True])

    def rotate_to_free_spot(self, rel_location):
        """
        Rotate the agent to have a free spot at the given location.

        arguments
        ---------
        rel_location: tuple
            The relative location to rotate the free spot to.
        """
        free_spot_turns = [self._required_turns(rel_location, x) for x
                           in [(0, -1), (1, 0), (0, 1), (-1, 0)] if x
                           not in self.beliefs.attached[self._user_id]]
        args = min(free_spot_turns, key=lambda x: len(x))
        n_turns = len(args)

        return (n_turns * [self.rotate], args, n_turns * [tuple()],
                n_turns * ["rotateToFreeSpot"], n_turns * [True])

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
                return [('ccw',)]

    @staticmethod
    def _required_blocks(task):
        required = defaultdict(list)
        for requirement in task['requirements']:
            required[requirement['type']].append(
                (requirement['x'], requirement['y']))
        return required

    @staticmethod
    def _required_moves(from_loc, to_loc):
        to_loc[0] -= from_loc[0]
        to_loc[1] -= from_loc[1]

        result = []
        if to_loc[0] > 0:
            result += to_loc[0] * [('e',)]
        elif to_loc[0] < 0:
            result += to_loc[0] * [('w',)]
        
        if to_loc[1] > 0:
            result += to_loc[1] * [('s',)]
        elif to_loc[1] < 0:
            result += to_loc[1] * [('n',)]
        
        return result

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
