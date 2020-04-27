import agents
from .helpers import BDIAgent
from .attacker import Attacker
from .builder import Builder
from .defender import Defender
from .mapper import Mapper
from .scout import Scout
import json


AGENTS = [Attacker, Builder, Defender, Mapper, Scout]


class SuperAgent(*AGENTS, BDIAgent):

    def run(self):
        """
        Function that (currently) moves north every iteration
        """
        while True:
            # Receive a message.
            msg = self.receive_msg()

            if msg:
                print(json.dumps(msg, indent=2))

                # Parse the response.
                if msg["type"] == "request-action":
                    self.update_beliefs(msg)

                    # TODO: listen to strategist thread for role

                    # TODO: Set role as chosen by strategist

                    # TODO: Reasoning according to selected role
                elif msg["type"] == "sim-start":
                    pass
                elif msg["type"] == "sim-end":
                    pass
                elif msg["type"] == "bye":
                    self.close_socket()
                else:
                    print(f"Unknown message from the server: {msg['type']}")
