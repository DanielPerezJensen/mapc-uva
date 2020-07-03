from .helpers import Agent
from keras.models import load_model
from keras import metrics
import tensorflow as tf
import os
import random
import time


def root_mean_squared_error(y_true, y_pred):
    return K.sqrt(K.mean(K.square(y_pred - y_true)))


class Attacker(Agent):

    def __init__(self, user, pw, print_json):
        super().__init__(user, pw, print_json)

        # Create and seed a random object
        self.local_random = random.Random()
        seed = int(''.join(str(ord(c)) for c in user))
        self.local_random.seed(seed)

        # Load model
        prefix = os.path.dirname(os.path.abspath(__file__)) + "/"
        self.model = load_model(prefix + "model/t1-n=3", compile=False)
        self.model.compile(loss=root_mean_squared_error, optimizer="rmsprop")
        # Run a dummy predict to initialize fully
        self.model.predict([[[0, 0], [0, 0], [0, 0]]])
        print("Model compiled")

        # Store enemies path
        self.enemy_path = []

    def get_intention(self):
        """
        Gets intentions of this type of agent.
        """
        percept_area = self.percept_area()
        classifications = self.classify_nodes(percept_area)

        # start tracking a builder in case another is not being tracked
        if "builder" in classifications and len(self.enemy_path) < 3:
            builder_idx = classifications.index("builder")
            builder_loc = percept_area[builder_idx].location

            self.enemy_path.append(builder_loc)

            print(self.enemy_path)

            # Only follow agent if he is more than 2 blocks away
            if self.distance(self.current_location(), builder_loc) > 3:

                return self.move_towards_node(percept_area[builder_idx])

            return self.skip_action()

        # In case path is long enough predict enemy future location and clear
        elif len(self.enemy_path) == 3:
            # Hard code prediction in case enemy is standing still since model
            # is not trained for that
            if (self.enemy_path[0] == self.enemy_path[1] and
               self.enemy_path[0] == self.enemy_path[2]):
                prediction = self.enemy_path[0]

            else:
                t = time.time()
                prediction = self.model.predict([self.enemy_path])[0]
                print("Time required for prediction:", time.time() - t)

            # Round and convert predictions to integers
            prediction = [int(round(p)) for p in prediction]

            self.enemy_path = []

            my_coords = self.current_location()

            rel_coords = (prediction[0] - my_coords[0],
                          prediction[1] - my_coords[1])

            return self.clear_fully(*rel_coords)

        return self.move_randomly()

    def skip_action(self):
        intentions = [self.skip]
        args = [tuple()]
        contexts = [tuple()]
        descriptions = ["skip"]
        primitives = [True]

        return intentions, args, contexts, descriptions, primitives

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
        current_location = self.current_location()

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
        contexts = [tuple()] * 3
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

        if x_diff < 0:
            if abs(y_diff) > abs(x_diff) and y_diff > 0:
                return "n"
            elif abs(y_diff) > abs(x_diff) and y_diff < 0:
                return "s"

            return "e"

        else:
            if abs(y_diff) > abs(x_diff) and y_diff > 0:
                return "n"
            elif abs(y_diff) > abs(x_diff) and y_diff < 0:
                return "s"
            return "w"

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

    def distance(self, x, y):
        """
        Reasoning: Returns distance from x to y using manhattan distance
        """
        return sum(abs(x1 - y1) for x1, y1 in zip(x, y))
