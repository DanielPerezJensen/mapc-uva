from agents.helpers.graph import merge_graphs
from agents.helpers.graph import Graph

class Strategist(object):
    def __init__(self):
        pass

    def insert_agents(self, a_list):
        self.agents, self.graphs = {}, {}
        for agent in a_list:
            self.agents[agent._user_id] = agent
            self.graphs[agent._user_id] = Graph(agent._user_id)
    
    def get_graph(self, agent_id):
        return self.graphs[agent_id]

    def get_agent_info(self, agent_id):
        if self.agents[agent_id]:
            return self.agents[agent_id]

    def get_graph_pairs(self, agent_id):
        return list(self.graphs[agent_id].current.keys())
    
    def get_all_pairs(self):
        n = list(self.agents.keys())
        pairs = []
        while n != []:
            temp = self.get_graph_pairs(n[0])
            pairs.append(temp)
            n = [x for x in n if x not in temp]
        return pairs

    def merge_agents(self, agent_id, local_agents):
        """
        If the agent know the identity of another agent, they will merge their
        graphs.

        Arguments
        ---------
        agent_id: int
            The id of the agent requesting the action.
        local_agents: dict(locations, agents)
            The dictionary returned by potential_agents(). The keys are the
            agent locations and the values are a list of potential agents.
        """
        for location in local_agents:
            if len(local_agents[location]) == 1:
                agent = local_agents[location][0]
                # Merge agents
                if agent in self.graphs[agent_id].current.keys():
                    print(f'Agent{agent} is already merged with Agent{agent_id}.')
                else:
                    g1 = merge_graphs(self.graphs[agent_id], agent_id,
                                      self.graphs[agent], agent, location)
                    for agent in g1.current:
                        self.graphs[agent] = g1

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
            A list of id's of the potential agents.
        """
        finalists = potential[:]
        own_local_nodes = self.graphs[agent_id].get_local_nodes(agent_id, offset=(0, 0))
        for agent in potential:
            intersection = []
            agent_local_nodes = self.graphs[agent].get_local_nodes(agent, offset=(0, 0))
            for node in agent_local_nodes:
                temp = (node[0] + location[0], node[1] + location[1])
                if temp in own_local_nodes:
                    intersection.append(temp)
            
            for node in intersection:
                # node + current location
                own_node = (node[0] + self.graphs[agent_id].get_current(agent_id).location[0], 
                            node[1] + self.graphs[agent_id].get_current(agent_id).location[1])

                # node - location + current location
                agent_node = (node[0] - location[0] + self.graphs[agent].get_current(agent).location[0], 
                                node[1] - location[1] + self.graphs[agent].get_current(agent).location[1])

                if compare_nodes(self.graphs[agent_id].nodes[own_node],
                        self.graphs[agent].nodes[agent_node],
                        self.graphs[agent_id].get_step()):
                    pass
                else:
                    finalists.remove(agent)
                    break

        return finalists

    def potential_agents(self, agent_id, location=None):
        """
        Create a list of potential agent id's on a certain location.
        If no location is given all locations where agents are will be calculated.
        """
        if location:
            potential = []
            reverse_location = (-location[0], -location[1])
            for agent in self.agents.values():
                if agent._user_id != agent_id:
                    if reverse_location in \
                            self.graphs[agent._user_id].get_local_agents(agent._user_id):
                        potential.append(agent._user_id)

            if len(potential) == 1:
                return potential[0]
            else:
                return self.eliminate_agents(agent_id, location, potential)

        else:
            potential = {}
            local_agent = self.graphs[agent_id].get_local_agents(agent_id)
            reverse_local_agent = [(-x, -y) for (x, y) in local_agent]

            for agent in self.agents.values():
                if agent._user_id != agent_id:
                    local_agents = self.graphs[agent._user_id].get_local_agents(agent._user_id)
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
