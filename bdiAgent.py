from agent import Agent
from spade_bdi.bdi import BDIAgent
import agentspeak

class CustomBDIAgent(BDIAgent, Agent):

    def __init__(self, jid, xmpp_pass, asl, game_name, game_pass, print_json):
        BDIAgent.__init__(self, jid, xmpp_pass, asl)
        Agent.__init__(self, game_name, game_pass, print_json)

    def add_custom_actions(self, actions):

        @actions.add_function("bdi_move", (int, agentspeak.Literal,))
        def bdi_move(request_id, direction):
            print(request_id, str(direction))
            a.move(request_id, str(direction))
            return 1

        @actions.add_function("a_function", (agentspeak.Literal,))
        def a_function(x):
            return x

    def play(self):
        while True:
            # Receive a message.
            msg = self.receive_msg()

            # Parse the response.
            if msg["type"] == "request-action":
                request_id = self._get_request_id(msg)

                # do something
                print("doing something")
                # self.bdi.set_belief("car", "red")
                # self.bdi.remove_belief("car", "red")

                self.bdi.set_belief("cell_empty", request_id, "n")
                # self.bdi.remove_belief("cell_empty", request_id, "n")
            elif msg["type"] == "sim-start":
                pass
            elif msg["type"] == "sim-end":
                pass
            elif msg["type"] == "bye":
                self.close_socket()
            else:
                print(f"Unknown message type from the server: {msg['type']}")




a = CustomBDIAgent("agentA0@localhost", "1", 'agent.asl', 'agentA0', '1', False)
a.start()
a.play()

