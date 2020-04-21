from collections import defaultdict
import json


class Node(object):
    def __init__(self, key, terrain="empty", things=[], north=None, east=None,
                 south=None, west=None):

        self.key = key          # coordinates: tuple(x, y)
        self.terrain = terrain  # str
        self.things = things     # list containing tuples
        self.directions = {     # dict containing surrounding nodes
            "north": north,
            "east": east,
            "south": south,
            "west": west
        }

    # terrain is a str
    def set_terrain(self, terrain):
        self.terrain = terrain
        return True

    # thing is a tuple (type, detail)
    def add_thing(self, thing):
        self.things.append(thing)
        return True

    def remove_thing(self, thing):
        if thing in self.things:
            self.things.remove(thing)
            return True
        return False

    def add_direction(self, north=None, east=None, south=None, west=None):
        if isinstance(north, Node):
            self.directions["north"] = north

        if isinstance(east, Node):
            self.directions["east"] = east

        if isinstance(south, Node):
            self.directions["south"] = south

        if isinstance(west, Node):
            self.directions["west"] = west


class Graph(object):
    def __init__(self, msg):
        self.root = Node((0, 0))
        self.current = self.root
        self.nodes = {(0, 0): self.root}
        vision = get_vision(msg)

        # Self.nodes contains all {(x, y):Node} combination currently in the graph.
        for x in range(-5, 6):
            for y in range(-5, 6):
                if abs(x) + abs(y) <= 5:
                    self.nodes[(x, y)] = Node((x, y))
                    # Add information given by get_vision()

        # For loop that connects all the nodes in self.nodes by [north, east,
        # south, west].

    def update_graph(self, graph, msg):
        """
        Update the graph based on the previous action and results.

        Parameters
        ---------
        graph: Graph
            The graph created by the agent.
        msg: dict
            The request-action from the server.
        """
        pass

    def get_current(self):
        """
        Returns the node of the agent's current location.

        Returns
        -------
        current node: Node
            The node of the agent's current location.
        """
        return self.current

    def update_current(self, node):
        """
        Update the agent's current location.

        Parameters
        ----------
        node: Node
            The node on which the agent is currently place.
        """
        if isinstance(node, Node):
            self.current = node
            return True
        return False


def get_vision(msg):
    """
    Uses the agents perception to create a dict, with a (x,y)-tuple as key
    and a nested dict as value. The nested dict contains the type of
    terrain on that coordinate and the things on that location.

    Parameters
    ----------
    msg: dict
        The request-action from the server.
    """
    vision = {}
    terrain = msg['content']['percept']['terrain']

    for terrain_option in terrain.keys():
        for x, y in terrain[terrain_option]:
            if (x, y) in vision.keys():
                vision[(x, y)]["terrain"] = terrain_option
            else:
                vision[(x, y)] = {"terrain": terrain_option, "things": []}

    for thing in msg['content']['percept']['things']:
        x, y = thing["x"], thing["y"]
        if (x, y) in vision.keys():
            vision[(x, y)]["things"].append((thing["type"], thing["details"]))
        else:
            vision[(x, y)] = {"terrain": "empty",
                              "things": [(thing["type"], thing["details"])]}

    return vision


msg = json.loads('{"type":"request-action","content":{"step":0,"id":0,\
"time":1587299386431,"percept":{"lastActionParams":[],\
"score":0,"task":"","lastAction":"",\
"things":[{"x":1,"y":0,"details":"A","type":"entity"},\
{"x":1,"y":-1,"details":"B","type":"entity"},\
{"x":1,"y":-1,"details":"A","type":"entity"},\
{"x":1,"y":0,"details":"B","type":"entity"},\
{"x":0,"y":0,"details":"A","type":"entity"},\
{"x":0,"y":0,"details":"B","type":"entity"}],\
"attached":[],\
"disabled":false,\
"terrain":{"obstacle":[[1,4],[0,4],[-1,4],[0,5]]},\
"lastActionResult":"","tasks":[],"energy":300}, \
"deadline":1587299390456}}')

g = Graph(msg)
print(len(g.nodes.keys()))

print("\nCongrats, you haven't royally butt-flapped it up yet...")
