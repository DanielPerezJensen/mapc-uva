import json


class Node(object):
    """
    Create a node used in the graph and store information about its terrain
    and activity.
    """
    def __init__(self, location, terrain='empty', step=0, things={},
                 north=None, east=None, south=None, west=None):
        """
        Initialise the node and create attribute with default values.
        Terrain and step get combined into a tuple for easier use

        Arguments
        ---------
        location: (int, int)
            A tuple containing the x, y coordinate of the node relative to the
            graph's initial node.
        terrain: str
            The type of terrain (empty, obstacle, goal).
        step: int
            The step in which the node is created
        things: {step:thing}
            A dictionary containing a list of things (value) in the node
            (entities, blocks, dispensers, markers) on a certain step (key).
        north, east, south, west: Node
            The node to the corresponding direction of this node.
        """
        self.location = location
        self.terrain = (terrain, step)
        if things == {}:
            self.things = {}
        else:
            self.things = things
        self.directions = {
            'n': north,
            'e': east,
            's': south,
            'w': west
        }

    def __str__(self):
        """
        Convert the information from a node into a clear style to be printed.
        """
        node = f'Node object\n- Location : {self.location}\n'
        node += f'- Terrain  : {self.terrain[0]} (at step {self.terrain[1]})\n'
        if self.things == {}:
            node += '- Things   : None'
        else:
            node += '- Things   :'
            for i, thing in enumerate(sorted(self.things.items())):
                if i:
                    node += f'\n{" "*13}'
                    node += f'step {thing[0]}: {str(thing[1]).strip("[]")}'
                else:
                    node += f' step {thing[0]}: {str(thing[1]).strip("[]")}'

        for direction in self.directions.items():
            if direction[0] == 'n':
                if direction[1]:
                    node += f'\n- North    : {direction[1].get_location()}'
                else:
                    node += f'\n- North    : None'

            elif direction[0] == 'e':
                if direction[1]:
                    node += f'\n- East     : {direction[1].get_location()}'
                else:
                    node += f'\n- East     : None'

            elif direction[0] == 's':
                if direction[1]:
                    node += f'\n- South    : {direction[1].get_location()}'
                else:
                    node += f'\n- South    : None'

            elif direction[0] == 'w':
                if direction[1]:
                    node += f'\n- West     : {direction[1].get_location()}'
                else:
                    node += f'\n- West     : None'
        return node+'\n'

    def get_location(self):
        return self.location

    def set_location(self, location):
        """
        Change the location of a node.

        Arguments
        ---------
        location: (int, int)
        """
        self.location = location

    def get_terrain(self):
        return self.terrain

    def set_terrain(self, terrain, step):
        self.terrain = (terrain, step)

    def get_things(self, step=-1):
        """
        Return the things on a specific step.

        Arguments
        ---------
        step: int
            If step > 0, return list with things in that step
            (None if step doesn't exist). If no step is specified,
            return things dict as sorted list with (step, things) elements.
        """
        if step >= 0:
            if step in self.things.keys():
                return self.things[step]
            else:
                return []
        else:
            return sorted(self.things.items())

    def add_things(self, objects, step):
        """
        Add things to the node at a specific step and remove duplicates.

        Arguments
        ---------
        objects: tuple or list
            the objects can either be a single thing or a list of things.
        step: int
            The step on which the things need to be added.
        """
        if step in self.things:
            if isinstance(objects, list):
                self.things[step].extend(objects)
            elif isinstance(objects, tuple):
                self.things[step].append(objects)
        else:
            if isinstance(objects, list):
                self.things[step] = objects
            elif isinstance(objects, tuple):
                self.things[step] = [objects]

        self.things[step] = list(dict.fromkeys(self.things[step]))

    def get_direction(self, direction=None):
        """
        Return the node in the specified direction. If no direction is provided
        the current node is returned.

        Arguments
        ---------
        direction: str
            The direction of the requested node (n, e, s, w).
        """
        if direction:
            return self.directions[direction]
        else:
            return self

    def add_direction(self, north=None, east=None, south=None, west=None):
        """
        Add a node to the current node in a given direction.

        Arguments
        ---------
        nort, east, south, west: Node
        """
        if isinstance(north, Node):
            self.directions['n'] = north
        if isinstance(east, Node):
            self.directions['e'] = east
        if isinstance(south, Node):
            self.directions['s'] = south
        if isinstance(west, Node):
            self.directions['w'] = west

    def _is_obstacle(self):
        """
        Determine if a node is an obstacle block.
        Parameters
        ---------
        step: int
            Current game step.
        agent_location: (int, int)
            The location of the agent itself.
        """
        # check for obstacles
        if self.terrain[0] == 'obstacle':
            return True
        
        return False

    def _is_thing(self, step, agent_location, things=['block', 'entity']):
        """
        Determine if a node is a given thing.
        By default looking for blocks and entities.
        Parameters
        ---------
        step: int
            Current game step.
        agent_location: (int, int)
            The location of the agent itself.
        things: list of str
            List of things to include from {block, entity, dispenser, marker}.
        """
        
        if agent_location == self.location:
            return False

        # check for entities
        loc_things = self.get_things(step)
        for thing in loc_things:
            if thing[0] in things:
                return True
        return False


