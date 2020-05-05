import sys
from agents import SuperAgent
from agents.strategist import Strategist

n_agents = 15
a_list = []

strategist = Strategist()

for i in range(n_agents):
    a_list.append(SuperAgent(f"agentA{i}", "1", strategist))
    a_list[i].start()

strategist.insert_agents(a_list)
