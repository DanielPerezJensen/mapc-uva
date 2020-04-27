import socket
import json
import time
from threading import Thread


class Server(Thread):
    """
    Class used to connect, authorize, receive and send messages
    with/to the server
    """
    def __init__(self, user, pw, print_json=False):
        """
        Store some information about the agent and connect and authorize with
        the server

        parameters
        ----------
        user: str
            The username of the agent.
        pw: str
            The password of the agent.
        print_json: bool
            If the communication jsons should be printed.
        """
        super().__init__(name=user)
        self._user = user
        self._pw = pw
        self._print_json = print_json

        # Create, connect and authorize socket connection
        self.connect_socket()
        self.authorize_socket()

    def connect_socket(self):
        # Create socket object.
        host, port = "localhost", 12300
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to server.
        try:
            self.socket.connect((host, port))
        # In case of error throw error message
        except Exception as e:
            print("Could not connect to port")
            raise e

    def authorize_socket(self):
        """
        Authorize socket by sending auth-request to server
        """
        auth_request = {
            "type": "auth-request",
            "content": {
                "user": self._user,
                "pw": self._pw
            }
        }

        # Create and send authentication request.
        self.send_request(auth_request)

        # Parse response.
        response = self.receive_msg()

        if response["content"]["result"] == "ok":
            print(self.name, ": Connection Succesful")
        else:
            print(self.name, ": Connection Failed")

    def close_socket(self):
        """
        Disconnects the socket from the server.
        """
        if self.socket:
            self.socket.close()

    def send_request(self, request):
        """
        Takes request as input and sends binary-encoded json block to server.

        parameters
        ----------
        request: dict
            The request to send to the server.
        """
        # Print the request if required.
        if self._print_json:
            print(request)

        # Send the request to the server.
        self.socket.sendall((json.dumps(request) + "\0").encode())

    def receive_msg(self):
        """
        Returns message from server, if no message is received return None
        """
        msg = self.socket.recv(65536).decode().split("\0")[0]

        # In case a message is received, parse it into a dictionary.
        if len(msg) > 1:
            if self._print_json:
                print(msg)

            return json.loads(msg)
        else:
            return None

    @staticmethod
    def _get_request_id(action_request):
        """
        Returns the request id of a request-action message from the server.

        parameters
        ----------
        action_request: dict
            The action-request of the server.
        """
        return action_request["content"]["id"]