class Graph(object):
    """
    Create a graph used by the agents to help naviagate and store information
    about the environment.
    """
    def __init__(self):
        """
        Initialise the graph and create a dictionary to store the nodes based
        on the coordinates of the agents initial position (will acts as
        the (0, 0) coordinate) and add the neighbouring nodes to each node.
        The graph also saves the current step, current
        node and the start node (0, 0).
        """
        self.nodes = {}
        self.step = 0

        for x in range(-5, 6):
            for y in range(-5, 6):
                if abs(x) + abs(y) < 6:
                    self.nodes[(x, y)] = Node((x, y))

        self.root = self.nodes[(0, 0)]
        self.current = self.root
        self.next = self.root

        for node in self.nodes.values():
            x, y = node.location
            if (x, y-1) in self.nodes.keys():
                node.add_direction(north=self.nodes[(x, y-1)])
            if (x+1, y) in self.nodes.keys():
                node.add_direction(east=self.nodes[(x+1, y)])
            if (x, y+1) in self.nodes.keys():
                node.add_direction(south=self.nodes[(x, y+1)])
            if (x-1, y) in self.nodes.keys():
                node.add_direction(west=self.nodes[(x-1, y)])

    def __str__(self):
        """
        Convert the information from a graph into a clear style to be printed.
        """
        graph = f'Graph object\n- Current step     : {self.step}'
        graph += f'\n- Root location    : {self.root.location}'
        graph += f'\n- Current location : {self.current.location}'
        graph += f'\n- Next location    : {self.next.location}'
        graph += f'\n- Number of nodes  : {len(self.nodes.keys())}\n'
        return graph

    def update(self, msg):
        """
        Update the graph given the information in the message. The function
        adds new nodes if necessary, updates information and return
        lists of new obstacles, new empty space and new agents.

        Arguments
        ---------
        msg: dict
            The request-action message from the server.
        """
        self.update_step(msg['content']['step'])
        if agent_moved(msg):
            # update location
            prev_direction = msg['content']['percept']['lastActionParams'][0]
            # Failsafe incase new node doesn't exist.
            self.current = self.current.directions[prev_direction]

            for new_node in self.get_new_nodes(msg['content']['percept']
                                               ['lastActionParams'][0]):
                if new_node in self.nodes:
                    self.add_neighbours(self.nodes[new_node])
                else:
                    self.nodes[new_node] = Node(new_node, step=self.get_step())
                    self.add_neighbours(self.nodes[new_node])

        new_obstacles, new_empty = [], []
        step = self.get_step()
        vision = self.get_vision(msg)
        for node in self.get_local_nodes():
            if self.nodes[node].get_terrain()[0] == 'obstacle':
                if node not in vision or vision[node]['terrain'] == 'empty':
                    self.nodes[node].set_terrain('empty', step)
                    new_empty.append(node)

            if node in vision:
                if self.nodes[node].get_terrain()[0] == 'empty' and \
                        vision[node]['terrain'] == 'obstacle':
                    new_obstacles.append(node)

                self.nodes[node].set_terrain(vision[node]['terrain'], step)
                self.nodes[node].add_things(vision[node]['things'], step)

        return new_obstacles, new_empty, self.get_new_agents(vision)

    def update_step(self, step):
        self.step = step

    def add_neighbours(self, node):
        """
        Connect node to neighbouring nodes if necessary.
        """
        x, y = node.location
        if (x, y-1) in self.nodes and node.directions['n'] is None:
            node.add_direction(north=self.nodes[(x, y-1)])
            self.nodes[(x, y-1)].add_direction(south=node)

        if (x+1, y) in self.nodes and node.directions['e'] is None:
            node.add_direction(east=self.nodes[(x+1, y)])
            self.nodes[(x+1, y)].add_direction(west=node)

        if (x, y+1) in self.nodes and node.directions['s'] is None:
            node.add_direction(south=self.nodes[(x, y+1)])
            self.nodes[(x, y+1)].add_direction(north=node)

        if (x-1, y) in self.nodes and node.directions['w'] is None:
            node.add_direction(west=self.nodes[(x-1, y)])
            self.nodes[(x-1, y)].add_direction(east=node)

    def get_vision(self, msg):
        """
        Process the percept information from the message and create
        a dictionary.

        Arguments
        ---------
        msg: dict
            The message from which the information will be extracted.
        """
        vision = {}
        terrain = msg['content']['percept']['terrain']
        things = msg['content']['percept']['things']
        cx, cy = self.get_current().location

        for option in terrain:
            for x, y in terrain[option]:
                new_x, new_y = x + cx, y + cy
                if (new_x, new_y) in vision:
                    vision[(new_x, new_y)]['terrain'] = option
                else:
                    vision[(new_x, new_y)] = {'terrain': option, 'things': []}

        for thing in things:
            new_x, new_y = thing['x'] + cx, thing['y'] + cy
            if (new_x, new_y) in vision:
                vision[(new_x, new_y)]['things'].append((thing['type'],
                                                         thing['details']))
            else:
                vision[(new_x, new_y)] = {'terrain': 'empty',
                                          'things': [(thing['type'],
                                                      thing['details'])]}
        return vision

    def get_current(self):
        """
        Return the node of the agent's current location.
        """
        return self.current

    def get_next(self):
        """
        Return the node of the agent's next location.
        """
        return self.next

    def get_new_agents(self, vision):
        """
        Create a list with the locations on which there are currently now agent
        but not the previous step.

        Arguments
        ---------
        vision: dict
            The processed perceptual information from the server's
            request-action message.
        """
        # TODO: Add previous location to new agents.
        agents = []
        step = self.get_step()
        for node in vision:
            if node != self.current.get_location():
                for thing in vision[node]['things']:
                    if thing not in self.nodes[node].get_things(step - 1) and \
                            thing[0] == 'entity' and node not in agents:
                        agents.append(node)
        return agents

    def get_agents(self, step=0, team='A'):
        """
        Get the agents and location on a certain from a specific team.

        Arguments:
        step: int
            The step from which the agents are gathered.
        team: str
            The team can be either A or B.
        """
        agents = []
        for node in self.nodes:
            for thing in self.nodes[node].get_things(step):
                if thing[0] == 'entity' and thing[1] == team:
                    agents.append((node, thing))
        return agents

    def get_local_nodes(self):
        """
        Return the location of the nodes around the current node, within the
        vision of the agent.
        """
        cx, cy = self.get_current().location
        nodes = []
        for x in range(-5, 6):
            for y in range(-5, 6):
                if abs(x) + abs(y) < 6:
                    nodes.append((x + cx, y + cy))
        return nodes

    def get_new_nodes(self, direction):
        """
        Get coordinates of the new nodes relative to the root node.

        Arguments
        ---------
        direction: str
            The direction can either be n, e, s, w.
        """
        cx, cy = self.get_current().location
        nodes = []
        if direction == 'n':
            nodes = [(-5, 0), (-4, -1), (-3, -2), (-2, -3), (-1, -4), (0, -5),
                     (1, -4), (2, -3), (3, -2), (4, -1), (5, 0)]
        elif direction == 'e':
            nodes = [(0, -5), (1, -4), (2, -3), (3, -2), (4, -1), (5, 0),
                     (4, 1), (3, 2), (2, 3), (1, 4), (0, 5)]
        elif direction == 's':
            nodes = [(-5, 0), (-4, 1), (-3, 2), (-2, 3), (-1, 4), (0, 5),
                     (1, 4), (2, 3), (3, 2), (4, 1), (5, 0)]
        elif direction == 'w':
            nodes = [(0, -5), (-1, -4), (-2, -3), (-3, -2), (-4, -1), (-5, 0),
                     (-4, 1), (-3, 2), (-2, 3), (-1, 4), (0, 5)]

        for i, node in enumerate(nodes):
            nodes[i] = (node[0] + cx, node[1] + cy)

        return nodes

    def get_step(self):
        return self.step

    def get_direction(self, location):
        """
        Return the direction of the given location relative to
        the current location.

        Arguments
        ---------
        location: (int, int)
            The location of the given node, should be adjacent to
            the current location.
        """
        current = self.current.location
        if location[1] < current[1]:
            return 'n'
        elif location[0] > current[0]:
            return 'e'
        elif location[1] > current[1]:
            return 's'
        elif location[0] < current[0]:
            return 'w'
        else:
            return ''


