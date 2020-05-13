from .helpers import Agent
from .helpers import BDIAgent
from collections import defaultdict
import numpy as np


class Builder(Agent, BDIAgent):
    def __init__(self, user, pw, print_json=False):
        Agent.__init__(self, user, pw, print_json)
        BDIAgent.__init__(self)
        self.current_task = None

    def run(self):
        while True:
            print(self.intention_queue)
            msg = self.receive_msg()
            if msg:
                if msg["type"] == "request-action":
                    if msg['content']['percept']['lastActionResult'] == 'failed_random':
                        self.add_last_action()
                    n_o, n_e, n_a = self.beliefs.update(msg, self._user_id)
                    intention_addition = self.get_intention(n_o, n_e, n_a)
                    self.add_intention(*intention_addition)
                    action = self.execute_intention()
                    if action:
                        request_id = self._get_request_id(msg)
                        self.send_request(self._add_request_id(action, request_id))
                    else:
                        print("Done with action")

    def get_intention(self):

        if not hasattr(self, 'ready'): 
            self.debug()

        if len(self.beliefs.tasks):
            # TODO: do actual task selection
            task = self.select_task()
            return  self.do_task(task)
        
        return tuple()

    
    def debug(self):
        self.beliefs.things['dispensers']['b0'].append((14, 3))
        self.beliefs.things['taskboards'].append((15, 2))
        self.beliefs.things['goals'].append((9, 16))
        self.ready = True

    def select_task(self):
        """
        Selects a task from the active tasks and returns it.
        """
        return self.beliefs.tasks[0]


    def do_task(self, task):
        if self.current_task != task['name']:
            intentions, args, contexts, descriptions = [], [], [], []

            # TODO: find the most efficient path going past the taskboard and dispensers to the goal.

            # get the nearest taskboard
            taskboard = self.get_nearest_taskboard()

            if not taskboard:
                return tuple()

            # get the nearest required dispensers
            requirements = self.get_required_blocks(task)
            dispensers = [self.get_nearest_dispenser(block_type) for block_type in requirements]
            
            if None in dispensers:
                return tuple()
            
            # get nearest goal location
            goal = self.get_nearest_goal()

            if not goal:
                return tuple()

            new_obs = [obs for sublist in self.beliefs.new_obs.values() for obs in sublist]
            intentions = [self.nav_to, self.accept, self.nav_to, self.request]
            args = [(taskboard, self._user_id, new_obs, True), (task['name']), (dispensers[0]), (self.beliefs.get_direction(self._user_id, self.beliefs.get_current(self._user_id).location)]
            
            # find shortest path from taskboard and dispenser, to goal.
            self.beliefs.things['dispensers']
            # go to taskboard to get the task

            # go to dispenser to retrieve blocks

            # go to goal location
            
            self.current_task = task['name']
            return intentions, args, contexts, descriptions
        return tuple()

    def get_required_blocks(self, task):
        required = defaultdict(list)
        for requirement in task['requirements']:
            required[requirement['type']].append((requirement['x'], requirement['y']))
        return required

    def get_nearest_dispenser(self, block_type):
        """
        Returns the nearest dispenser (using manhattan distance)
        or None if there is no known dispenser of the given type.

        Arguments
        ---------
        block_type: str
            The type of blocks the dispenser dispenses, e.g. 'b0'.
        """

        if block_type in self.beliefs.things['dispensers'] and self.beliefs.things['dispensers'][block_type]:
            return min(self.beliefs.things['dispensers'][block_type],
                key=lambda x: self.manhattan_distance(x, self.beliefs.get_curernt(self._user_id).location))
        return None

    def get_nearest_taskboard(self):
        """
        Returns the nearest taskboard (using manhattan distance)
        or None if there is no known taskboard.
        """

        if self.beliefs.things['taskboards']:
            return min(self.beliefs.things['taskboards'], 
                key=lambda x: self.manhattan_distance(x, self.beliefs.get_current(self._user_id).location))
        return None

    def get_nearest_goal(self):
        """
        Returns the nearest taskboard (using manhattan distance)
        or None if there is no known taskboard.
        """

        if self.beliefs.things['goals']:
            return min(self.beliefs.things['goals'], 
                key=lambda x: self.manhattan_distance(x, self.beliefs.get_current(self._user_id).location))
        return None



    def attach_block_from_dispenser(self):
        pass
    
    @staticmethod
    def manhattan_distance(coords1, coords2):
        return sum(abs(np.array(coords1, dtype=int) - np.array(coords2, dtype=int)))


if __name__ == "__main__":
    a_list = []
    for i in range(1, 2):
        a_list.append(Builder(f"agentA{i}", "1"))
        a_list[-1].start()