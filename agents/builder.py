from .helpers import Agent


class Builder(Agent):
    def get_action(self, new_obstacle, new_empty, new_agents):

        # do some reasoning with new_obstacle, new_empty, new_agents and self.graph

        return self.nav_to((5, 10), new_obstacle + new_empty + new_agents)