def get_action_direction(action_msg):
    """
    Return the direction for the given move action.

    Arguments
    ---------
    action_msg: dict
        The action message for the server.
    """
    if action_msg and action_msg['content']['type'] == 'move':
        return action_msg['content']['p'][0]
    else:
        return ''


def agent_moved(msg):
    """
    Return True if the agent's last action was 'move' and it was successful.
    """
    if msg['content']['percept']['lastAction'] == 'move' and \
            msg['content']['percept']['lastActionResult'] == 'success':
        return True
    return False


def merge_graphs(g1, g2, offset):
    """
    Merge two graphs. The second graph (g2) will adopt the coordinate system from
    the first graph (g1).

    Arguments
    ---------
    g1, g2: Graph
        The graphs of the first and second agent, respectively.
    offset: (int, int)
        The location of the second agent from the perspective of the first.
    """
    g1_x, g1_y = g1.get_current().location
    g2_x, g2_y = g2.get_current().location

    rx, ry = g1_x + offset[0] - g2_x, g1_y + offset[1] - g2_y

    for x, y in g2.nodes:
        new_x, new_y = rx + x, ry + y
        if (new_x, new_y) in g1.nodes:
            # Get the most up-to-date terrain information
            if g1.nodes[(new_x, new_y)].get_terrain()[1] < \
                    g2.nodes[(x, y)].get_terrain()[1]:
                g2_terrain = g2.nodes[(x, y)].get_terrain()[0]
                g2_step = g2.nodes[(x, y)].get_terrain()[1]
                g1.nodes[(new_x, new_y)].set_terrain(g2_terrain, g2_step)

            for things in g2.nodes[(x, y)].get_things():
                g1.nodes[(new_x, new_y)].add_things(things[1], things[0])
        else:
            g1.nodes[(new_x, new_y)] = g2.nodes[(x, y)]
            g1.nodes[(new_x, new_y)].set_location((new_x, new_y))

            if (x, y-1) in g1.nodes:
                g1.nodes[(new_x, new_y)].add_direction(north=g1.nodes[(x, y-1)])
                g1.nodes[(x, y-1)].add_direction(south=g1.nodes[(new_x, new_y)])
            if (x+1, y) in g1.nodes:
                g1.nodes[(new_x, new_y)].add_direction(east=g1.nodes[(x+1, y)])
                g1.nodes[(x+1, y)].add_direction(west=g1.nodes[(new_x, new_y)])
            if (x, y+1) in g1.nodes:
                g1.nodes[(new_x, new_y)].add_direction(south=g1.nodes[(x, y+1)])
                g1.nodes[(x, y+1)].add_direction(north=g1.nodes[(new_x, new_y)])
            if (x-1, y) in g1.nodes:
                g1.nodes[(new_x, new_y)].add_direction(west=g1.nodes[(x-1, y)])
                g1.nodes[(x-1, y)].add_direction(east=g1.nodes[(new_x, new_y)])

    # g2 adopts the nodes from g1
    g2.nodes = g1.nodes

    # g2 changes its current and next node accordingly
    g2.current = g1.nodes[(rx + g2_x, ry + g2_y)]
    g2_x, g2_y = g2.get_next().location
    g2.next = g1.nodes[(rx + g2_x, ry + g2_y)]
    g2_x, g2_y = g2.root.location
    g2.root = g1.nodes[(rx + g2_x, ry + g2_y)]


if __name__ == '__main__':
    agent_0_step_0 = json.loads('{\
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

    agent_0_step_1 = json.loads('{\
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

    agent_2_step_0 = json.loads('{\
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

    agent_2_step_1 = json.loads('{\
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

    graph1 = Graph()
    graph1.update(agent_0_step_0)
    graph1.update(agent_0_step_1)

    graph2 = Graph()
    graph2.update(agent_2_step_0)
    graph2.update(agent_2_step_1)

    merge_graphs(graph1, graph2, (1, 2))

    print(graph1)
    print(graph1.nodes[(1, 0)])
    print(graph2)
    print(graph2.nodes[(1, 0)])
