import sys
import socket
import json
from agents import SuperAgent


def main():

    teamSize = get_teamSize()

    # In case teamSize is returned and not None, start up the agents
    if teamSize:
        a_list = []

        for i in range(1, teamSize + 1):
            a_list.append(SuperAgent(f"agentA{i}", "1"))
            a_list[-1].start()


def get_teamSize():
    """
    Returns the configuration of the server as
    returned by the SIM-CONFIG message request
    args:
        None
    returns:
        teamSize
    """
    # Create socket object.
    host, port = "localhost", 12300
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to server.
    try:
        sock.connect((host, port))

    # In case of error throw error message
    except ConnectionRefusedError:
        print("Could not connect to port")
        return

    # Create status-request
    request = {
        "type": "status-request",
        "content": {}
    }

    # Send status-request and listen for response
    sock.sendall((json.dumps(request) + "\0").encode())

    msg = sock.recv(65536).decode().split("\0")[0]
    msg = json.loads(msg)
    # print(msg)

    # If message is received, parse it and return it otherwise return None
    if len(msg) > 1:
        currentSimulation = msg["content"]["currentSimulation"]
        teamSizes = msg["content"]["teamSizes"]

        # If currentSimulation index is -1, simulation has not started yet
        if currentSimulation == -1:
            return teamSizes[0]
        else:
            return teamSizes[currentSimulation]
    else:
        return None

    sock.close()


if __name__ == "__main__":
    main()
