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


class SuperAgent(*AGENTS, BDIAgent):

    def __init__(self, user, pw, print_json=False,
                 timer=False, print_queue=False):
        super().__init__(user, pw, print_json)
        BDIAgent.__init__(self)
        self._timer = timer
        self._print_queue = print_queue

    def run(self):
        """
        Function that runs the agents.
        """
        strategist = [agent for agent in threading.enumerate()
                      if agent.name == 'Strategist'][0]
        if strategist:
            self.input_queue = strategist.input_queue
            self.output_queue = strategist.output_queue
        else:
            print('Agents play without the strategist.')

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
                    self.beliefs.update(msg, agent_id)

                    # Send a message to the strategist that if has updated its
                    # beliefs. Agent can continue when all agents updated their
                    # belief.
                    if hasattr(self, 'input_queue'):
                        self.input_queue.put(('update', self))
                        self.input_queue.join()

                        self.input_queue.put(('merge', self))

                    # TODO: Listen to strategist thread for role
                    # TODO: Set role as chosen by strategist
                    agent_type = AGENTS[3]

                    # # Read last action if it randomly failed
                    if msg['content']['percept']['lastActionResult'] == \
                            'failed_random' and self.last_intention:
                        if self.last_intention.method.__name__ != "nav_to":
                            self.add_last_intention()

                    if self._print_queue:
                        self.pretty_print([x.description
                                           for x in self.intention_queue])

                    # If intention queue is empty, add intention (temporary)
                    if not self.intention_queue:
                        # Get intention from agent_type
                        intention_addition = agent_type.get_intention(self)

                        if intention_addition:
                            print("got intention")
                            self.add_intention(*intention_addition)

                    request_id = self._get_request_id(msg)

                    action = self.execute_intention()

                    if action:
                        self.send_request(self._add_request_id(action,
                                          request_id))
                    else:
                        action = self.skip()
                        self.send_request(
                            self._add_request_id(action, request_id))
                        self.pretty_print("Done with action", request_id)

                    # Provide timing information
                    if self._timer:
                        end_ms = int(round(time.time() * 1000))
                        diff = msg["content"]["deadline"] - end_ms
                        time_relation = 'before' if diff >= 0 else 'after'
                        self.pretty_print(f"done {abs(diff)} ms \
                                        {time_relation} deadline", request_id)

                elif msg["type"] == "sim-start":
                    pass
                elif msg["type"] == "sim-end":
                    pass
                elif msg["type"] == "bye":
                    self.close_socket()
                else:
                    print(f"Unknown message from the server: {msg['type']}")
