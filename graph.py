import json


class Node(object):
    """
    Creates a node used in the graph
    """
    def __init__(self, loc, terrain="empty", things=[], north=None, east=None,
                 south=None, west=None):
        """
        Initialize the node

        Parameters
        ----------
        loc: tuple(int, int)
            The x and y coordinate of the node relative to the graph root
        terrain: str
            The type of terrain (empty, obstacle, goal)
        things: list
            Things in the node (entities, blocks, dispensers, markers) and
            details about each.
        north, east, south, west: Node
            The node to the corresponding direction from the current node.
        """
        self.loc = loc
        self.terrain = terrain
        self.things = things
        self.directions = {
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
    """
    Class used to create and update the graph
    """
    def __init__(self, msg):
        self.root = Node((0, 0))
        self.current = self.root
        self.nodes = {(0, 0): self.root}
        vision = get_vision(msg)

        for x in range(-5, 6):
            for y in range(-5, 6):
                if abs(x) + abs(y) <= 5:
                    if (x, y) in vision.keys():
                        info = vision[(x, y)]
                        self.nodes[(x, y)] = Node((x, y),
                                                  terrain=info["terrain"],
                                                  things=info["things"])
                    else:
                        self.nodes[(x, y)] = Node((x, y))

        for current_node in self.nodes.values():
            x, y = current_node.loc
            if (x, y-1) in self.nodes.keys():
                current_node.add_direction(north=self.nodes[(x, y-1)])

            if (x+1, y) in self.nodes.keys():
                current_node.add_direction(east=self.nodes[(x+1, y)])

            if (x, y+1) in self.nodes.keys():
                current_node.add_direction(south=self.nodes[(x, y+1)])

            if (x-1, y) in self.nodes.keys():
                current_node.add_direction(west=self.nodes[(x-1, y)])

    def add_neighbours(self, current_node):
        pass

    def update_graph(self, msg, current):
        """
        Update the graph based on the previous action and results.

        Parameters
        ---------
        graph: Graph
            The graph created by the agent.
        msg: dict
            The request-action from the server.
        """
        if msg["content"]["percept"]["lastAction"] == "move" and \
                msg["content"]["percept"]["lastActionResult"] == "success":

            prev_direction = msg["content"]["percept"]["lastActionParams"]
            
            """
            A. Add new nodes and update paths
                1) Create new nodes and add paths to current graph.
                2) Add path from graph to new nodes.
                3)Exceptions for when new nodes already exist?
            B. Use get_vision to update events
            """

        else:
            print("Nothing to update")
            return False


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


if __name__ == "__main__":
    msg_1 = json.loads('{"type":"request-action","content":{"step":0,"id":0,\
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
        "lastActionResult":"","tasks":[],"energy":300},\
        "deadline":1587299390456}}')

    msg_2 = json.loads('{"type":"request-action","content":{"step":1,"id":1,\
        "time":1587488844089,"percept":{"lastActionParams":["n"],\
        "score":0,"task":"","lastAction":"move",\
        "things":[{"x":1,"y":1,"details":"A","type":"entity"},\
        {"x":0,"y":0,"details":"A","type":"entity"},\
        {"x":0,"y":1,"details":"B","type":"entity"},\
        {"x":1,"y":0,"details":"B","type":"entity"},\
        {"x":1,"y":1,"details":"B","type":"entity"},\
        {"x":1,"y":0,"details":"A","type":"entity"}],\
        "attached":[],\
        "disabled":false,\
        "terrain":{"obstacle":[[0,5]]},\
        "lastActionResult":"success","tasks":[],"energy":300},\
        "deadline":1587488848109}}')
    
    g = Graph(msg_1)
    g.update_graph(msg_2, current)
