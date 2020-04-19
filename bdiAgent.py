import asyncio
from agent import Agent
from spade_bdi.bdi import BDIAgent

class CustomBDIAgent(BDIAgent, Agent):

    def __init__(self, jid, xmpp_pass, asl, game_name, game_pass, print_json):
        BDIAgent.__init__(self, jid, xmpp_pass, asl)
        Agent.__init__(self, game_name, game_pass, print_json)

    def add_custom_actions(self, actions):

        @actions.add_function("bdi_move", (int, str))
        def bdi_move(request_id, direction):
            print(request_id, direction)
            # a.move(request_id, direction)

    def play(self):
        while True:
            # Receive a message.
            msg = self.receive_msg()

            # Parse the response.
            if msg["type"] == "request-action":
                request_id = self._get_request_id(msg)

                # do something
                print("doing something")
                self.bdi.set_belief("car", "green")
                self.bdi.set_belief("cell_empty", "kaas")
                self.bdi.set_belief("cell_empty", request_id, "n")
                self.bdi.remove_belief("cell_empty", request_id, "n")
            elif msg["type"] == "sim-start":
                pass
            elif msg["type"] == "sim-end":
                pass
            elif msg["type"] == "bye":
                self.close_socket()
            else:
                print(f"Unknown message type from the server: {msg['type']}")




a = CustomBDIAgent("agent0@localhost", "0", 'agent.asl', 'agentA0', '1', False)
a.start()
a.play()

