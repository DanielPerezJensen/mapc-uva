from .helpers import Server
from .helpers.graph import Graph
from .helpers.graph import merge_graphs

from queue import Queue
import threading


class Strategist(Server):
    """
    The strategist agent uses game information to decide which agent plays
    what role.
    """
    def __init__(self, user, queue, print_json=False):
        """
        Initialize the stratagist as a child of the server. Add an input_queue,
        which is used for task from the agents to the strategist, and an
        output_queue, which is used for tasks from the strategist to the
        agents.

        Arguments
        ----------
        user: str
            The username of the agent.
        pw: str
            The password of the agent.
        queue: (Queue, Queue)
            A tuple containing both the input and output queue. The size of
            both queues is equal the the number of agents playing.
        print_json: bool
            If the communication jsons should be printed.
        """
        super().__init__(user, print_json)
        self.input_queue = queue[0]
        self.output_queue = queue[1]
        print(f'\033[1;34m{self._user}\033[0;0m running')

    def run(self):
        """
        The function that runs the strategist.
        """
        lock = threading.Lock()
        while True:
            task = self.peek_queue()
            if task == 'update':
                if self.input_queue.full():
                    print(f'Number of graphs: {self.get_number_graphs()}')
                    x = self.get_agent(1).beliefs
                    print(f'Width: {x.width}\nHeight: {x.height}')
                    while not self.input_queue.empty():
                        task, agent = self.input_queue.get()
                        self.input_queue.task_done()

            elif task == 'print':
                print(agent.name)
                self.input_queue.task_done()

            elif task == 'merge':
                task, agent = self.input_queue.get()
                potential_agents = self.identifying_agents(agent)
                self.merge_agent_graphs(agent, potential_agents)
                self.input_queue.task_done()

    def peek_queue(self):
        """
        Identify task and return item to queue. Returns the task as a str.
        """
        if not self.input_queue.empty():
            task, agent = self.input_queue.get()
            self.input_queue.task_done()
            self.input_queue.put((task, agent))
            return task
        return ''

    def identifying_agents(self, main_agent, agent_name=False):
        """
        Determine the identities of the agents in the main agent's local
        vision.

        Arguments
        ---------
        main_agent: SuperAgent
            The agent who wants to identify the other agents within its vision.
        agent_ID: boolean
            If True, the agent IDs are returned in potential agents instead
            of the agent objects.
        """
        potential_agents = {}
        main_local_agents = main_agent.beliefs.get_local_agents(main_agent.
                                                                _user_id)

        for agent in self.get_agents(main_agent.name):
            local_agents = [(-x, -y) for (x, y) in
                            agent.beliefs.get_local_agents(agent._user_id)]
            for location in main_local_agents:
                if location in local_agents:
                    if location in potential_agents.keys():
                        potential_agents[location].append(agent)
                    else:
                        potential_agents[location] = [agent]

        potential_agents = self.eliminate_agents(main_agent, potential_agents)
        if agent_name:
            for location in potential_agents:
                potential_agents[location] = [agent.name for agent in
                                              potential_agents[location]]
        return potential_agents

    def eliminate_agents(self, main_agent, potential_agents):
        """
        Eliminate potential agents based on the information their intersecting
        nodes hold.

        Arguments
        ---------
        main_agent: SuperAgent
            The agent who wants to identify the other agents within its vision.
        potential_agents: dict
            A dictionary where each key is a location and each value is a list
            containing potential agents in that location.
        """
        main_local_nodes = main_agent.beliefs.get_local_nodes(main_agent.
                                                              _user_id,
                                                              offset=(0, 0))
        main_current_node = main_agent.beliefs.get_current(main_agent.
                                                           _user_id).location
        for location in potential_agents:
            new_list = potential_agents[location][:]
            intersect = [(x + location[0], y + location[1]) for (x, y) in
                         main_local_nodes if (x + location[0], y + location[1])
                         in main_local_nodes]

            for agent in potential_agents[location]:
                agent_current_node = agent.beliefs.\
                    get_current(agent._user_id).location
                for node in intersect:
                    # node + current location
                    main_agent_node = (node[0] + main_current_node[0],
                                       node[1] + main_current_node[1])

                    # node - location + current location
                    agent_node = (node[0]-location[0] + agent_current_node[0],
                                  node[1]-location[1] + agent_current_node[1])

                    if not self._compare_nodes(main_agent.beliefs.
                                               nodes[main_agent_node],
                                               agent.beliefs.nodes[agent_node],
                                               main_agent.beliefs.get_step()):
                        new_list.remove(agent)
                        break

            potential_agents[location] = new_list

        return potential_agents

    def merge_agent_graphs(self, main_agent, potential_agents):
        """
        If the agent identified the other agent they will merge their graphs.

        Arguments
        ---------
        main_agent: SuperAgent
            The agent who wants to identify the other agents within its vision.
        potential_agents: dict
            A dictionary where each key is a location and each value is a list
            containing potential agents in that location.
        """
        for location, agent in potential_agents.items():
            if len(agent) == 1:
                agent = agent[0]
                if agent._user_id not in main_agent.beliefs.current.keys():
                    if main_agent._user_id < agent._user_id:
                        new_graph = merge_graphs(main_agent.beliefs,
                                                 main_agent._user_id,
                                                 agent.beliefs,
                                                 agent._user_id,
                                                 location)
                        print(f'{agent._user} merged with {main_agent._user}')
                    else:
                        new_graph = merge_graphs(agent.beliefs,
                                                 agent._user_id,
                                                 main_agent.beliefs,
                                                 main_agent._user_id,
                                                 (-location[0], -location[1]))
                        print(f'{main_agent._user} merged with {agent._user}')

                    for agent in new_graph.current:
                        self.get_agent(agent).beliefs = new_graph

                else:
                    self.calculate_dimensions(main_agent, agent, location)

    def calculate_dimensions(self, main_agent, agent, location):
        location = list(location)
        main_location = main_agent.beliefs.\
            get_current(main_agent._user_id).location
        agent_location = agent.beliefs.\
            get_current(agent._user_id).location

        if main_location[0] + location[0] != agent_location[0]:
            if main_location[0] <= 0:
                location[0] = -location[0]

            width = abs(main_location[0]) + location[0] + \
                abs(agent_location[0])

            if not main_agent.beliefs.width or \
                    main_agent.beliefs.width/width == \
                    round(main_agent.beliefs.width/width):
                self.apply_dimensions(width=width)

        if main_location[1] + location[1] != agent_location[1]:
            if main_location[1] <= 0:
                location[1] = -location[1]

            height = abs(main_location[1]) + location[1] + \
                abs(agent_location[1])

            if not main_agent.beliefs.height or \
                    main_agent.beliefs.height/height == \
                    round(main_agent.beliefs.height/height):
                self.apply_dimensions(height=height)

    def apply_dimensions(self, width=0, height=0):
        for agent in self.get_agents():
            if width != 0 and not agent.beliefs.width:
                print(f'Width of {width} applied')
                agent.beliefs.width = width
            if height != 0 and not agent.beliefs.height:
                print(f'Height of {height} applied')
                agent.beliefs.height = height
            agent.beliefs.apply_dimensions_to_graph()

    def get_number_graphs(self):
        """
        Returns the total number of graphs used by all the agents combined.
        """
        agents = [agent._user_id for agent in self.get_agents()]
        pairs = []
        while agents != []:
            temp = list(self.get_agent(agents[0]).beliefs.current.keys())
            pairs.append(temp)
            agents = [x for x in agents if x not in temp]
        return len(pairs)

    def get_agents(self, name=''):
        """
        Return a list of all active agents/threads.
        (Minus the MainThread and the Strategist).

        Arguments
        ---------
        name: str
            The name of the agent which will not be returned. Default is ''
        """
        ex = ['MainThread', 'Strategist', name]
        agents = [thread for thread in threading.enumerate() if thread.name
                  not in ex]
        return agents

    def get_agent(self, name):
        """
        Return the agent object given the agent's name or user_id.

        Arguments
        ---------
        name: str or int
            The name or user_id of the agent.
        """
        agents = self.get_agents()
        if isinstance(name, str):
            agent = [thread for thread in agents if thread.name == name]
            if agent:
                return agent[0]
        elif isinstance(name, int):
            agent = [thread for thread in agents if thread._user_id == name]
            if agent:
                return agent[0]
        return False

    @staticmethod
    def _compare_nodes(node_1, node_2, step):
        """
        Compare two nodes based of their information about the terrain and
        things.

        Arguments
        ---------
        node_1, node_2: Node
            The nodes in question
        step: int
            The current game step (used when comparing things).
        """
        if node_1.get_terrain()[0] != node_2.get_terrain()[0]:
            return False
        if set(node_1.get_things(step)) != set(node_2.get_things(step)):
            return False
        return True


if __name__ == "__main__":
    input_queue, output_queue = Queue(maxsize=0), Queue(maxsize=0)
    strategist = Strategist(f"Strategist", [input_queue, output_queue])
    strategist.start()
