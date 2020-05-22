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

    def single_agent_zig_zag(self, agent_id, path_length=15):
        """
        Use a zig-zag pattern to explore the environment.

        Arguments
        ---------
        path_length: int
            The number of step the agent walks vertically before
            changing direction.
        direction: str {'east', 'west'}
            Indicats which horizontal direction the agent explores.
        """
        if not hasattr(self, 'z_goal'):
            self.z_goal = list(self.graph.get_current().location)

        if not hasattr(self, 'zigzag'):
            self.zigzag = 'south'
            self.prev_zigzag = None

        if self.zigzag == 'south':
            action = self.nav_to((self.z_goal[0], self.z_goal[1]+path_length),
                                 agent_id)
            if not action:
                self.z_goal = list(self.graph.get_current().location)
                self.prev_zigzag = self.zigzag
                self.zigzag = self.options[2]
                self.pretty_print(f'changing direction to {self.zigzag}')

        if self.zigzag == 'north':
            action = self.nav_to((self.z_goal[0], self.z_goal[1]-path_length),
                                 agent_id)
            if not action:
                self.z_goal = list(self.graph.get_current().location)
                self.prev_zigzag = self.zigzag
                self.zigzag = self.options[2]
                self.pretty_print(f'changing direction to {self.zigzag}')

        if self.zigzag == self.options[2]:
            if self.options[2] == 'east':
                action = self.nav_to((self.z_goal[0] + 11, self.z_goal[1]),
                                     agent_id)
            else:
                action = self.nav_to((self.z_goal[0] - 11, self.z_goal[1]),
                                     agent_id)
            if not action:
                self.z_goal = list(self.graph.get_current().location)
                if self.prev_zigzag == 'north':
                    self.prev_zigzag = self.zigzag
                    self.zigzag = 'south'
                else:
                    self.prev_zigzag = self.zigzag
                    self.zigzag = 'north'
                self.pretty_print(f'changing direction to {self.zigzag}')

        return action

    def single_agent_tghm(self):
        """
        This is part of my actual thesis.
        """
        pass

    def multi_agent_explore(self, agent_id, teammate):
        """
        1) Determine which agent moves in which direction
        2) Both start doing the zig-zag exploration

        Arguments
        ---------
        agent_id: str
            The id of the other agent

        """
        pass
