from .helpers import Agent
import random


class Mapper(Agent):

    def get_intention(self):
        """
        Gets intentions of this type of agent.
        """
        # Example of what to return:
        #   intentions = [self.nav_to]
        #   args = [((3, 3), self._user_id)]
        #   contexts = [tuple()]
        #   descriptions = ["Primitive"]
        #   primitive = [True]
        #
        # return intentions, args, contexts, descriptions, primitive
        pass

    def refresh(self, mode='landmarks'):
        """
        Go to either unvisited location or important areas of the map.
        """
        if mode == 'landmarks':
            pass  # Visit the important areas of the map
        else:
            pass  # Visit the areas that haven't been visited in a while

    def explore(self, agent_id, options=['single', 'random', 'east']):
        self.options = options
        if self.options[0] == 'multi':
            """
            1) Broadcast location and find another agent to explore with
                If no connection can be made, do single_agent_explore()
            2) Merge maps based on locations
            """
            teammate = "A2"  # agent_broadcast()
            if teammate:
                action = self.multi_agent_explore(agent_id, teammate=teammate)
                return action

        action = self.single_agent_explore(agent_id)
        return action

    def single_agent_explore(self, agent_id):
        """
        Different mode of single agent exploration.
        Serpentine and random will both use pattern recognition to determine
        if the agent has looped the map.
        """
        if self.options[1] == 'random':
            return self.single_agent_random(agent_id)
        elif self.options[1] == 'serpentine':
            return self.single_agent_zig_zag(agent_id)
        elif self.options[1] == 'tghm':
            return self.single_agent_tghm()
        else:
            return None

    def single_agent_random(self, agent_id, min_max=range(5, 15)):
        """
        Explore the world by going to random locations. A random location is
        chosen as goal. If the agent reaches the goal location or it is not
        reachable, a new goal is chosen.

        Arguments
        ---------
        new_obs: list
            A list of the new observations.
        min_max: (int, int)
            The range in which the coordinates will be randomly chosen.
        """
        r = list(min_max) + [-x for x in list(min_max)]
        if not hasattr(self, 'r_goal'):
            self.r_goal = [random.choice(r), random.choice(r)]

        action = self.nav_to((self.r_goal[0], self.r_goal[1]),
                             agent_id)

        if action[0] == '' and action[1] is True:
            self.r_goal[0] += random.choice(r)
            self.r_goal[1] += random.choice(r)
            action = self.skip()
            # action = self.nav_to((self.r_goal[0], self.r_goal[1]),
            # agent_id, new_obs)

        return action

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
                print(f'{self._user}: Changing direction to {self.zigzag}')

        if self.zigzag == 'north':
            action = self.nav_to((self.z_goal[0], self.z_goal[1]-path_length),
                                 agent_id)
            if not action:
                self.z_goal = list(self.graph.get_current().location)
                self.prev_zigzag = self.zigzag
                self.zigzag = self.options[2]
                print(f'{self._user}: Changing direction to {self.zigzag}')

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
                print(f'{self._user}: Changing direction to {self.zigzag}')

        return action

    def single_agent_tghm(self):
        """
        This is part of my actual thesis.
        """
        pass

    def agent_broadcast(self, agent_location):
        """
        Communicate with the other agents to establish a connection for multi
        agent exploration.
        Return agent's id if found, otherwise return False

        Arguments
        ---------
        agent_location: (int, int)
            The location of the other agent your trying to connect to.
        """
        return False

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
