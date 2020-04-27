from agent import Agent
from mapping.graph import Graph
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
        self.first_step()

        
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
        print("Graph updated: ready!")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--agent",
        type=str,
        default="agentA0",
        help="Name of agent to be initialized"
    )

    parser.add_argument(
        "--pw",
        type=str,
        default="1",
        help="Password of agent to be initialized"
    )

    parser.add_argument(
        "--loc",
        type=int,
        nargs='+',
        help="Name of agent to be initialized"
    )


    ARGS = parser.parse_args()

    agent = DebugAgent(ARGS.agent, ARGS.pw, tuple(ARGS.loc))