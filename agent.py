import socket
import sys
import json


class Agent():
    """
    Basic class for dummy agents which can connect to the server
    """
    def __init__(self, user, pw):
        """
        Store some information about the agent and the socket so we can 
        connect to the localhost.

        Input: user (str)
               pw (str)
               socket (socket object)
        """
        self.user = user
        self.pw = pw

        # Create socket object
        HOST, PORT = "localhost", 12300
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Connect to server
            self.socket.connect((HOST, PORT))

        except Exception as e:
            print(str(e))
            print("Could not connect port")

        self.connect()
        self.play()

    def connect(self):
        """
        Connect to socket and send auth_request
        """

        auth_request_dict = {
            "type": "auth-request",
            "content": {
                "user": self.user,
                "pw": self.pw
            }
        }
        # Create and send authentication request with 0 byte to terminate
        auth_request = json.dumps(auth_request_dict)
        self.send_request(auth_request)

        # Parse response
        response = json.loads(self.socket.recv(65536).decode())
        if response["content"]["result"] == "ok":
            print("Connection Succesful")
        else:
            print("Connection Failed")

    def send_request(self, request):
        """
        Receives json block and sends request to server
        """
        self.socket.sendall((request + "\0").encode())

    def play(self):
        """
        Play function that (currently) moves north every iteration
        """
        while True:
            response = self.socket.recv(65536).decode().split("\0")[0]
            print(response)
            print(len(response))
            # In case we get a response, parse it into a dictionary
            if len(response) > 1:
                response = json.loads(response)

                if response["type"] == "request-action":
                    request_id = response["content"]["id"]
                    move_request = self.move("n", request_id)
                    self.send_request(move_request)

    def move(self, direction, request_id):
        """
        Returns the json block that tells agent to move
        """
        move_request = {
            "type": "action",
            "content": {
                "id": request_id,
                "type": "move",
                "p": [direction]
            }
        }
        return json.dumps(move_request)


agent = Agent(f"agentA0", "1")
agent.connect()
