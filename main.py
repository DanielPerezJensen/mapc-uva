import sys
from agents import SuperAgent
from agents import Strategist
from queue import Queue

n_agents = 15
agent_list = []
input_queue, output_queue = Queue(maxsize=n_agents), Queue(maxsize=n_agents)

strategist = Strategist(f"Strategist", [input_queue, output_queue])
strategist.start()

for i in range(1, n_agents + 1):
    agent_list.append(SuperAgent(f"agentA{i}", "1"))
    agent_list[-1].start()
