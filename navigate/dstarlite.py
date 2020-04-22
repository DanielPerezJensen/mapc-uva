from collections import deque
from functools import partial

from pydstarlite.utility import draw_grid
from pydstarlite.priority_queue import PriorityQueue
# from pydstarlite.grid import AgentViewGrid, Graph
from pydstarlite.utility import grid_from_string


class DStarLite(object):
    def __init__(self, graph, goal):
        """
        Find the path to the goal location from the current position

        parameters
        ----------
        graph: object
            Instance of the current graph
        start: tuple
            Starting coordinates
        goal: tuple
            Goal coordinates
        """

        # Init the graph
        self.graph = graph

        self.back_pointers = {}
        self.G_VALS = {}
        self.RHS_VALS = {}
        self.Km = 0
        self.position = graph.current.key
        self.goal = goal
        self.queue = PriorityQueue()
        self.queue.put(self.goal, self.calculate_key(self.goal))
        self.back_pointers[self.goal] = None

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
        self.graph.nodes[node].directions.values
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
        self.compute_shortest_path()
        self.last_node = self.position

        while self.position != self.goal:
            if self.g(self.position) == float('inf'):
                raise Exception("No path")

            self.position = self.lowest_cost_neighbour(self.position)

            yield self.position

    def update_graph(self, new_graph, new_walls):
        """
        Update the graph with the new observations.

        parameters
        ----------
        new_graph: object
            A new Graph (graph.py) instance.
        """

        self.graph = new_graph

        if new_walls:
            self.Km += self.heuristic(self.last_node, self.position)
            self.last_node = self.position
            self.update_nodes({node for wallnode in new_walls
                                for node in self.neighbors(wallnode)
                                if (node not in self.graph.nodes or not self.graph.nodes[node]._is_obstacle())})
            self.compute_shortest_path()





if __name__ == "__main__":
    GRAPH, START, END = grid_from_string("""
    ..........
    ...######.
    .......A#.
    ...######.
    ...#....#.
    ...#....#.
    ........#.
    ........#.
    ........#Z
    ........#.
    """)
    dstar = DStarLite(GRAPH, START, END)
    path = [p for p, o, w in dstar.move_to_goal()]

    print("The graph (A=Start, Z=Goal)")
    draw_grid(GRAPH, width=3, start=START, goal=END)
    print("\n\nPath taken (@ symbols)")
    draw_grid(GRAPH, width=3, path=path)