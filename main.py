from agents import SuperAgent
from agents.strategist import Strategist

n_agents = 1
a_list = []

strategist = Strategist()

for i in range(1, n_agents + 1):
    a_list.append(SuperAgent(f"agentA{i}", "1", strategist))
    strategist.insert_agents(a_list[-1])
    a_list[i-1].start()