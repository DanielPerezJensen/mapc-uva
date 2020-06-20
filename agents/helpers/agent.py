from collections import deque
from functools import partial
import heapq
import math

if __name__ == "__main__":
    from server import Server
    from graph import graph
else:
    from .server import Server
    from .graph import Graph


class Agent(Server):
    """
    Super class that can perform all primitive agent functionality
    """
    def __init__(self, user, pw, print_json=False):
        """
        Store some information about the agent and the socket so we can
        connect to the localhost.

        parameters
        ----------
        user: str
            The username of the agent.
        pw: str
            The password of the agent.
        print_json: bool
            If the communication jsons should be printed.
        """
        super().__init__(user, pw, print_json)
        self.last_action_move = None
        self.dstar = None
        self.steps = None
        self.beliefs = Graph(self._user_id)

    def get_location(self):
        return self.beliefs.get_current(self._user_id).location

    def nav_to(self, goal, agent_id, adjacent=False):
        """
        Navigate to coordinates in the agents local reference frame.
        The first call to nav_to does not require new_obs.

        parameters
        ----------
        goal: tuple
            x and y coordinates of the goal location.
        agent_id: int
            id of the agent.
        adjacent: bool
            If True, navigates to a block next to the goal location,
            e.g. for dispensers, taskboards etc.

        Returns the action.
        If at goal location or no path is possible, returns None.
        """
        goal = self.beliefs.modulate(goal)
        # Initialize or update
        if not self.dstar or self.dstar.goal != goal:
            self.dstar = DStarLite(self.beliefs, goal, agent_id)
        else:
            self.dstar.update(self.beliefs)

        # Get the new direction
        new_loc = self.dstar.move_to_goal()

        # Check if path is impossible or already at goal location
        if not new_loc:
            return None

        # Check if next to goal location
        if adjacent and new_loc == goal:
            return None

        curr_loc = self.beliefs.get_current(agent_id).location

        direction = self.beliefs.get_direction(agent_id, new_loc)

        if self.beliefs.nodes[new_loc]._is_obstacle():
            clear_pos_x = (new_loc[0] - curr_loc[0]) * 2
            clear_pos_y = (new_loc[1] - curr_loc[1]) * 2
            # Clear obstacle (invert flag because nav_to requires multiple
            action = self.clear(clear_pos_x, clear_pos_y)
            return action
        else:
            # Move to location (invert flag because nav_to requires
            # multiple moves)
            action = self.move(direction)
            return action

    def quit_nav(self):
        """
        Stops and resets the current navigation.
        """
        self.steps, self.dstar = None, None

    def skip(self):
        """
        Skip a turn for the agent.
        """

        self.last_action_move = ""

        # Create and return the request
        return self._create_action("skip")

    def move(self, direction):
        """
        Moves the agent in the specified direction.

        parameters
        ----------
        direction: str
            One of {n,s,e,w}, representing the direction the agent wants to
            move in.
        """

        self.last_action_move = direction

        # Create and return the request.
        return self._create_action("move", direction)

    def attach(self, direction):
        """
        Attaches something to the agent.
        Note: the agent has to be directly next to it.

        parameters
        ----------
        direction: str
            One of {n,s,e,w}, representing the direction to the thing the agent
            wants to attach.
        """

        self.last_action_move = ""

        # Create and return the request.
        return self._create_action("attach", direction)

    def detach(self, direction):
        """
        Detaches something from the agent.
        Note: only the connection between the agent and the thing is released.

        parameters
        ----------
        direction: str
            One of {n,s,e,w}, representing the direction to the thing the agent
            wants to detach from.
        """

        self.last_action_move = ""

        # Create and return the request.
        return self._create_action("detach", direction)

    def rotate(self, direction):
        """
        Rotates the agent (and all attached things) 90 degrees in the given
        direction.

        parameters
        ----------
        direction: str
            One of {cw, ccw}, representing the rotation direction
            (clockwise or counterclockwise).
        """

        self.last_action_move = ""

        # Create and return the request.
        return self._create_action("rotate", direction)

    def connect(self, agent, x, y):
        """
        Two agents can use this action to connect things attached to them.

        parameters
        ----------
        agent: str
            The agent to cooperate with.
        x: int or str
            The relative x position of the thing
        y: int or str
            The relative y position of the thing
        """

        self.last_action_move = ""

        # Create and return the request.
        return self._create_action("connect", agent, str(x), str(y))

    def disconnect(self, x1, y1, x2, y2):
        """
        Disconnects two attachments (probably blocks) of the agent.

        parameters
        ----------
        x1: int or str
            The relative x position of the first attachment.
        y1: int or str
             The relative y position of the first attachment.
        x2: int or str
            The relative x position of the second attachment.
        y2: int or str
            The relative y position of the second attachment.
        """

        self.last_action_move = ""

        # Create and return the request.
        return self._create_action("disconnect", str(x1), str(y1),
                                   str(x2), str(y2))

    def request(self, direction):
        """
        Requests a new block from a dispenser.
        Note: the agent has to be in a cell adjacent to the dispenser
        and specify the direction to it.

        parameters
        ----------
        direction: str
            One of {n,s,e,w}, representing the direction to the position of
            the dispenser to use.
        """

        self.last_action_move = ""

        # Create and return the request.
        return self._create_action("request", direction)

    def submit(self, task):
        """
        Submit the pattern of things that are attached to the agent to
        complete a task.

        parameters
        ----------
        task: str
            The name of an active task.
        """

        self.last_action_move = ""

        # Create and return the request.
        return self._create_action("submit", task)

    def clear(self, x, y):
        """
        Prepare to clear an area (a target position and the 4 adjacent cells).
        Note: The area is cleared after a number of consecutive
              successful clear actions for the same target position.
        Note: The action consumes a fixed amount of energy.

        parameters
        ----------
        x: int or str
            The relative x position of the target position.
        y: int or str
            The relative y position of the target position.
        """

        self.last_action_move = ""

        # Create and return the request.
        return self._create_action("clear", x, y)

    def accept(self, task):
        """
        Submit the pattern of things that are attached to the agent to
            complete a task.
        Note: The area is cleared after a number of consecutive successful
              clear actions for the same target position.
        Note: The action consumes a fixed amount of energy.

        parameters
        ----------
        task: str
            The name of the task to accept.
        """

        self.last_action_move = ""

        # Create and return the request.
        return self._create_action("accept", task)

    # Helper functions
    @staticmethod
    def _create_action(action_type, *p):
        """
        Returns an action message.

        parameters
        ----------
        action_type: str
            The type of action to use.
        p: str
            Parameters for the action.
        """
        # Create the action.
        action = {
            "type": "action",
            "content": {
                "id": "",
                "type": action_type,
                "p": list(p)
            }
        }
        # Return the action.
        return action


