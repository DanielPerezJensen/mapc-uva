import sys
from agents import SuperAgent

n_agents = 1
a_list = []

for i in range(1, n_agents + 1):
    a_list.append(SuperAgent(f"agentA{i}", "1"))
    a_list[-1].start()
