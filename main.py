import sys
from agents import SuperAgent
from agents.strategist import Strategist

n_agents = 15
a_list = []

strategist = Strategist()

for i in range(1, n_agents + 1):
    a_list.append(SuperAgent(f"agentA{i}", "1", strategist))
    a_list[-1].start()

strategist.insert_agents(a_list)
