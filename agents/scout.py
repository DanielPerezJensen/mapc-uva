from .helpers import Agent
from .helpers.agent import DStarLite

import random
from math import floor, ceil, exp
from collections import defaultdict
from operator import itemgetter
import sys


class Scout(Agent):
    def get_intention(self):
        """
        Gets intentions of this type of agent.
        """
        if not hasattr(self, 'local_random'):
            self.local_random = random.Random()
            self.local_random.seed(self.local_random.
                                   choice(range(sys.maxsize)) *
                                   int(self._user[6:]*1024))

        selected_action = ([self.exploration],
                           [()],
                           [tuple()],
                           ['exploreRandomly'],
                           [False])

        return selected_action

    def exploration(self):
        if not hasattr(self, 'exploration_compeleted'):
            self.exploration_complete = False
        mode = 'tghm'

        if mode == 'tghm':
            current = self.get_location()
            if not hasattr(self, 'topology'):
                self.topology = [current]
                self.candidate_target_points = set()
                self.candidate_topology_points = set()
                self.t = 1

            while self.candidate_topology_points or self.t == 1:
                return ([self.tghm_move],
                        [(0.5, 5)],
                        [tuple()],
                        ['chooseNextTargetPoint'],
                        [False])

            return ([self.skip],
                    [()],
                    [tuple()],
                    ['explorationCompleted'],
                    [True])

        else:
            while not self.exploration_complete:
                height, width = self.beliefs.height, self.beliefs.width
                if height and width and height * width == len(self.beliefs.nodes):
                    self.exploration_complete = True

                return ([self.random_move],
                        [()],
                        [tuple()],
                        ['chooseRandomGoal'],
                        [False])
        
            return ([self.skip],
                    [()],
                    [tuple()],
                    ['explorationCompleted'],
                    [True])

    def tghm_exploration(self, lambd, N_0):
        current = self.get_location()
        if not hasattr(self, 'topology'):
            self.topology = [current]
            self.candidate_target_points = set()
            self.candidate_topology_points = {current}
            self.t = 1

        while self.candidate_topology_points:
            return ([self.tghm_move],
                    [(lambd, N_0)],
                    [tuple()],
                    ['chooseNextTargetPoint'],
                    [False])

        return ([self.skip], [()], [tuple()], ['explorationCompleted'], [True])

    def tghm_move(self, lambd, N_0):
        """
        Practically does the same as tghm_move() only it simplifies the
        process. This is because the actual paper adds a lot of things we don't
        need as we already have our own graph in a simplified world.

        Arguments
        ---------
        lambd: float
            A parameter used to weigh motion cost against excpeted
            information gain. A small lambd means it prioritizes
            information gain over motion cost.
        N_0: int
            When selecting the next target point, the information gain
            (amount of nodes it hasn't discovered yet) must be higher than
            N_0.
        """
        current = self.get_location()
        if not hasattr(self, 'topology'):
            self.topology = [current]
            self.candidate_target_points = set()
            self.candidate_topology_points = set()
            self.t = 1

        self.candidate_target_points = \
            self.generate_candidate_target_points(current)

        if self.candidate_target_points:
            potential_points = self.candidate_target_points.\
                union(set([location for location, V in
                           self.candidate_topology_points]))

            self.candidate_topology_points.clear()

        for candidate in list(potential_points):
            if self.calculate_unknown_N(candidate) > N_0:
                V = self.utility_V(current, candidate, lambd)
                self.candidate_topology_points.add((candidate, V))
        if self.candidate_topology_points:
            max_V = max(self.candidate_topology_points, key=itemgetter(1))[1]
            highest_points = [location for location, V in
                              self.candidate_topology_points if V == max_V]
            next_target_point = self.local_random.choice(highest_points)
            print(f'Next target point: {next_target_point}')
            self.topology.append(next_target_point)
            self.t += 1

            return ([self.nav_to],
                    [(next_target_point, self._user_id)],
                    [tuple()],
                    ['moveToNextTargetPoint'],
                    [True])
        else:
            print('!!! Done exploring !!!')
            self.exploration_complete = True
            return ([self.skip],
                    [()],
                    [tuple()],
                    ['explorationCompleted'],
                    [True])

    def calculate_unknown_N(self, location):
        """
        Return the number of unknown function in a local vision.
        """
        local_nodes = self.beliefs.get_local_node_locations(self._user_id,
                                                            offset=location)
        unknown_nodes = [node for node in local_nodes if node not in
                         self.beliefs.nodes.keys()]
        return len(unknown_nodes)

    def utility_V(self, current, target_point, lambd):
        """
        The utility function that determines the exploration value if a node
        based on the distance and potential information gain.
        """
        x, y = target_point
        cx, cy = current

        distance = abs(x - cx) + abs(y - cy)

        return self.calculate_unknown_N(target_point) * exp(-lambd*distance)

    def generate_candidate_target_points(self, current):
        """
        Determine the cells that are being crossed if a straight line is
        drawn between the agent's current location and the given location.

        Arguments
        ---------
        parent: tuple(int, int)
            The current location of the agent. This is the parent node to
            all the candidate target points that will be generated.
        """
        candidate_target_points = set()
        cx, cy = current

        motion_points = [(5, 0), (0, 5), (-5, 0), (0, -5)]

        for x, y in self.beliefs.get_local_node_locations(self._user_id,
                                                          offset=(0, 0)):
            if abs(x) + abs(y) == 5:
                x, y = self.beliefs.modulate((x + cx, y + cy))
                if self.beliefs.nodes[(x, y)].get_terrain()[0] != 'obstacle':
                    # Frontier Type I
                    candidate_target_points.add((x, y))
                else:
                    # Frontier Type II
                    crossed_cells = []
                    if x > cx:
                        if x-cx == 0:
                            a = 0
                        else:
                            a = (y-cy)/(x-cx)
                        b = y - a*x
                        range_x = range(cx+1, x)
                    else:
                        if x-cx == 0:
                            a = 0
                        else:
                            a = (cy-y)/(cx-x)
                        b = y - a*x
                        range_x = range(x+1, cx)

                    for i in range_x:
                        j = a*i + b
                        if j == y:
                            crossed_cells.append((i, round(j)))
                        elif j == int(j):
                            crossed_cells.append((i, int(j+1)))
                            crossed_cells.append((i, int(j)))
                            crossed_cells.append((i, int(j-1)))
                        else:
                            crossed_cells.append((i, floor(j)))
                            crossed_cells.append((i, ceil(j)))

                    crossed_empty_cells = [cell for cell in crossed_cells if
                                           self.beliefs.nodes[cell].
                                           get_terrain()[0] != 'obstacle']

                    crossed_empty_cells.sort(key=lambda c:
                                             abs(x-c[0]) + abs(y-c[1]))

                    if crossed_empty_cells:
                        candidate_target_points.add(crossed_empty_cells[0])

        return candidate_target_points

    def random_move(self, r_range=range(5, 50)):
        """
        Set a random goal for the agent to move towards (within a
        certain range).

        Arguments
        ---------
        r_range: list
            The range in which the x and y coordinates will be chosen.
        """
        cx, cy = self.get_location()
        r_range = list(r_range) + [-x for x in list(r_range)]
        goal = (self.local_random.choice(r_range) + cx,
                self.local_random.choice(r_range) + cy)
        goal = self.beliefs.modulate(goal)
        print(f'Goal: {goal}')
        return ([self.nav_to],
                [(goal, self._user_id)],
                [tuple()],
                ['moveRandom'],
                [True])

    def zigzag_exploration(self):
        """
        Explore by moving in a zigzag pattern. Exploration is
        finished when 100% of the nodes in the map are covered.

        Arguments
        ---------
        path_length: int
            The number of steps the agent walks vertically before moving
            11 steps horizontally (because the local vision reaches 5 cells).
        """
        while not self.exploration_complete:
            height, width = self.beliefs.height, self.beliefs.width
            if height and width and height * width == len(self.beliefs.nodes):
                self.exploration_complete = True

            return ([self.zigzag_move], [()], [tuple()],
                    ['performZigzagAction'], [False])

        return ([self.skip], [()], [tuple()], ['explorationCompleted'], [True])

    def zigzag_direction(self, direction, dimension, path_length):
        """
        Return correct nav_to intention based on direction and dimension
        in which the agent will move.
        """
        location = self.get_location()
        if dimension == 'height':
            if direction == 'north':
                goal = (location[0], location[1] - 11)
                descriptions = 'moveNorth'
            elif direction == 'east':
                goal = (location[0] + path_length, location[1])
                descriptions = 'moveEast'
            elif direction == 'south':
                goal = (location[0], location[1] + 11)
                descriptions = 'moveSouth'
            elif direction == 'west':
                goal = (location[0] - path_length, location[1])
                descriptions = 'moveWest'

        elif dimension == 'width':
            if direction == 'north':
                goal = (location[0], location[1] - path_length)
                descriptions = 'moveNorth'
            elif direction == 'east':
                goal = (location[0] + 11, location[1])
                descriptions = 'moveEast'
            elif direction == 'south':
                goal = (location[0], location[1] + path_length)
                descriptions = 'moveSouth'
            elif direction == 'west':
                goal = (location[0] - 11, location[1])
                descriptions = 'moveWest'

        return ([self.nav_to],
                [(goal, self._user_id)],
                [tuple()],
                [descriptions],
                [True])

    def zigzag_move(self, path_length=20, direction='east'):
        """
        Move is a zigzag pattern to explore the environment most efficiently.

        Arguments
        ---------
        path_length: int
            The number of steps the agent walks vertically before moving
            11 steps horizontally (because the local vision reaches 5 cells).
        direction: str
            A direction perpendicular to the path,
            which is defined by path length.
        """
        direction = self.local_random.choice(['north', 'east',
                                              'south', 'west'])
        intentions = [self.zigzag_direction, self.zigzag_direction,
                      self.zigzag_direction, self.zigzag_direction]
        contexts = [tuple(), tuple(), tuple(), tuple()]
        primitives = [False, False, False, False]

        if direction in ['east', 'west']:
            args = [('south', 'width', path_length),
                    (direction, 'width', path_length),
                    ('north', 'width', path_length),
                    (direction, 'width', path_length)]
            descriptions = ['moveSouth', f'move{direction.capitalize()}',
                            'moveNorth', f'move{direction.capitalize()}']

        elif direction in ['north', 'south']:
            args = [('east', 'height', path_length),
                    (direction, 'height', path_length),
                    ('west', 'height', path_length),
                    (direction, 'height', path_length)]
            descriptions = ['moveEast', f'move{direction.capitalize()}',
                            'moveWest', f'move{direction.capitalize()}']

        return intentions, args, contexts, descriptions, primitives
