class Strategist(object):
    def __init__(self):
        pass

    def insert_agents(self, a_list):
        self.agents = {}
        for agent in a_list:
            self.agents[agent._user_id] = agent
    
    def get_agent_info(self, agent_id):
        if self.agents[agent_id]:
            return self.agents[agent_id]

    def eliminate_agents(self, agent_id, location, potential):
        """
        Eliminate potential agents based on environmental information.

        Arguments
        ---------
        agent_id: int
            The id of the agent requesting the action (the agent itself).
        location: (int, int)
            The offset between the comparing agents.
        potential: list
            A list of the potential agents.
        """
        finalists = potential[:]
        own_local_nodes = self.agents[agent_id].graph.get_local_nodes(offset=(0, 0))
        for agent in potential:
            intersection = []
            agent_local_nodes = self.agents[agent].graph.get_local_nodes(offset=(0, 0))
            for node in agent_local_nodes:
                temp = (node[0] + location[0], node[1] + location[1])
                if temp in own_local_nodes:
                    intersection.append(temp)
            
            for node in intersection:
                # node + current location
                own_node = (node[0] + self.agents[agent_id].graph.get_current().location[0], 
                            node[1] + self.agents[agent_id].graph.get_current().location[1])

                # node - location + current location
                agent_node = (node[0] - location[0] + self.agents[agent].graph.get_current().location[0], 
                                node[1] - location[1] + self.agents[agent].graph.get_current().location[1])

                if compare_nodes(self.agents[agent_id].graph.nodes[own_node],
                        self.agents[agent].graph.nodes[agent_node],
                        self.agents[agent_id].graph.get_step()):
                    pass
                else:
                    finalists.remove(agent)
                    break

        return finalists

    def potential_agents(self, agent_id, location=None):
        if location:
            potential = []
            reverse_location = (-location[0], -location[1])
            for agent in self.agents.values():
                if agent._user_id != agent_id:
                    if reverse_location in agent.graph.get_local_agents():
                        potential.append(agent._user_id)

            if len(potential) == 1:
                return potential[0]
            else:
                return self.eliminate_agents(agent_id, location, potential)

        else:
            potential = {}
            local_agent = self.agents[agent_id].graph.get_local_agents()
            print(local_agent)
            reverse_local_agent = [(-x, -y) for (x, y) in local_agent]

            for agent in self.agents.values():
                if agent._user_id != agent_id:
                    local_agents = agent.graph.get_local_agents()
                    for node in reverse_local_agent:
                        if node in local_agents:
                            node = (-node[0], -node[1])
                            if node in potential.keys():
                                potential[node].append(agent._user_id)
                            else:
                                potential[node] = [agent._user_id]
            for node in potential:
                potential[node] = self.eliminate_agents(agent_id, node, potential[node])
        return potential

def compare_nodes(n1, n2, step):
    # Terrain
    if n1.get_terrain()[0] != n2.get_terrain()[0]:
        return False

    # Things
    if sorted(n1.get_things(step)) != sorted(n2.get_things(step)):
        return False

    return True