import sys
from agents import SuperAgent
from agents.strategist import Strategist

n_agents = 3
a_list = []

strategist = Strategist()

agent1 = SuperAgent(f"agentA{1}", "1", strategist)
agent1.start()
agent3 = SuperAgent(f"agentA{3}", "1", strategist)
agent3.start()


# for i in range(1, n_agents + 1):
#     a_list.append(SuperAgent(f"agentA{i}", "1", strategist))
#     a_list[-1].start()

strategist.insert_agents([agent1, agent3])
