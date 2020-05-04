import sys
from agents import SuperAgent

n_agents = 15

a_list = []

for i in range(n_agents):
    a_list.append(SuperAgent(f"agentA{i}", "1", timer=True))
    a_list[i].start()
