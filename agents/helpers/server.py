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
        self._user_id = int((user[-2] if user[-2].isdigit() else "") +
                            user[-1])
        self._pw = pw
        self._print_json = print_json
        self._COLORS = ['\033[1;31m', '\033[1;32m', '\033[1;33m', '\033[1;34m',
                        '\033[1;35m', '\033[1;36m', '\033[1;37m', '\033[1;90m',
                        '\033[1;91m', '\033[1;92m', '\033[1;93m', '\033[1;94m',
                        '\033[1;95m', '\033[1;96m', '\033[1;30m']
        self._END_COLOR = '\033[0;0m'

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
            self.pretty_print("connection succesful")
        else:
            self.pretty_print("connection failed")

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
        if request['type'] == "action":
            content = f"{request['content']['type']}" + \
                    (f" {request['content']['p']}" if
                        list(request['content']['p']) else "")
            self.pretty_print(content, self._get_request_id(request))

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
                # print(json.loads(msg))
                print(json.dumps(json.loads(msg), indent=2))

            return json.loads(msg)
        else:
            return None

    def pretty_print(self, msg, request_id=""):
        """
        Prints a well formatted message including the agent
        name and optionally with the current step information.

        parameters
        ----------
        msg: str
            The message to send to the server
        request_id: str, optional
            The latest request-id from the server.
            If provided, prints the current step.
        """

        out = f"""{self._COLORS[self._user_id % 15]}
                  {self.name:<10}{self._END_COLOR} {msg:<50}"""

        if request_id:
            out += f" step {request_id}"

        print(out)

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

    @staticmethod
    def _get_action_result(action_request):
        """
        Returns if the action last sent to the server has succeeded

        parameters
        ----------
        action_request: dict
            The action-request of the server.
        """
        if action_request["content"]["percept"]["lastAction"] != "no_action":
            if action_request["content"]["percept"]["lastActionResult"] == \
                    "success":
                return True

        return False

    @staticmethod
    def _add_request_id(action, request_id):
        """
        Returns the action with the given request id.

        parameters
        ----------
        action: dict
            The action to be sent to the server.
        """
        action['content']['id'] = request_id
        return action
