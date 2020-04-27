import json


class Node(object):
    """
    Creates a node used in the graph
    """
    def __init__(self, loc, terrain="empty", terrain_step=0, things=[], north=None, east=None,
                 south=None, west=None):
        """
        Initialize the node

        Parameters
        ----------
        loc: tuple(int, int)
            The x and y coordinate of the node relative to the graph root.
        terrain: str
            The type of terrain (empty, obstacle, goal).
        terrain_step: int
            The step in which the terrain has changed (used when merging graphs).
        things: list
            Things in the node (entities, blocks, dispensers, markers) and
            details about each.
        north, east, south, west: Node
            The node to the corresponding direction from the current node.
        """
        self.loc = loc
        self.terrain = terrain
        self.terrain_step = terrain_step
        self.things = []
        self.directions = {
            "north": north,
            "east": east,
            "south": south,
            "west": west
        }

    # terrain is a str
    def set_terrain(self, terrain):
        self.terrain = terrain

    def set_terrain_step(self, terrain_step):
        self.terrain_step = terrain_step

    def set_loc(self, new_loc):
        self.loc = new_loc    

    # things is a list of triple(s) (type, detail, step)
    def add_things(self, thing):
        if isinstance(thing, list):
            for obj in thing:
                self.things.append(obj)
        else:
            self.things.append(thing)

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

    def _is_obstacle(self, step, current):
        if self.terrain in ["empty", "goal"]:
            if current == self.loc:
                return False
            elif [agent for agent in self.things if agent[2] == step] == []:
                return False
            
        return True


class Graph(object):
    """
    Class used to create and update the graph
    """
    def __init__(self):
        self.nodes = {}
        self.step = 0
        
        for x in range(-5, 6):
            for y in range(-5, 6):
                if abs(x) + abs(y) <= 5:
                    self.nodes[(x, y)] = Node((x, y))

        self.root = self.nodes[(0, 0)]
        self.current = self.root

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

    def initial_vision(self, msg):
        new_obstacle = []
        vision, new_empty = get_vision(self, msg, self.current)
        for node in self.nodes.keys():
            if node in vision.keys():
                if vision[node]["terrain"] == "obstacle" and \
                        self.nodes[node].terrain != "obstacle":
                    new_obstacle.append(node)
                
                self.nodes[node].set_terrain(vision[node]["terrain"])
                self.nodes[node].set_terrain_step(vision[node]["step"])
                self.nodes[node].add_things(vision[node]["things"])

        return new_obstacle, new_empty

    def update_current(self, msg):
        """
        Update the Agent's current location 
        based on the previous action and results.

        Parameters
        ----------
        msg: dict
            The request-action from the server.

        Returns True if the location has been updated,
        False if is has not been changed
        """
        if msg["content"]["percept"]["lastAction"] == "move" and \
                msg["content"]["percept"]["lastActionResult"] == "success":

            prev_direction = msg["content"]["percept"]["lastActionParams"][0]

            if prev_direction == "n":
                new_loc = self.current.directions['north']
            elif prev_direction == "e":
                new_loc = self.current.directions['east']
            elif prev_direction == "s":
                new_loc = self.current.directions['south']
            elif prev_direction == "w":
                new_loc = self.current.directions['west']
            
            if isinstance(new_loc, Node):
                self.current = new_loc
            else:
                print("---------------------------------------")
                print("ERROR: New node is not a Node object...")
                print("---------------------------------------")

            # the location has changed
            return True

        # the location has not changed
        return False


    def update_graph(self, msg):
        """
        Update the graph based on the previous action and results.

        Parameters
        ----------
        msg: dict
            The request-action from the server.
        """
        self.step = msg['content']['step']
        new_obstacle, new_empty = [], []
        if msg["content"]["percept"]["lastAction"] == "move" and \
                msg["content"]["percept"]["lastActionResult"] == "success":

            prev_direction = msg["content"]["percept"]["lastActionParams"][0]
            cx, cy = self.current.loc
            
            vision, new_empty = get_vision(self, msg, self.current)
            new_nodes = get_new_nodes(self.current, prev_direction)

            for node in new_nodes:
                if node in self.nodes.keys():
                    temp = self.nodes[node]

                    # Update vision information to new node
                    if temp.loc in vision.keys():
                        temp.set_terrain(vision[temp.loc]["terrain"])
                        temp.set_terrain_step(vision[temp.loc]["step"])
                        for thing in vision[temp.loc]["things"]:
                            # Ignores adding the same dispenser twice
                            if thing[0] != "dispenser":
                                temp.add_things(thing)

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
                        temp.set_terrain_step(vision[temp.loc]["step"])
                        temp.add_things(vision[temp.loc]["things"])

                    # Connect node (possibly) in each direction to graph.
                    self.add_neighbours(temp)
        else:
            new_obstacle, new_empty = self.initial_vision(msg)
        
        return new_obstacle, new_empty, self.new_agents()

    def new_agents(self):
        new_agents = []
        if self.step == 0:
            return [loc[0] for loc in self.get_agents()]
        else:
            current = self.get_agents(step=self.step, team="A")
            current += self.get_agents(step=self.step, team="B")
            current_loc = [loc[0] for loc in current]

            previous = self.get_agents(step=self.step-1, team="A")
            previous += self.get_agents(step=self.step-1, team="B")
            previous_loc = [loc[0] for loc in previous]

            for loc in current_loc:
                if loc not in previous_loc:
                    new_agents.append(loc)
            
        while self.current in new_agents:
            new_agents.remove(self.current)

        return new_agents

    def add_neighbours(self, node):
        """
        Connect node the graph in (possibly) each direction.
        """
        # TODO: If temp->node & node->temp are different nodes than the agent
        #       has looped the map.
        x, y = node.loc
        # Northern connection
        if (x, y-1) in self.nodes.keys():
            node.add_direction(north=self.nodes[(x, y-1)])
            self.nodes[(x, y-1)].add_direction(south=node)

        # Eastern connection
        if (x+1, y) in self.nodes.keys():
            node.add_direction(east=self.nodes[(x+1, y)])
            self.nodes[(x+1, y)].add_direction(west=node)
        
        # Southern connection
        if (x, y+1) in self.nodes.keys():
            node.add_direction(south=self.nodes[(x, y+1)])
            self.nodes[(x, y+1)].add_direction(north=node)
        
        # Western connection
        if (x-1, y) in self.nodes.keys():
            node.add_direction(west=self.nodes[(x-1, y)])
            self.nodes[(x-1, y)].add_direction(east=node)

    def get_direction(self, loc):
        """
        Returns the direction of the given location 
        relative to the current location.
        
        parameters
        ----------
        loc: tuple
            x and y coordinates of given location. 
            Should be adjacent to the current location.
        """
        if loc[0] > self.current.loc[0]:
            return "e"
        elif loc[0] < self.current.loc[0]:
            return "w"
        elif loc[1] > self.current.loc[1]:
            return "s"
        elif loc[1] < self.current.loc[1]:
            return "n"
        else:
            return ""

    def get_current(self):
        """
        Returns the node of the agent's current location.

        Returns
        -------
        current node: Node
            The node of the agent's current location.
        """
        return self.current

    def get_agents(self, step=-1, team="A"):
        """
        Returns the locations of friendly agents, on a certain step (if given).

        parameters
        ----------
        step: int
            The step on which the agents were seen.
            If step is -1, give every location.
        """
        agents = []
        for node in self.nodes:
            for thing in self.nodes[node].things:
                if thing[0] == "entity" and thing[1] == team:
                    if step == -1:
                        agents.append((node, thing))
                    elif thing[2] == step:
                        agents.append((node, thing))
        return agents


