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
        location: tuple(int, int)
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
        """
        Return the location of the node as a tuple (int, int).
        """
        return self.location

    def set_location(self, location):
        """
        Change the location of a node.

        Arguments
        ---------
        location: tuple(int, int)
        """
        self.location = location

    def get_terrain(self):
        """
        Return the terrain of a node as a tuple (str, int), where the first
        element is the type of terrain and the second is the step in which
        the terrain was changed.
        """
        return self.terrain

    def set_terrain(self, terrain, step):
        self.terrain = (terrain, step)

    def get_things(self, step=-1):
        """
        Return the all the things in a node on a specific step.
        If a step is given, return a list of tuples where the first element of
        the tuple is the type of thing and the second is a detail of the thing.

        If no step is given, all things from every step are returned as a list
        of tuples. Where the first element is the step and the second is the
        list of things from that step.

        Arguments
        ---------
        step: int
            The step from which the information will be returned.
            Default is -1.
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
        Add things to the node at a specific step and store it in a list.
        It also removes any duplicates.

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

    def get_direction(self, width=None, height=None, direction=None):
        """
        Return the node in the specified direction. If no direction is provided
        the current node is returned.

        Arguments
        ---------
        direction: str
            The direction of the requested node (n, e, s, w).
        """
        x, y = self.location
        if direction:
            if self.directions[direction]:
                return self.directions[direction].location

            elif height:
                if direction == 'n':
                    if y == 0:
                        return (x, height - 1)
                    return (x, y-1)
                if direction == 's':
                    if y == height - 1:
                        return (x, 0)
                    return (x, y+1)

            elif width:
                if direction == 'w':
                    if x == 0:
                        return (width - 1, y)
                    return (x-1, y)
                if direction == 'e':
                    if x == width - 1:
                        return (0, y)
                    return (x+1, y)

        else:
            return [self.get_direction(width=width, height=height, direction='n'),
                    self.get_direction(width=width, height=height, direction='e'),
                    self.get_direction(width=width, height=height, direction='s'),
                    self.get_direction(width=width, height=height, direction='w')]

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
    def __init__(self, agent_id):
        """
        Initialise the graph and create a dictionary to store the nodes based
        on the coordinates of the agents initial position (will acts as
        the (0, 0) coordinate) and add the neighbouring nodes to each node.
        The graph also saves the current step, current node and the
        start node (0, 0).
        """
        self.nodes = {}
        self.step = 0
        self.width = None
        self.height = None

        for x in range(-5, 6):
            for y in range(-5, 6):
                if abs(x) + abs(y) < 6:
                    self.nodes[self.modulate((x, y))] = Node(self.modulate((x, y)))

        self.current = {agent_id: self.nodes[(0, 0)]}
        self.things = {'goals': [], 'dispensers': {}, 'taskboards': []}

        for node in self.nodes.values():
            x, y = node.location
            if self.modulate((x, y-1)) in self.nodes.keys():
                node.add_direction(north=self.nodes[self.modulate((x, y-1))])
            if self.modulate((x+1, y)) in self.nodes.keys():
                node.add_direction(east=self.nodes[self.modulate((x+1, y))])
            if self.modulate((x, y+1)) in self.nodes.keys():
                node.add_direction(south=self.nodes[self.modulate((x, y+1))])
            if self.modulate((x-1, y)) in self.nodes.keys():
                node.add_direction(west=self.nodes[self.modulate((x-1, y))])

    def __str__(self):
        """
        Convert the information from a graph into a clear style to be printed.
        """
        graph = f'Graph object\n- Current step     : {self.step}'
        graph += f'\n- Current location :'
        for i, agent in enumerate(self.current):
            if i:
                graph += f'\n{" "*20} Agent{agent} --> ' + \
                         f'{self.current[agent].location}'
            else:
                graph += f' Agent{agent} --> {self.current[agent].location}'
        graph += f'\n- Number of nodes  : {len(self.nodes.keys())}\n'
        return graph

    def update(self, msg, agent_id):
        """
        Update the graph given the information in the message. The function
        adds new nodes if necessary, updates information and return
        lists of newly added obstacles, spaces that used to be obstacles but
        are now empty and new agents.

        Arguments
        ---------
        msg: dict
            The request-action message from the server.
        agent_id: int
            The id of the agent. Used to know which nodes and current node
            need to be changed.
        """
        self.update_current(msg, agent_id)
        self.update_step(msg['content']['step'])
        if agent_moved(msg):
            for new_node in self.get_new_nodes(msg, agent_id):
                if new_node in self.nodes:
                    self.add_neighbours(self.nodes[new_node])
                else:
                    self.nodes[new_node] = Node(new_node, step=self.get_step())
                    self.add_neighbours(self.nodes[new_node])

        new_obstacles, new_empty = [], []
        step = self.get_step()
        vision = self.get_vision(msg, agent_id)
        for node in self.get_local_nodes(agent_id):
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

        return new_obstacles, new_empty, self.get_new_agents(vision, agent_id)

    def update_current(self, msg, agent_id):
        """
        Update the agent's current location based on the previous action.

        Arguments
        ---------
        msg: dict
            The request-action message from the server.
        """
        if agent_moved(msg):
            prev_direction = msg['content']['percept']['lastActionParams'][0]
            # Failsafe incase new node doesn't exist.
            self.current[agent_id] = self.current[agent_id].directions[prev_direction]

    def update_step(self, step):
        """
        Update the step. The graph contains the current step so that it can be
        used by graph functions.
        """
        self.step = step

    def add_neighbours(self, node):
        """
        Connect node to neighbouring nodes if it doesn't already have a node in
        that direction.
        """
        x, y = node.location
        if self.modulate((x, y-1)) in self.nodes and node.directions['n'] is None:
            node.add_direction(north=self.nodes[self.modulate((x, y-1))])
            self.nodes[self.modulate((x, y-1))].add_direction(south=node)

        if self.modulate((x+1, y)) in self.nodes and node.directions['e'] is None:
            node.add_direction(east=self.nodes[self.modulate((x+1, y))])
            self.nodes[self.modulate((x+1, y))].add_direction(west=node)

        if self.modulate((x, y+1)) in self.nodes and node.directions['s'] is None:
            node.add_direction(south=self.nodes[self.modulate((x, y+1))])
            self.nodes[self.modulate((x, y+1))].add_direction(north=node)

        if self.modulate((x-1, y)) in self.nodes and node.directions['w'] is None:
            node.add_direction(west=self.nodes[self.modulate((x-1, y))])
            self.nodes[self.modulate((x-1, y))].add_direction(east=node)

    def get_vision(self, msg, agent_id):
        """
        Process the percept information from the message and create
        a dictionary.
        Return a dictionary where, the keys are the coordinates of the nodes
        where there is either a thing or a non-empty terrain type. The values
        are a nested dictionary, where the keys are 'terrain' (containing the
        type of terrain) and 'things' which contains a list of
        tuples (thing type, thing detail).

        Arguments
        ---------
        msg: dict
            The message from which the information will be extracted.
        agent_id: int
            The id of the agent.
        """
        vision = {}
        terrain = msg['content']['percept']['terrain']
        things = msg['content']['percept']['things']
        cx, cy = self.get_current(agent_id).location

        for option in terrain:
            for x, y in terrain[option]:
                new_x, new_y = x + cx, y + cy

                if option == "goal":
                    if (new_x, new_y) not in self.things['goals']:
                        self.things['goals'].append((new_x, new_y))

                if (new_x, new_y) in vision:
                    vision[(new_x, new_y)]['terrain'] = option
                else:
                    vision[(new_x, new_y)] = {'terrain': option, 'things': []}

        for thing in things:
            new_x, new_y = thing['x'] + cx, thing['y'] + cy

            if thing['type'] == 'taskboard':
                if (new_x, new_y) not in self.things['taskboards']:
                    self.things['taskboards'].append((new_x, new_y))
            elif thing['type'] == 'dispensers':
                if thing['details'] not in self.things['dispensers']:
                    self.things['dispensers'][thing['details']] = [(new_x, new_y)]
                elif (new_x, new_y) not in self.things['dispensers'][thing['details']]:
                    self.things['dispensers'][thing['details']].append((new_x, new_y))

            if (new_x, new_y) in vision:
                vision[(new_x, new_y)]['things'].append((thing['type'],
                                                         thing['details']))
            else:
                vision[(new_x, new_y)] = {'terrain': 'empty',
                                          'things': [(thing['type'],
                                                      thing['details'])]}
        return vision

    def get_current(self, agent_id):
        """
        Return the node of the agent's current location.
        """
        return self.current[agent_id]

    def get_new_agents(self, vision, agent_id):
        """
        Create a list with the locations on which there are currently now agent
        but not the previous step.

        Returns a list of the coordinates.

        Arguments
        ---------
        vision: dict
            The processed perceptual information from the server's
            request-action message.
        agent_id: int
            The id of the agent.
        """
        agents = []
        step = self.get_step()
        for node in vision:
            if node != self.current[agent_id].get_location():
                for thing in vision[node]['things']:
                    node = self.modulate(node)
                    if thing not in self.nodes[node].get_things(step - 1) and \
                            thing[0] == 'entity' and node not in agents:
                        agents.append(node)
        return agents

    def get_agents(self, step=0, team='A'):
        """
        Get the agents and location on a certain step from a specific team.

        Arguments:
        step: intagent_
            The step from which the agents are collected.
        team: str
            The team can be either A or B.
        """
        agents = []
        for node in self.nodes:
            node = self.modulate(node)
            for thing in self.nodes[node].get_things(step):
                if thing[0] == 'entity' and thing[1] == team:
                    agents.append((node, thing))
        return agents

    def get_local_nodes(self, agent_id, offset=None):
        """
        Return the location of the nodes around within the agent's local vision.
        By default the coordinates are create with respect to the agent's
        current location. This can be changed by changing the offset.
        Returns a list of tuple coordinates.

        Arguments
        ---------
        offset: tuple(int, int)

        """
        if offset:
            cx, cy = offset
        else:
            cx, cy = self.get_current(agent_id).location
        nodes = []
        for x in range(-5, 6):
            for y in range(-5, 6):
                if abs(x) + abs(y) < 6:
                    nodes.append((self.modulate((x + cx, y + cy))))
        return nodes

    def get_local_agents(self, agent_id, team='A'):
        """
        Return the location of the agents from a certain team within
        the agent's own local vision.

        Return a list of tuple coordinates.

        Arguments
        ---------
        team: str
            The team's name.
        """
        local_agents = []
        cx, cy = self.get_current(agent_id).location
        for node in self.get_local_nodes(agent_id, offset=(0, 0)):
            if node != (0, 0):
                real_node = self.modulate((node[0] + cx, node[1] + cy))
                for thing in self.nodes[real_node].get_things(step=self.step):
                    if thing[0] == 'entity' and thing[1] == team:
                        local_agents.append(node)
        return local_agents

    def get_local_things(self, agent_id):
        """
        Return the location and things of the nodes in the agent's local vision.
        The returned item is a list of tuples. The tuples contain the
        coordinates of the thing relative to the agent and the things
        themselves, respectively.
        """
        local_things = []
        cx, cy = self.get_current(agent_id).location
        for node in self.get_local_nodes(agent_id, offset=(0, 0)):
            real_node = self.modulate((node[0] + cx, node[1] + cy))
            local_things.append((node, self.nodes[real_node].get_things(step=self.step)))
        return local_things

    def get_new_nodes(self, msg, agent_id):
        """
        Get coordinates of the new nodes relative to the root node.

        Return a list of tuple coordinates.

        Arguments
        ---------
        direction: str
            The direction can either be n, e, s, w.
        """
        direction = msg['content']['percept']['lastActionParams'][0]
        cx, cy = self.get_current(agent_id).location
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
            nodes[i] = self.modulate((node[0] + cx, node[1] + cy))

        return nodes

    def get_step(self):
        return self.step

    def get_direction(self, agent_id, location):
        """
        Return the direction of the given location relative to
        the agent's current location.

        Arguments
        ---------
        location: (int, int)
            The location of the given node, should be adjacent to
            the current location.
        """
        current = self.get_current(agent_id).location
        if self.width:
            if current[0] == 0 and location[0] == self.width-1:
                return 'w'
            elif current[0] == self.width-1 and location[0] == 0:
                return 'e'

        if self.height:
            if current[1] == 0 and location[1] == self.height-1:
                return 'n'
            elif current[1] == self.height-1 and location[1] == 0:
                return 's'

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

    def modulate(self, location):
        """
        Apply the width and height of the map as a modulo on the location
        values. Does nothing if no width or height have been set yet.

        Arguments
        ---------
        coordinates: (int, int)
            The location of the given node.
        """
        x, y = location
        if self.width:
            x = x % self.width
        if self.height:
            y = y % self.height
        return (x, y)

    def modulate_graph(self, width, height):
        """
        Apply the width and height of the map as a modulo to every node in the
        graph and update/add nodes where neccessary.
        """
        self.width = width
        self.height = height

        for node in self.nodes:
            if self.modulate(node) in self.nodes:
                if node != self.modulate(node):
                    if self.nodes[node].get_terrain()[1] > \
                            self.nodes[self.modulate(node)].get_terrain()[1]:
                        self.nodes[self.modulate(node)].set_terrain(self.nodes[node].get_terrain()[0],
                                                                    self.nodes[node].get_terrain()[1])

                    for things in self.nodes[node].get_things():
                        self.nodes[self.modulate(node)].add_things(things[0], things[1])
            else:
                self.nodes[self.modulate(node)] = Node(self.modulate(node),
                                                       terrain=self.nodes[node].get_terrain()[0],
                                                       step=self.nodes[node].get_terrain()[1])

                for things in self.nodes[node].get_things():
                    self.nodes[self.modulate(node)].add_things(things[0], things[1])

        for agent, node in self.current.items():
            self.current[agent] = self.nodes[self.modulate(node.get_location())]

        for node in self.nodes:
            self.add_neighbours(self.nodes[node])


def agent_moved(msg):
    """
    Return True if the agent's last action was 'move' and it was successful.
    """
    if msg['content']['percept']['lastAction'] == 'move' and \
            msg['content']['percept']['lastActionResult'] == 'success':
        return True
    return False


def merge_graphs(g1, agent1, g2, agent2, offset):
    """
    Merge two graphs. The second graph (g2) will adopt the coordinate system from
    the first graph (g1).

    Arguments
    ---------
    g1, g2: Graph
        The graphs of the first and second agent, respectively.
    agent1, agent2: SuperAgent
        The id's of the two agent to which g1 and g2 belong respectively.
    offset: (int, int)
        The location of the second agent from the perspective of the first.
    """
    g1_x, g1_y = g1.get_current(agent1).location
    g2_x, g2_y = g2.get_current(agent2).location

    rx, ry = g1_x + offset[0] - g2_x, g1_y + offset[1] - g2_y

    for x, y in g2.nodes:
        new_x, new_y = g1.modulate((rx + x, ry + y))
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

    for agent in g2.current:
        temp = g2.get_current(agent).location
        g1.current[agent] = g1.nodes[g1.modulate((rx + temp[0], ry + temp[1]))]

    for thing in g2.things:
        if thing == 'dispensers':
            for block in g2.things[thing]:
                for x, y in g2.things[thing][block]:
                    new_x, new_y = rx + x, ry + y
                    if (new_x, new_y) not in g1.things['dispensers'][block]:
                        g1.things['dispensers'][block].append((new_x, new_y))
        else:
            for x, y in g2.things[thing]:
                new_x, new_y = rx + x, ry + y
                if (new_x, new_y) not in g1.things[thing]:
                    g1.things[thing].append((new_x, new_y))

    return g1


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
                    "obstacle":[[0,3],[1,4],[-1,3],[0,4],[-2,3],[-1,4],[0,5],\
                        [5,0],[4,1]]},\
                "lastActionResult":"success",\
                "tasks":[],\
                "energy":300},\
            "deadline":1587837763855}}')

    graph1 = Graph(0)
    graph1.update(agent_0_step_0, 0)
    graph1.update(agent_0_step_1, 0)

    graph2 = Graph(2)
    graph2.update(agent_2_step_0, 2)
    graph2.update(agent_2_step_1, 2)

    graph2 = merge_graphs(graph1, 0, graph2, 2, (1, 2))
    print(graph2)
