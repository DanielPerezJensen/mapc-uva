from .helpers import BDIAgent
from .attacker import Attacker
from .builder import Builder
from .defender import Defender
from .mapper import Mapper
from .spy import Spy
import json
import time


AGENTS = [Attacker, Builder, Defender, Mapper, Spy]
COLORS = ['\033[1;31m','\033[1;32m','\033[1;33m','\033[1;34m','\033[1;35m','\033[1;36m','\033[1;37m','\033[1;90m','\033[1;91m','\033[1;92m','\033[1;93m','\033[1;94m','\033[1;95m','\033[1;96m','\033[1;30m']
END_COLOR = '\033[0;0m'

class SuperAgent(*AGENTS, BDIAgent):

    def __init__(self, user, pw, print_json=False, timer=False):
        super().__init__(user, pw, print_json)
        self._timer = timer

    def run(self):
        """
        Function that (currently) moves north every iteration
        """

        while True:
            # Receive a message.
            msg = self.receive_msg()

            if msg:
                # Parse the response.
                if msg["type"] == "request-action":
                    # Get the request id
                    request_id = self._get_request_id(msg)

                    # Update beliefs
                    new_obstacle, new_empty, new_agents = self.graph.update(msg)
                    # self.update_beliefs(new_obstacle, new_emtpy, new_agents)

                    # TODO: Listen to strategist thread for role

                    # TODO: Set role as chosen by strategist

                    selected_agent = AGENTS[1] # Builder, example 

                    # TODO: Reasoning according to selected role
                    
                    action = selected_agent.get_action(self, new_obstacle, new_empty, new_agents) # example

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