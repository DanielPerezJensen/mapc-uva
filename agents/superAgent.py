from .helpers import BDIAgent
from .attacker import Attacker
from .builder import Builder
from .defender import Defender
from .mapper import Mapper
from .spy import Spy
import json
import time
import threading


AGENTS = [Attacker, Builder, Defender, Mapper, Spy]
COLORS = ['\033[1;31m','\033[1;32m','\033[1;33m','\033[1;34m','\033[1;35m',
          '\033[1;36m','\033[1;37m','\033[1;90m','\033[1;91m','\033[1;92m',
          '\033[1;93m','\033[1;94m','\033[1;95m','\033[1;96m','\033[1;30m']
END_COLOR = '\033[0;0m'

class SuperAgent(*AGENTS, BDIAgent):

    def __init__(self, user, pw, strategist, print_json=False, timer=False):
        super().__init__(user, pw, print_json)
        self._timer = timer
        self.strategist = strategist

    def run(self):
        """
        Function that runs the agents.
        """
        lock = threading.Lock()
        self.beliefs = self.strategist.get_graph(self._user_id)
        while True:
            # Receive a message.
            msg = self.receive_msg()

            if msg:
                # Parse the response.
                if msg["type"] == "request-action":
                    # Get the request id
                    request_id = self._get_request_id(msg)
                    agent_id = self._user_id
                    # Update beliefs
                    
                    lock.acquire()
                    new_obstacle, new_empty, new_agents = \
                        self.strategist.get_graph(agent_id).update(msg, agent_id)
                    lock.release()
                    # self.update_beliefs(new_obstacle, new_emtpy, new_agents)

                    # TODO: Listen to strategist thread for role

                    lock.acquire()
                    local_agents = self.strategist.potential_agents(agent_id)
                    lock.release()
                    print(f'{agent_id} --> {local_agents}')
                    #print(f'AgentA{agent_id} is paired with: {self.strategist.get_graph_pairs(agent_id)}')
                    
                    lock.acquire()
                    self.strategist.merge_agents(agent_id, local_agents)
                    lock.release()
                    
                    #print(len(self.strategist.get_all_pairs()))

                    # TODO: Set role as chosen by strategist

                    selected_agent = AGENTS[3] # Builder, example 

                    # TODO: Reasoning according to selected role
                    
                    options = ['single', 'random', 'east']
                    action = selected_agent.explore(self, agent_id,
                                                    new_obstacle, new_empty,
                                                    new_agents, options)

                    if not action:
                        action = self.skip()

                    # Send action to server
                    self.send_request(self._add_request_id(action, request_id))

                    # Provide timing information
                    if self._timer:
                        end_ms = int(round(time.time() * 1000))
                        diff = msg["content"]["deadline"] - end_ms
                        time_relation = 'before' if diff >= 0 else 'after'
                        print(f"{COLORS[self._user_id % 15]}{self.name:<10}{END_COLOR} {f'done {abs(diff)} ms {time_relation} deadline':<50} step {request_id}")

                elif msg["type"] == "sim-start":
                    pass
                elif msg["type"] == "sim-end":
                    pass
                elif msg["type"] == "bye":
                    self.close_socket()
                else:
                    print(f"Unknown message from the server: {msg['type']}") 
