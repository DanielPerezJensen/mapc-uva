from .helpers import Agent
import random


class Attacker(Agent):

    def __init__(self, user, pw, print_json=False):
        """
        """
        super().__init__(user, pw, print_json)
        self.local_random = random.Random()
        self.local_random.seed(int(user[6:] * 1024))

    def get_intention(self):
        """
        Gets intentions of this type of agent.
        """
        percept_area = self.percept_area()
        classifications = self.classify_nodes(percept_area)

        if "builder" in classifications:
            builder_idx = classifications.index("builder")

            builder_coords = percept_area[builder_idx].location
            my_coords = self.current_location()

            rel_coords = (builder_coords[0] - my_coords[0],
                          builder_coords[1] - my_coords[1])

            return self.clear_fully(*rel_coords)

        return self.move_randomly()

    def move_randomly(self):
        """
        Intention: Moves the agent randomly in a given direction
        """
        intentions = [self.move]
        args = [(self.local_random.choice(['n', 'e', 's', 'w']),)]
        contexts = [tuple()]
        descriptions = ["moveRandomly"]
        primitives = [True]

        return intentions, args, contexts, descriptions, primitives

    def move_towards_node(self, node):
        """
        Intention: Moves the agent towards a node one step at a time
        """
        current_location = self.beliefs.current_location()

        rel_direction = self.get_relative_direction(current_location,
                                                    node.location)

        intentions = [self.move]
        args = [(rel_direction,)]
        contexts = [tuple()]
        descriptions = [f"moveTowards({node.location})"]
        primitives = [True]

        return intentions, args, contexts, descriptions, primitives

    def clear_fully(self, x, y):
        """
        Intention: Clears a coordinate fully thus exploding a bomb in
        that location
        """
        intentions = [self.clear] * 3
        args = [(x, y)] * 3
        contexts = [((x, y), ('entity', 'B'))] * 3
        descriptions = ["clear1", "clear2", "clear3"]
        primitives = [True, True, True]

        return intentions, args, contexts, descriptions, primitives

    def get_relative_direction(self, coordinate, relative):
        """
        Reasoning: Returns the relative direction of the relative node
        compared to the coordinate
        """
        x_diff = coordinate[0] - relative[0]
        y_diff = coordinate[1] - relative[1]

        if x_diff > 0 and abs(x_diff) > abs(y_diff):
            return 'w'
        if x_diff < 0 and abs(x_diff) > abs(y_diff):
            return 'e'
        if y_diff >= 0 and abs(y_diff) > abs(x_diff):
            return 'n'
        if y_diff < 0 and abs(y_diff) > abs(x_diff):
            return 's'

    def classify_nodes(self, nodes):
        """
        Reasoning: Classifies all nodes in nodes list and returns a list
        of classifications
        """
        return [self.classify_node(n) for n in nodes]

    def classify_node(self, node):
        """
        Reasoning: Classifies a node as either containing an enemy and
        what type or as a friendly
        """
        things = node.get_things(self.beliefs.step)
        if ('entity', 'A') in things:
            if node.location == self.beliefs.current[self._user_id].location:
                return "self"
            else:
                return "friendly"
        elif ('entity', 'B') in things:
            if self.blocks_around_node(node) > 2:
                return "builder"
            return "enemy"

        return None

    def blocks_around_node(self, node):
        """
        Reasoning: Returns the amount of blocks around a given node
        """

        count = 0

        x, y = node.location

        for node in self.neighbourhood(x, y, depth=2):
            things = node.get_things(self.beliefs.step)
            for itemtype, item in things:
                if itemtype == "block":
                    count += 1

        return count

    def percept_area(self):
        """
        Reasoning: Returns all nodes within the percept from the
        current location of the agent
        """
        return [self.beliefs.get_node((x, y)) for x, y in
                self.beliefs.get_local_node_locations(self._user_id)]

    def neighbourhood(self, x, y, depth=1):
        """
        Reasoning: Returns all nodes within the neighbourhood of a given
        coordinate to a given depth, a depth of 2 would return all nodes that
        are no more than 2 blocks away from the agent.

        args:
            x: int
                x coordinate
            y: int
                y coordinate
            depth=1: int
                depth of neighbourhood
        """
        node_list = []

        for i in range(x - depth, x + depth + 1):
            for j in range(y - depth, y + depth + 1):
                if (i != x or j != y):
                    n = self.beliefs.get_node((i, j))
                    if n:
                        node_list.append(n)

        return node_list
