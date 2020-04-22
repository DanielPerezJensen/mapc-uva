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

    # things is a list of triple(s) (type, detail, step)
    def add_things(self, thing):
        for obj in thing:
            self.things.append(obj)

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
        vision, _ = get_vision(None, msg, self.current)

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

    def update_graph(self, msg):
        """
        Update the graph based on the previous action and results.

        Parameters
        ---------
        graph: Graph
            The graph created by the agent.
        msg: dict
            The request-action from the server.
        """

        new_obstacle = []
        if msg["content"]["percept"]["lastAction"] == "move" and \
                msg["content"]["percept"]["lastActionResult"] == "success":

            prev_direction = msg["content"]["percept"]["lastActionParams"][0]
            cx, cy = self.current.loc

            if prev_direction == "n":
                # Update current node and percept
                self.update_current(self.nodes[(cx, cy-1)])
                vision, new_empty = get_vision(self, msg, self.current)
                new_nodes = get_new_nodes(self.current, prev_direction)

            elif prev_direction == "e":
                # Update current node and percept
                self.update_current(self.nodes[(cx+1, cy)])
                vision, new_empty = get_vision(self, msg, self.current)
                new_nodes = get_new_nodes(self.current, prev_direction)

            elif prev_direction == "s":
                # Update current node and percept
                self.update_current(self.nodes[(cx, cy+1)])
                vision, new_empty = get_vision(self, msg, self.current)
                new_nodes = get_new_nodes(self.current, prev_direction)

            elif prev_direction == "w":
                # Update current node and percept
                self.update_current(self.nodes[(cx-1, cy)])
                vision, new_empty = get_vision(self, msg, self.current)
                new_nodes = get_new_nodes(self.current, prev_direction)
            else:
                pass

            for node in new_nodes:
                if node in self.nodes.keys():
                    temp = self.nodes[node]
                    # Update vision information to new node
                    # TODO: Don't add duplicates
                    if temp.loc in vision.keys():
                        temp.set_terrain(vision[temp.loc]["terrain"])
                        temp.add_things(vision[temp.loc]["things"])

                    # Connect node (possibly) in each direction to graph.
                    self.add_neighbours(temp)

                else:
                    # Create new node
                    self.nodes[node] = Node(node)
                    temp = self.nodes[node]

                    # Add vision information to new node
                    if temp.loc in vision.keys():
                        if vision[temp.loc]["terrain"] == "obstacle":
                            new_obstacle.append(temp.loc)

                        temp.set_terrain(vision[temp.loc]["terrain"])
                        temp.add_things(vision[temp.loc]["things"])

                    # Connect node (possibly) in each direction to graph.
                    self.add_neighbours(temp)
        
        return new_empty, new_obstacle


    def add_neighbours(self, node):
        """
        Connect node the graph in (possibly) each direction.
        """
        x, y = node.loc
        # Northern connection
        if (x, y-1) in self.nodes.keys():
            # TODO: If these 2 are different, than agent has looped map.
            node.add_direction(north=self.nodes[(x, y-1)])
            self.nodes[(x, y-1)].add_direction(south=node)
        
        # Eastern connection
        if (x+1, y) in self.nodes.keys():
            # TODO: If these 2 are different, than agent has looped map.
            node.add_direction(east=self.nodes[(x+1, y)])
            self.nodes[(x+1, y)].add_direction(west=node)
        
        # Southern connection
        if (x, y+1) in self.nodes.keys():
            # TODO: If these 2 are different, than agent has looped map.
            node.add_direction(south=self.nodes[(x, y+1)])
            self.nodes[(x, y+1)].add_direction(north=node)
        
        # Western connection
        if (x-1, y) in self.nodes.keys():
            # TODO: If these 2 are different, than agent has looped map.
            node.add_direction(west=self.nodes[(x-1, y)])
            self.nodes[(x-1, y)].add_direction(east=node)


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
        else:
            print("---------------------------------------")
            print("ERROR: New node is not a Node object...")
            print("---------------------------------------")


def get_vision(graph, msg, current_node):
    """
    Uses the agents perception to create a dict, with a (x,y)-tuple as key
    and a nested dict as value. The nested dict contains the type of
    terrain on that coordinate and the things on that location.

    Parameters
    ----------
    msg: dict
        The request-action from the server.
    """
    agent_x, agent_y = current_node.loc
    vision = {}
    terrain_percept = msg['content']['percept']['terrain']
    things_percept = msg['content']['percept']['things']
    step = msg['content']['step']
    new_empty = []
    
    if graph:
        # Check if new node became empty. TODO: optimize?
        vision_nodes = []
        for x in range(-5, 6):
            for y in range(-5, 6):
                if abs(x) + abs(y) <= 5:
                    vision_nodes.append((x + agent_x, y + agent_y))
        
        for node in vision_nodes:
            if node in graph.nodes.keys():
                if graph.nodes[node].terrain == "obstacle":
                    relative_node = [node[0] - agent_x, node[1] - agent_y]
                    if relative_node not in terrain_percept["obstacle"]:
                        # Node isn't obstacle anymore -> obstacle got removed
                        new_empty.append(node)

    # Create terrain information
    for terrain_option in terrain_percept.keys():
        for x, y in terrain_percept[terrain_option]:
            abs_x, abs_y = agent_x + x, agent_y + y
            if (abs_x, abs_y) in vision.keys():
                vision[(abs_x, abs_y)]["terrain"] = terrain_option
            else:
                vision[(abs_x, abs_y)] = {"terrain": terrain_option,
                                        "things": []}

    # Create things information
    # TODO: Add steps to things (tuple -> triple)
    for thing in things_percept:
        x, y = thing["x"], thing["y"]
        abs_x, abs_y = agent_x + x, agent_y + y
        if (abs_x, abs_y) in vision.keys():
            vision[(abs_x, abs_y)]["things"].append((thing["type"],
                                                    thing["details"], step))
        else:
            vision[(abs_x, abs_y)] = {"terrain": "empty",
                                    "things": [(thing["type"],
                                                thing["details"], step)]}

    return vision, new_empty

def get_new_nodes(current, direction):
    """
    Gets coordinates of the new nodes relative to the root node.

    Parameters
    ----------
    current: Node
        The node the agent is currently located
    direction: str
        The direction in which the new nodes have to be created.
    """
    current_x, current_y = current.loc
    new_nodes = []
    if direction == "n":
        for x in range(-5, 6):
            if x < 0:
                y = -5-x
            elif x >= 0:
                y = -5+x
            new_nodes.append((x + current_x , y + current_y))
    
    elif direction == "e":
        for y in range(-5, 6):
            if y < 0:
                x = 5+y
            elif y >= 0:
                x = 5-y
            new_nodes.append((x + current_x , y + current_y))

    elif direction == "s":
        for x in range(-5, 6):
            if x < 0:
                y = 5+x
            elif x >= 0:
                y = 5-x
            new_nodes.append((x + current_x , y + current_y))

    elif direction == "w":
        for y in range(-5, 6):
            if y < 0:
                x = -5-y
            elif y >= 0:
                x = -5+y
            new_nodes.append((x + current_x , y + current_y))

    return new_nodes

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
        "terrain":{"obstacle":[[0, 5]]},\
        "lastActionResult":"success","tasks":[],"energy":300},\
        "deadline":1587488848109}}')

    g = Graph(msg_1)
    new_empty, new_obstacle = g.update_graph(msg_2)
    print(get_vision(g, msg_1, Node((0,0))))
