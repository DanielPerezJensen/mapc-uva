from .helpers import Server
from .helpers.graph import Graph
from queue import Queue
import threading
import time


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
        while True:
            if self.input_queue.full():
                while not self.input_queue.empty():
                    request, agent_id = self.input_queue.get()
                    if request == 'update beliefs':
                        #print(f'Agent{agent_id}: beliefs updated')
                        self.input_queue.task_done()

                    elif request == 'print name':
                        print(args.name)
                        self.input_queue.task_done()

    def get_agent_names(self):
        """
        Return a list with the names of all active agents/threads. (Minus the
        MainThread and the Strategist).
        """
        agents = [thread.name for thread in threading.enumerate()
                  if thread.name not in ['MainThread', 'Strategist']]
        return agents

    def get_agent(self, name):
        """
        Return the agent object given the agent's name.
        
        Arguments
        ---------
        name: str
            The name of the agent.
        """
        if isinstance(name, str):
            if [thread for thread in threading.enumerate() if thread.name == name]:
                return [thread for thread in threading.enumerate()
                        if thread.name == name][0]
        return False

    def get_beliefs(self, name):
        """
        Return the graph of a certain agent.

        Arguments
        ---------
        name: str
            The name of the agent.
        """
        if isinstance(name, str):
            return self.get_agent(name).beliefs
        return False

if __name__ == "__main__":
    input_queue, output_queue = Queue(maxsize=0), Queue(maxsize=0)
    strategist = Strategist(f"Strategist", [input_queue, output_queue])
    strategist.start()