def merge_graphs(g1, g2, offset=(1, 0)):
    """
    Merge graphs of two agents. The root node of the first agent (a1) will now 
    also become the root node of the second agent (a2).

    parameters
    ----------
    g1, g2: Graph
        The graphs of the first and second agent, respectively
    offset: tuple (int, int)
        The location of the second agent from the perspective of the first agent.
    """
    # TODO: Add step to terrain for up-to-date map merging
    g1_x, g1_y = g1.get_current().loc
    g2_x, g2_y = g2.get_current().loc

    # Calculate the root offset
    rx, ry = (g1_x + offset[0] + g2_x, g1_y + offset[1] + g2_y)

    for x, y in g2.nodes:
        new_x, new_y = rx + x, ry + y

        if (new_x, new_y) in g1.nodes:
            # Check which map has the most up-to-date terrain info
            if g1.nodes[(new_x, new_y)].terrain_step < \
                    g2.nodes[(x, y)].terrain_step:
                g1.nodes[(new_x, new_y)].set_terrain(g2.nodes[(x, y)].terrain)

            for thing in g2.nodes[(x, y)].things:
                if thing not in g1.nodes[(new_x, new_y)].things:
                    g1.nodes[(new_x, new_y)].add_things(thing)
        else:
            g1.nodes[(new_x, new_y)] = g2.nodes[(x, y)]
            g1.nodes[(new_x, new_y)].set_loc((new_x, new_y))
            g1.add_neighbours(g1.nodes[(new_x, new_y)])

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
        # Check if new node became empty.
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
                vision[(abs_x, abs_y)]["step"] = step
            else:
                vision[(abs_x, abs_y)] = {"terrain": terrain_option,
                                          "step": step,
                                          "things": []}

    # Create things information
    for thing in things_percept:
        x, y = thing["x"], thing["y"]
        abs_x, abs_y = agent_x + x, agent_y + y
        if (abs_x, abs_y) in vision.keys():
            vision[(abs_x, abs_y)]["things"].append((thing["type"],
                                                     thing["details"], step))
        else:
            vision[(abs_x, abs_y)] = {"terrain": "empty",
                                      "step": step,
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
    msg_1 = json.loads('{\
        "type":\
            "request-action",\
        "content":{\
            "step":0,\
            "id":0,\
            "time":1587299386431,\
            "percept":{\
                "lastActionParams":[],\
                "score":0,\
                "task":"",\
                "lastAction":"",\
                "things":[\
                    {"x":1,"y":0,"details":"A","type":"entity"},\
                    {"x":1,"y":-1,"details":"B","type":"entity"},\
                    {"x":1,"y":-1,"details":"A","type":"entity"},\
                    {"x":1,"y":0,"details":"B","type":"entity"},\
                    {"x":0,"y":0,"details":"A","type":"entity"},\
                    {"x":0,"y":0,"details":"B","type":"entity"}],\
                "attached":[],\
                "disabled":false,\
                "terrain":{\
                    "obstacle":[[1,4],[0,4],[-1,4],[0,5]]},\
                "lastActionResult":"",\
                "tasks":[],\
                "energy":300},\
            "deadline":1587299390456}}')

    msg_1_1 = json.loads('{\
        "type":\
            "request-action",\
        "content":{\
            "step":1,\
            "id":1,\
            "time":1587488844089,\
            "percept":{\
                "lastActionParams":["n"],\
                "score":0,\
                "task":"",\
                "lastAction":"move",\
                "things":[\
                    {"x":1,"y":1,"details":"A","type":"entity"},\
                    {"x":0,"y":0,"details":"A","type":"entity"},\
                    {"x":0,"y":1,"details":"B","type":"entity"},\
                    {"x":1,"y":0,"details":"B","type":"entity"},\
                    {"x":1,"y":1,"details":"B","type":"entity"},\
                    {"x":1,"y":0,"details":"A","type":"entity"}],\
                "attached":[],\
                "disabled":false,\
                "terrain":{\
                    "obstacle":[[0, 5]]},\
                "lastActionResult":"success",\
                "tasks":[],\
                "energy":300},\
            "deadline":1587488848109}}')

    msg_2 = json.loads('{\
        "type":\
            "request-action",\
        "content":{\
            "step":0,\
            "id":0,\
            "time":1587837247681,\
            "percept":{\
                "lastActionParams":[],\
                "score":0,\
                "task":"",\
                "lastAction":"",\
                "things":[\
                    {"x":-1,"y":0,"details":"A","type":"entity"},\
                    {"x":0,"y":-1,"details":"B","type":"entity"},\
                    {"x":0,"y":0,"details":"B","type":"entity"},\
                    {"x":0,"y":-1,"details":"A","type":"entity"},\
                    {"x":-1,"y":0,"details":"B","type":"entity"},\
                    {"x":0,"y":0,"details":"A","type":"entity"}],\
                "attached":[],\
                "disabled":false,\
                "terrain":{\
                    "obstacle":[[0,4],[-1,4],[0,5]]},\
                "lastActionResult":"",\
                "tasks":[],\
                "energy":300},\
            "deadline":1587837251697}}')
    
    msg_2_2 = json.loads('{\
        "type":\
            "request-action",\
        "content":{\
            "step":1,\
            "id":1,\
            "time":1587837759849,\
            "percept":{\
                "lastActionParams":["s"],\
                "score":0,"task":"",\
                "lastAction":"move",\
                "things":[\
                    {"x":-1,"y":-1,"details":"B","type":"entity"},\
                    {"x":0,"y":-2,"details":"A","type":"entity"},\
                    {"x":0,"y":-2,"details":"B","type":"entity"},\
                    {"x":-1,"y":-1,"details":"A","type":"entity"},\
                    {"x":0,"y":0,"details":"A","type":"entity"},\
                    {"x":0,"y":-1,"details":"B","type":"entity"}],\
                "attached":[],\
                "disabled":false,\
                "terrain":{\
                    "obstacle":[[0,3],[1,4],[-1,3],[0,4],[-2,3],[-1,4],[0,5],[5,0],[4,1]]},\
                "lastActionResult":"success",\
                "tasks":[],\
                "energy":300},\
            "deadline":1587837763855}}')

    g1 = Graph()
    g1.initial_vision(msg_1)
    g1.get_agents(0)

