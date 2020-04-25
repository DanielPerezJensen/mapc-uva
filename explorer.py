from agent import Agent


class Explorer(Agent):
    def explore(self):
        """
        1) Basic overall exploration
        2) More detailed exploration
        3) Find patterns in environment
        """

        while True:
            # Receive a message.
            msg = self.receive_msg()

            # Parse the response.
            if msg["type"] == "request-action":
                request_id = self._get_request_id(msg)

                self.skip(request_id)
                self.graph.update_graph(msg)

                self.general_mapping()
                

            elif msg["type"] == "sim-start":
                print("Simulation starting")
            elif msg["type"] == "sim-end":
                pass
            elif msg["type"] == "bye":
                self.close_socket()
            else:
                print(f"Unknown message type from the server: {msg['type']}")

            # detailed_mapping
            #self.detailed_mapping()

            # Find patterns


    def general_mapping(self, vert_len=15, iters=1):
        """
        Create an overall map of the world by moving horizontally in a wide
        zig-zag pattern (south, east, north, east, south, etc.).

        IDEA: Do general mapping; if obstacle is detected -> trace obstacle.
              Return to general mapping

        parameters
        ----------
        vert_len: int
            Number of cells the agent walks vertically.
        iters: int
            Number of times the agent repeats the zig-zag pattern.
        """

        for i in range(iters):
            # TODO: make failcase

            x, y = self.graph.get_current().loc
            self.nav_to((x, vert_len+y))

            x, y = self.graph.get_current().loc
            self.nav_to((11+x, y))

            x, y = self.graph.get_current().loc
            self.nav_to((x, -vert_len+y))

            x, y = self.graph.get_current().loc
            self.nav_to((11+x, y))
    
    def detailed_mapping(self):
        """
        Enhance the general map by filling in empty spots and detecting obstacles.
        """
        pass
        self.fill_in()
        

    def fill_in(self):
        """
        Fill in the graph by moving to empty spaces within the graph.
        """

        pass
    
    def trace_obstacle(self):
        """
        Trace the edge of an obstacle to help fill in empty nodes inside the obtacle.
        """
        pass


dora = Explorer("agentA0", "1")
dora.explore()