class DStarLite(object):
    def __init__(self, beliefs, goal, agent_id):
        """
        Find the path to the goal location from the current position

        parameters
        ----------
        beliefs: object
            Instance of the current beliefs
        goal: tuple
            Goal x and y coordinates
        """

        # Init the beliefs
        self.beliefs = beliefs
        self.obstacle_cost = 32 * math.e ** (-0.008 * self.beliefs.energy)

        self.back_pointers = {}
        self.G_VALS = {}
        self.RHS_VALS = {}
        self.Km = 0
        self.agent_id = agent_id
        self.position = beliefs.get_current(agent_id).location
        self.goal = goal
        self.queue = PriorityQueue()
        self.queue.put(self.goal, self.calculate_key(self.goal))
        self.back_pointers[self.goal] = None

        # Create initial path to goal
        self.compute_shortest_path()

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

        curr_loc = self.beliefs.get_current(self.agent_id).location

        attached_locs = [(curr_loc[0] + att[0], curr_loc[1] + att[1]) for att
                         in self.beliefs.attached]

        for node in [from_node, to_node]:
            if node in self.beliefs.nodes and \
                    self.beliefs.nodes[node]._is_thing(self.beliefs.step,
                                                       curr_loc,
                                                       attached_locs):
                return float('inf')

        if len(self.beliefs.attached):
            if to_node in self.beliefs.nodes and \
                    self.beliefs.nodes[to_node]._is_exp_obstacle():
                return float('inf')
        else:
            if to_node in self.beliefs.nodes and \
                    self.beliefs.nodes[to_node]._is_obstacle():
                return 32 * math.e ** (-0.008 * self.beliefs.energy)

        return 1

    def neighbors(self, id):
        (x, y) = id
        results = [(x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)]
        if (x + y) % 2 == 0:
            results.reverse()  # aesthetics
        return [self.beliefs.modulate(coords) for coords in results]

    def calculate_rhs(self, node):
        lowest_cost_neighbour = self.lowest_cost_neighbour(node)
        self.back_pointers[node] = lowest_cost_neighbour
        return self.lookahead_cost(node, lowest_cost_neighbour)

    def lookahead_cost(self, node, neighbour):
        return self.g(neighbour) + self.transition_cost(neighbour, node)

    def lowest_cost_neighbour(self, node):
        cost = partial(self.lookahead_cost, node)
        neighbors = self.neighbors(node)
        min_cost = min(neighbors, key=cost)
        return min_cost

    def g(self, node):
        return self.G_VALS.get(node, float('inf'))

    def rhs(self, node):
        if node != self.goal:
            return self.RHS_VALS.get(node, float('inf'))
        return 0

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
        while len(self.queue.elements) and \
                (self.queue.first_key() < self.calculate_key(self.position) or
                 self.rhs(self.position) != self.g(self.position)):
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
        self.goal = self.beliefs.modulate(self.goal)
        if self.position != self.goal:
            if self.g(self.position) == float('inf'):
                return None

            self.last_node = self.beliefs.get_current(self.agent_id).location

            # return the next step to be taken
            return self.lowest_cost_neighbour(self.position)
        else:
            return None

    def update(self, beliefs):
        """
        Update the path if necessary.

        parameters
        ----------
        beliefs: object
            The updated beliefs instance.
        """
        # Update observations
        self.goal = self.beliefs.modulate(self.goal)
        self.beliefs = beliefs
        self.obstacle_cost = 32 * math.e ** (-0.008 * self.beliefs.energy)
        self.position = beliefs.get_current(self.agent_id).location
        new_obs = [obs for sublist in beliefs.new_obs.values()
                   for obs in sublist]

        # Update the path if there are new observations
        if new_obs:
            self.Km += self.heuristic(self.last_node, self.position)
            attached_locs = [(self.position[0] + att[0], self.position[1] +
                             att[1]) for att in self.beliefs.attached]
            self.update_nodes({node for obs in new_obs
                              for node in self.neighbors(obs)
                              if (node not in self.beliefs.nodes or not
                                  self.beliefs.nodes[node]._is_thing(
                                      self.beliefs.step, self.position,
                                      attached_locs))})

            self.compute_shortest_path()


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def pop(self):
        item = heapq.heappop(self.elements)
        return item[1]

    def first_key(self):
        return heapq.nsmallest(1, self.elements)[0][0]

    def delete(self, node):
        self.elements = [e for e in self.elements if e[1] != node]
        heapq.heapify(self.elements)

    def __iter__(self):
        for _, node in self.elements:
            yield node


if __name__ == "__main__":
    agent = Agent("agentA0", "1", True)

    # while True:
    msg = agent.receive_msg()
