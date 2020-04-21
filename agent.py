from server import Server


class Agent(Server):
    """
    Class for dummy agents which can connect to the server
    """

    def play(self):
        """
        Function that (currently) moves north every iteration
        """
        while True:
            # Receive a message.
            msg = self.receive_msg()

            # Parse the response.
            if msg["type"] == "request-action":
                request_id = self._get_request_id(msg)

                # do something
                self.move(request_id, "n")
            elif msg["type"] == "sim-start":
                pass
            elif msg["type"] == "sim-end":
                pass
            elif msg["type"] == "bye":
                self.close_socket()
            else:
                print(f"Unknown message type from the server: {msg['type']}")


    def skip(self, request_id):
        """
        Skip a turn for the agent
        
        parameters
        ----------
        request_id: str 
            Id of the request-action from the server.
        """
        # Create the request.
        skip_request = self._create_action(request_id, "skip")

        # Send the request to the server.
        self.send_request(skip_request)


    def move(self, request_id, direction):
        """
        Moves the agent in the specified direction
        
        parameters
        ----------
        request_id: str 
            Id of the request-action from the server.
        direction: str
            One of {n,s,e,w}, representing the direction the agent wants to move in.
        """
        print("moving")
        # Create the request.
        move_request = self._create_action(request_id, "move", direction)

        # Send the request to the server.
        self.send_request(move_request)


    def attach(self, request_id, direction):
        """
        Attaches something to the agent. 
        Note: the agent has to be directly next to it.
        
        parameters
        ----------
        request_id: str 
            Id of the request-action from the server.
        direction: str
            One of {n,s,e,w}, representing the direction to the thing the agent wants to attach.
        """
        # Create the request.
        attach_request = self._create_action(request_id, "attach", direction)

        # Send the request to the server.
        self.send_request(attach_request)


    def detach(self, request_id, direction):
        """
        Detaches something from the agent. 
        Note: only the connection between the agent and the thing is released.
        
        parameters
        ----------
        request_id: str 
            Id of the request-action from the server.
        direction: str
            One of {n,s,e,w}, representing the direction to the thing the agent wants to detach from.
        """
        # Create the request.
        detach_request = self._create_action(request_id, "detach", direction)

        # Send the request to the server.
        self.send_request(detach_request)


    def rotate(self, request_id, direction):
        """
        Rotates the agent (and all attached things) 90 degrees in the given direction. 
        
        parameters
        ----------
        request_id: str 
            Id of the request-action from the server.
        direction: str
            One of {cw, ccw}, representing the rotation direction (clockwise or counterclockwise).
        """
        # Create the request.
        rotate_request = self._create_action(request_id, "rotate", direction)

        # Send the request to the server.
        self.send_request(rotate_request)


    def connect(self, request_id, agent, x, y):
        """
        Two agents can use this action to connect things attached to them.
        
        parameters
        ----------
        request_id: str 
            Id of the request-action from the server.
        agent: str
            The agent to cooperate with.
        x: int or str
            The relative x position of the thing
        y: int or str
            The relative y position of the thing
        """
        # Create the request.
        connect_request = self._create_action(request_id, "connect", agent, str(x), str(y))

        # Send the request to the server.
        self.send_request(connect_request)


    def disconnect(self, request_id, x1, y1, x2, y2):
        """
        Disconnects two attachments (probably blocks) of the agent.
        
        parameters
        ----------
        request_id: str
            Id of the request-action from the server.
        x1: int or str 
            The relative x position of the first attachment.
        y1: int or str
             The relative y position of the first attachment.
        x2: int or str
            The relative x position of the second attachment.
        y2: int or str
            The relative y position of the second attachment.
        """
        # Create the request.
        disconnect_request = self._create_action(request_id, "disconnect", str(x1), str(y1), str(x2), str(y2))

        # Send the request to the server.
        self.send_request(disconnect_request)

    
    def request(self, request_id, direction):
        """
        Requests a new block from a dispenser. 
        Note: the agent has to be in a cell adjacent to the dispenser and specify the direction to it.
        
        parameters
        ----------
        request_id: str 
            Id of the request-action from the server.
        direction: str
            One of {n,s,e,w}, representing the direction to the position of the dispenser to use.
        """
        # Create the request.
        request_request = self._create_action(request_id, "request", direction)

        # Send the request to the server.
        self.send_request(request_request)


    def submit(self, request_id, task):
        """
        Submit the pattern of things that are attached to the agent to complete a task.
        
        parameters
        ----------
        request_id: str 
            Id of the request-action from the server.
        task: str
            The name of an active task.
        """
        # Create the request.
        submit_request = self._create_action(request_id, "submit", task)

        # Send the request to the server.
        self.send_request(submit_request)


    def clear(self, request_id, x, y):
        """
        Submit the pattern of things that are attached to the agent to complete a task.
        Note: The area is cleared after a number of consecutive successful clear actions for the same target position.
        Note: The action consumes a fixed amount of energy.
        
        parameters
        ----------
        request_id: str 
            Id of the request-action from the server.
        x: int or str
            The relative x position of the target position.
        y: int or str
            The relative y position of the target position.
        """
        # Create the request.
        clear_request = self._create_action(request_id, "clear", x, y)

        # Send the request to the server.
        self.send_request(clear_request)

    
    def accept(self, request_id, task):
        """
        Submit the pattern of things that are attached to the agent to complete a task.
        Note: The area is cleared after a number of consecutive successful clear actions for the same target position.
        Note: The action consumes a fixed amount of energy.
        
        parameters
        ----------
        request_id: str 
            Id of the request-action from the server.
        task: str
            The name of the task to accept.
        """
        # Create the request.
        accept_request = self._create_action(request_id, "accept", task)

        # Send the request to the server.
        self.send_request(accept_request)

    

    ### Helper functions ###
    @staticmethod
    def _create_action(request_id, action_type, *p):
        """
        Returns an action message.

        parameters
        ----------
        request_id: str
            Id of the request-action from the server.
        action_type: str
            The type of action to use.
        p: str
            Parameters for the action.
        """
        # Create the action.
        action = {
            "type": "action",
            "content": {
                "id": request_id,
                "type": action_type,
                "p": list(p)
            }
        }
        
        # Return the action.
        return action


    



if __name__ == "__main__":
    agent = Agent(f"agentA0", "1", print_json=True)
    agent.play()

