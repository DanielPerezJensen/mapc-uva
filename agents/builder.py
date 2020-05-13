from .helpers import Agent


class Builder(Agent):
    def get_action(self):

        # do some reasoning with new_obstacle, new_empty, new_agents and self.graph
        
        # i want to navigate to (5,10)
        action = self.nav_to((-2, -12))
        
        # check if arrived or no path is possible
        if not action:
            action = self.skip()
        
        return action

