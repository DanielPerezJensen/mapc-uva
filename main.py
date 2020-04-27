import sys
from agents import SuperAgent


a_list = []

for i in range(15):
    a_list.append(SuperAgent(f"agentA{i}", "1"))
    a_list[i].start()
