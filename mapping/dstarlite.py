from collections import deque
from functools import partial

from mapping.priority_queue import PriorityQueue


class DStarLite(object):
    def __init__(self, graph, goal, last_action):
        """
        Find the path to the goal location from the current position

        parameters
        ----------
        graph: object
            Instance of the current graph
        goal: tuple
            Goal x and y coordinates
        last_action: str
            The direction of last move performed by the agent or an empty string
        """

        # Init the graph
        self.graph = graph

        self.back_pointers = {}
        self.G_VALS = {}
        self.RHS_VALS = {}
        self.Km = 0
        self.position = graph.current.loc
        self.goal = goal
        self.queue = PriorityQueue()
        self.queue.put(self.goal, self.calculate_key(self.goal))
        self.back_pointers[self.goal] = None

        # check for the last action
        if last_action:
            (cx, cy) = self.position
            if last_action == "n":
                self.position = (cx, cy-1)
            elif last_action == "s":
                self.position = (cx, cy+1)
            elif last_action == "w":
                self.position = (cx-1, cy)
            elif last_action == "e":
                self.position = (cx+1, cy)


    def transition_cost(self, from_node, to_node):
        """
        Returns the cost of the node transition.

        parameters
        ----------
        from_node: tuple
            x and y coordinate of first node
        to_node: tuple
            x and y coordinate of second node
        """
        if from_node in self.graph.nodes and self.graph.nodes[from_node]._is_obstacle():
                return float('inf')
        
        if to_node in self.graph.nodes and self.graph.nodes[to_node]._is_obstacle(): 
                return float('inf')
        
        return 1

    def neighbors(self, id):
        (x, y) = id
        results = [(x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)]
        if (x + y) % 2 == 0: results.reverse()  # aesthetics
        return results

    def calculate_rhs(self, node):
        lowest_cost_neighbour = self.lowest_cost_neighbour(node)
        self.back_pointers[node] = lowest_cost_neighbour
        return self.lookahead_cost(node, lowest_cost_neighbour)

    def lookahead_cost(self, node, neighbour):
        return self.g(neighbour) + self.transition_cost(neighbour, node)

    def lowest_cost_neighbour(self, node):
        cost = partial(self.lookahead_cost, node)
        return min(self.neighbors(node), key=cost)

    def g(self, node):
        return self.G_VALS.get(node, float('inf'))

    def rhs(self, node):
        return self.RHS_VALS.get(node, float('inf')) if node != self.goal else 0

    def heuristic(self, a, b):
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)

    def calculate_key(self, node):
        g_rhs = min([self.g(node), self.rhs(node)])

        return (
            g_rhs + self.heuristic(node, self.position) + self.Km,
            g_rhs
        )

    def update_node(self, node):
        if node != self.goal:
            self.RHS_VALS[node] = self.calculate_rhs(node)
        self.queue.delete(node)
        if self.g(node) != self.rhs(node):
            self.queue.put(node, self.calculate_key(node))

    def update_nodes(self, nodes):
        [self.update_node(n) for n in nodes]

    def compute_shortest_path(self):
        last_nodes = deque(maxlen=10)
        while self.queue.first_key() < self.calculate_key(self.position) or self.rhs(self.position) != self.g(self.position):
            k_old = self.queue.first_key()
            node = self.queue.pop()
            last_nodes.append(node)
            if len(last_nodes) == 10 and len(set(last_nodes)) < 3:
                raise Exception("Fail! Stuck in a loop")
            k_new = self.calculate_key(node)
            if k_old < k_new:
                self.queue.put(node, k_new)
            elif self.g(node) > self.rhs(node):
                self.G_VALS[node] = self.rhs(node)
                self.update_nodes(self.neighbors(node))
            else:
                self.G_VALS[node] = float('inf')
                self.update_nodes(self.neighbors(node) + [node])

        return self.back_pointers.copy(), self.G_VALS.copy()

    def move_to_goal(self):
        """
        Generator object that yields the best next step at each call.
        """
        if self.position != self.goal:
            self.compute_shortest_path()

            while self.position != self.goal:
                if self.g(self.position) == float('inf'):
                    yield False, False

                self.last_node = self.graph.current.loc

                self.position = self.lowest_cost_neighbour(self.position)
                self.recovery_loc = self.lowest_cost_neighbour(self.last_node)
                # yield the next step to be taken, and the step to be taken if the last step failed
                yield self.position, self.recovery_loc


    def update_graph(self, new_graph, new_obs, step_sent):
        """
        Update the graph with the new observations.

        parameters
        ----------
        new_graph: object
            The updated Graph (graph.py) instance.
        new_obs: list
            A list of all new walls and new free spots in the percept.
        step_sent: bool
            Indicating if the desired action was sent to the server, 
            if not, the recovery action was sent.
        """

        self.graph = new_graph

        if not step_sent:
            self.position = self.recovery_loc
        
        # Update the path if there are new observations
        if new_obs:
            self.Km += self.heuristic(self.last_node, self.position)
            
            self.update_nodes({node for wallnode in new_obs
                                for node in self.neighbors(wallnode)
                                if (node not in self.graph.nodes or not self.graph.nodes[node]._is_obstacle())})
            self.compute_shortest_path()
        