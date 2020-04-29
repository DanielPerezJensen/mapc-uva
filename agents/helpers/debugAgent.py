from .agent import Agent
from .graph import Graph
import argparse


class DebugAgent(Agent):
    """
    The debug agent gives agents the superpower of using global coordinates to navigate.
    They still have limited vision, but their initial position is given in global coordinates.
    """

    def __init__(self, user, pw, global_pos, print_json=True):
        """
        Initialise the debug agent by providing it with it's global starting coordinates.
        """

        super().__init__(user, pw, print_json)
        
        new_node_dict = {}
        gl_x, gl_y = global_pos
        for (x, y), node in self.graph.nodes.items():
            x += gl_x
            y += gl_y
            node.loc = (x, y)
            new_node_dict[(x, y)] = node

        self.graph.nodes = new_node_dict
        # self.first_step()

        
    def first_step(self):
        """
        Function that parses the first percept to map the environment
        """
        while True:
            # Receive a message.
            msg = self.receive_msg()

            # Parse the response.
            if msg["type"] == "request-action":
                request_id = self._get_request_id(msg)

                # Choose action
                self.skip(request_id)

                self.graph.update_graph(msg)
                break
        print(self.name, ": graph updated, ready!")




if __name__ == "__main__":
    global_locs = {
        "agentA0": (45, 3),
        "agentA1": (46, 2),
        "agentA2": (46, 3),
        "agentA3": (57, 33),
        "agentA4": (58, 32),
        "agentA5": (58, 33),
        "agentA6": (19, 54),
        "agentA7": (20, 53),
        "agentA8": (20, 54),
        "agentA9": (4, 29),
        "agentA10": (5, 28),
        "agentA11": (5, 29),
        "agentA12": (38, 35),
        "agentA13": (38, 36),
        "agentA14": (38, 37)
    }


    a_list = {}
    for name, global_loc in global_locs.items():
        a_list[name] = DebugAgent(name, "1", global_loc, print_json=False)
        a_list[name].start()
        
    for name in global_locs.keys():
        a_list[name].run()