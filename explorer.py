from agent import Agent
from mapping.graph import Graph
from mapping.dstarlite import DStarLite


class Explorer(Agent):
    def explore(self, mode=0):
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

                self.graph.update_current(msg)
                self.graph.update_graph(msg)

                if mode == 1:
                    agents = []#self.graph.get_agents(msg["content"]["step"])
                    agents = [value for value in agents if value[0] != (0,0)]
                    if agents != []:
                        agent = None
                        for i in [0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5]:
                            for a in agents:
                                if a[0][1] == i:
                                    agent = a
                                    break
                            if agent != None:
                                break

                        agent_id, loc = self.broadcast_agent(location)
                        self.two_agent_mapping(agent_id, loc)
                elif mode == 2:
                    pass#self.detailed_mapping()
                else:
                    self.general_mapping()
                
            elif msg["type"] == "sim-start":
                print("Simulation starting")
            elif msg["type"] == "sim-end":
                pass
            elif msg["type"] == "bye":
                self.close_socket()
            else:
                print(f"Unknown message type from the server: {msg['type']}")

    def general_mapping(self, vert_len=3, iters=2, a=-1):
        """
        Create an overall map of the world by moving horizontally in a wide
        zig-zag pattern (south, east, north, east, south, etc.).
        
        Flags are used to adjust the length the agent walks, in case the previous
        path (horizontal or vertical) failed and adjusted its length.

        parameters
        ----------
        vert_len: int
            Number of cells the agent walks vertically.
        iters: int
            Number of times the agent performs the zig-zag pattern.
        a: int
            a can be either 1 or -1, this decide whether the agent will 
            go east or west.
        """
        path_fail_h_flag = False
        path_fail_v_flag = False
        for i in range(iters):
            # Going south
            x, y = self.graph.get_current().loc
            if path_fail_h_flag:
                result = self.navigate((x, vert_len+y+10))
                path_fail_h_flag = False
            else:
                result = self.navigate((x, vert_len+y))

            if result not in [True, 0]:
                path_fail_h_flag = True
                start_x, start_y = result[0]
                current_x, current_y = result[1]
                self.navigate((start_x, start+10))
            
            # Going east
            x, y = self.graph.get_current().loc
            if path_fail_v_flag:
                result = self.navigate(((a*16)+x, y))
                path_fail_v_flag = False
            else:
                result = self.navigate(((a*11)+x, y))

            if result not in [True, 0]:
                path_fail_v_flag = True
                start_x, start_y = result[0]
                current_x, current_y = result[1]
                self.navigate((start+(a*5), start_y))
            
            # Going north
            x, y = self.graph.get_current().loc
            if path_fail_h_flag:
                result = self.navigate((x, -vert_len+y-10))
                path_fail_h_flag = False
            else:
                result = self.navigate((x, -vert_len+y))

            if result not in [True, 0]:
                path_fail_h_flag = True
                start_x, start_y = result[0]
                current_x, current_y = result[1]
                self.navigate((start_x, start_y-10))
            
            # Going east
            x, y = self.graph.get_current().loc
            if path_fail_v_flag:
                result = self.navigate(((a*16)+x, y))
                path_fail_v_flag = False
            else:
                result = self.navigate(((a*11)+x, y))
            if result not in [True, 0]:
                path_fail_v_flag = True
                start_x, start_y = result[0]
                current_x, current_y = result[1]
                self.navigate((start+(a*5), start_y))


    def two_agent_mapping(self, agent_loc, vert_len=20):
        """
        Create an overall map of the world by moving horizontally in a wide
        zig-zag pattern (south, east, north, east, south, etc.).

        IDEA: Do general mapping; if obstacle is detected -> trace obstacle.
              Return to general mapping

        parameters
        ----------
        agent_direction: str
            The direction the second agent stands.
        vert_len: int
            Number of cells the agent walks vertically.
        """
        if self.graph.get_direction(agent_loc) == "e":
            a = 1
        elif self.graph.get_direction(agent_loc) == "w":
            a = -1
        else:
            return

        while True:
            x, y = self.graph.get_current().loc
            temp = self.navigate((x, vert_len+y))
            if temp not in [True, 0]:
                pass# Backup plan
            elif temp == 0:
                # create new graph by merging the graphs
                pass#return new_graph

            x, y = self.graph.get_current().loc
            temp = self.nav_to(((11*a)+x, y))
            if temp not in [True, 0]:
                pass# Backup plan
            elif temp == 0:
                # create new graph by merging the graphs
                pass#return new_graph

            x, y = self.graph.get_current().loc
            temp = self.nav_to((x, -vert_len+y))
            if temp not in [True, 0]:
                pass# Backup plan
            elif temp == 0:
                # create new graph by merging the graphs
                pass#return new_graph

            x, y = self.graph.get_current().loc
            temp = self.nav_to(((11*a)+x, y))
            if temp not in [True, 0]:
                pass# Backup plan
            elif temp == 0:
                # create new graph by merging the graphs
                pass#return new_graph

        return True
    
    def navigate(self, goal, agent_id=None):
        """
        Navigate to coordinates in the agent's local reference frame.

        parameters
        ----------
        goal: tuple
            x and y coordinates of the goal location.
        request_id: str
            Id of the request_action for the first step

        Returns True if at goal state, False if no path is possible
        """
        dstar = DStarLite(self.graph, goal, self.last_action_move)
        start = self.graph.get_current()

        for step, recovery_step in dstar.move_to_goal():
            if agent_id and spot_scout(agent_id):
                # broadcast to find agents location and return it
                return 0#loc

            # check if a path is found
            if step:
                msg = self.receive_msg()

                while msg["type"] != "request-action":
                    msg = self.receive_msg()
                
                location_changed = self.graph.update_current(msg)
                request_id = self._get_request_id(msg)
                
                # check if last move was succesfull
                if location_changed:
                    direction = self.graph.get_direction(step)
                else:
                    direction = self.graph.get_direction(recovery_step)

                # move in the desired direction
                self.move(request_id, direction)
                    
                # update graph
                new_empty, new_obstacle = self.graph.update_graph(msg)
                print(len(self.graph.nodes.keys()))

                # update path
                dstar.update_graph(self.graph, new_empty + new_obstacle, location_changed)
            else:
                print("No path found")
                return start, self.current
        return True

    def spot_scout(agent_id):
        """
        Check if the other scout is spotted.
        If True: merge maps; False: keep going
        """
        return False

    def broadcast_agent(self, loc):
        """
        Send out a broadcast to identify other agent. Also get in same y-coordinates.
        """
        pass
        return agent_id

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
