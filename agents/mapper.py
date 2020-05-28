from .helpers import Agent
import random


class Mapper(Agent):
    def __init__(self, user, pw, print_json=False):
        Agent.__init__(self, user, pw, print_json)

    def get_intention(self):
        """
        Gets intentions of this type of agent.
        """

        # TODO: Actual action selection
        selected_action = self.zigzag_move()

        return selected_action

    def random_move(self, r_range=range(5, 15)):
        """
        Set a random goal for the agent to move towards (within a
        certain range).

        Arguments
        ---------
        r_range: list
            The range in which the x and y coordinates will be chosen.
        """
        r_range = list(r_range) + [-x for x in list(r_range)]
        goal = (random.choice(r_range), random.choice(r_range))

        return ([self.nav_to],
                [(goal, self._user_id)],
                [tuple()],
                ['moveRandom'],
                [True])

    def zigzag_direction(self, direction, dimension, path_length):
        """
        Return correct nav_to intention based on direction and dimension
        in which the agent will move.
        """
        location = self.beliefs.get_current(self._user_id).location
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

    def zigzag_move(self, path_length=5, direction='east'):
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
        direction = random.choice(['east', 'west'])
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

    def tghm_move(self):
        """
        This is part of my actual thesis.
        """
        pass
