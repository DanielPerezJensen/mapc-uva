if __name__ == "__main__":
    from helpers.agent import Agent
    from helpers.BDIAgent import BDIAgent

else:
    from .helpers import Agent
    from .helpers import BDIAgent

import numpy as np

class TesterA(Agent, BDIAgent):

    def __init__(self, user, pw, print_json=False):
        Agent.__init__(self, user, pw, print_json)
        BDIAgent.__init__(self)

    def run(self):
        while True:
            msg = self.receive_msg()
            if msg:
                if msg["type"] == "request-action":
                    if msg['content']['percept']['lastActionResult'] == \
                            'failed_random':
                        self.add_last_intention()

                    self.beliefs.update(msg, self._user_id)
                    intention_addition = self.get_intention()
                    self.add_intention(*intention_addition)
                    action = self.execute_intention()
                    if action:
                        request_id = self._get_request_id(msg)
                        self.send_request(self._add_request_id(action,
                                          request_id))
                    else:
                        print("Done with action")

    def get_intention(self):
        return self.test3()

    def neighbourhood(self, x, y, depth=1):
        """
        Reasoning: Returns all nodes within the neighbourhood of a given
        coordinate to a given depth, a depth of 2 would return all nodes that
        are no more than 2 blocks away from the agent.

        args:
            x: int
                x coordinate
            y: int
                y coordinate
            depth=1: int
                depth of neighbourhood
        """
        node_list = []

        for i in range(x - depth, x + depth + 1):
            for j in range(y - depth, y + depth + 1):
                if (i != x or j != y):
                    n = self.beliefs.get_node((i, j))
                    if n:
                        node_list.append(n)

        return node_list


    def get_crowded_goal(self):
        """
        Returns the goal state with the highest amount of enemy agents around
        """
        max_enemies = 0
        best_goal = tuple()
        for goal in self.beliefs.things['goals']:
            count = 0
            for neigh in self.neighbourhood(goal[0],goal[1],depth=5):
                if neigh.things:
                    if list(neigh.things.values())[-1] == [('entity','B')]:
                        count += 1
                    
            if count > max_enemies:
                best_goal = goal
                max_enemies = count
            # print(count)
        return best_goal

    def enemy_closing_in(self,agent_id):
        """
        """ 
        old_locs = self.beliefs.get_local_agent_locations(agent_id, team='B')
        new_locs = self.beliefs.get_local_agent_locations(agent_id, team='B')
        return self.same_agent_closing_in(old_locs,new_locs)
        
        # if new_locs != old_locs:
            # for i in range(len(new_locs)+1):
                # print('ok')
        
    def same_agent_closing_in(self,old_locs,new_locs):
        """ 
        Returns True if the agent on the old location is the agent on the new location
        """
        own_loc = self.current_info('location')
        for old_loc in old_locs:
            for new_loc in new_locs:
                
                if self.same_agent(old_loc,new_loc):
                    # blocks_around_enemy = self.blocks_around_node(self.get_node(new_loc))
                    distance_old_x = abs(old_loc[0] - own_loc[0])
                    distance_new_x = abs(new_loc[0] - own_loc[0])
                    distance_old_y = abs(old_loc[1] - own_loc[1]) 
                    distance_new_y = abs(new_loc[1] - own_loc[1])
                    if ((distance_old_x > (distance_new_x) or (distance_old_y > distance_new_y))):
                    # if ((distance_old_x > (distance_new_x) or (distance_old_y > distance_new_y)) and blocks_around_enemy > 1:
                        return new_loc
  
        return own_loc

    def blocks_around_node(self, node):
        """
        Reasoning: Returns the amount of blocks around a given node
        """

        count = 0

        x, y = node.location

        for node in self.neighbourhood(x, y):
            things = node.get_things(self.beliefs.step)
            for itemtype, _ in things:
                if itemtype == "block":
                    count += 1

        return count
    @staticmethod
    def same_agent(old_loc,new_loc):
        """ 
        Returns True if the agent on the old location is the agent on the new location
        """
        abs_x = abs(old_loc[0] - new_loc[0])
        abs_y = abs(old_loc[1] - new_loc[1]) 
        
        if  (abs_x == 1 and abs_y == 0) or (abs_x == 0 and abs_y == 1):
            return True

        return False

    





    
    # def all_different_goals(self):

    # def center_goal_state(self, goals):
    #     center_x =max(goals,key=lambda item:item[1])[0] - min(goals,key=lambda item:item[1])[0]
    #     center_y = max(goals,key=lambda item:item[1])[1] - min(goals,key=lambda item:item[1])[1] 
    #     return (center_x,center_y)

    def test(self):
        """
        Prevents enemy from moving towards goal
        """
        loc = self.get_crowded_goal()
        intentions = [self.nav_to, self.test3]
        args = [(loc, self._user_id), tuple()]
        contexts = [tuple(), tuple()]
        descriptions = ["RetrievingBlock", "NonPrimitive"]
        primitive = [True, False]

        return intentions, args, contexts, descriptions, primitive

    def test2(self):
        intentions = [self.test3, self.nav_to]
        args = [tuple(), ((2, 2), self._user_id)]
        contexts = [tuple(), tuple()]
        descriptions = ["NonPrimitive", "Primitive"]
        primitive = [False, True]

        return intentions, args, contexts, descriptions, primitive

    def test3(self):
        
        loc = self.enemy_closing_in(self._user_id)
        intentions = [self.nav_to]
        args = [(loc, self._user_id)]
        contexts = [tuple()]
        descriptions = ["Primitive"]
        primitive = [True]

        return intentions, args, contexts, descriptions, primitive
    
    @staticmethod
    def _manhattan_distance(coords1, coords2):
        return sum(abs(np.array(coords1, dtype=int) -
                       np.array(coords2, dtype=int)))





class TesterB(Agent, BDIAgent):

    def __init__(self, user, pw, print_json=False):
        Agent.__init__(self, user, pw, print_json)
        BDIAgent.__init__(self)

    def run(self):
        while True:
            msg = self.receive_msg()
            if msg:
                if msg["type"] == "request-action":
                    if msg['content']['percept']['lastActionResult'] == \
                            'failed_random':
                        self.add_last_intention()

                    self.beliefs.update(msg, self._user_id)
                    intention_addition = self.get_intention()
                    self.add_intention(*intention_addition)
                    action = self.execute_intention()
                    if action:
                        request_id = self._get_request_id(msg)
                        self.send_request(self._add_request_id(action,
                                          request_id))
                    else:
                        print("Done with action")

    def get_intention(self):
        return self.test3()

    def neighbourhood(self, x, y, depth=1):
        """
        Reasoning: Returns all nodes within the neighbourhood of a given
        coordinate to a given depth, a depth of 2 would return all nodes that
        are no more than 2 blocks away from the agent.

        args:
            x: int
                x coordinate
            y: int
                y coordinate
            depth=1: int
                depth of neighbourhood
        """
        node_list = []

        for i in range(x - depth, x + depth + 1):
            for j in range(y - depth, y + depth + 1):
                if (i != x or j != y):
                    n = self.beliefs.get_node((i, j))
                    if n:
                        node_list.append(n)

        return node_list


    def get_crowded_goal(self):
        
        # print(self.beliefs.things['goals'])
        max_enemies = 0
        best_goal = tuple()
        for goal in self.beliefs.things['goals']:
            count = 0
            for neigh in self.neighbourhood(goal[0],goal[1],depth=5):
                if neigh.things:
                    if list(neigh.things.values())[-1] == [('entity','B')]:
                        # print(ok)
                        count += 1
                    
            if count > max_enemies:
                best_goal = goal
                max_enemies = count
            # print(count)print
        return best_goal

    def _get_nearest_goal(self):
        """
        Returns the nearest taskboard (using manhattan distance)
        or None if there is no known taskboard.
        """

        if self.beliefs.things['goals']:
            return min(self.beliefs.things['goals'],
                       key=lambda x: self._manhattan_distance(x,
                       self.beliefs.get_current(self._user_id).location))
        return None
    # def all_different_goals(self):

    # def center_goal_state(self, goals):
    #     center_x =max(goals,key=lambda item:item[1])[0] - min(goals,key=lambda item:item[1])[0]
    #     center_y = max(goals,key=lambda item:item[1])[1] - min(goals,key=lambda item:item[1])[1] 
    #     return (center_x,center_y)

    def test(self):
        """
        Prevents enemy from moving towards goal
        """
        self.beliefs
        intentions = [self.nav_to, self.test2]
        args = [((1, 1), self._user_id), tuple()]
        contexts = [tuple(), tuple()]
        descriptions = ["RetrievingBlock", "NonPrimitive"]
        primitive = [True, False]

        return intentions, args, contexts, descriptions, primitive

    def test2(self):
        intentions = [self.test3, self.nav_to]
        args = [tuple(), ((2, 2), self._user_id)]
        contexts = [tuple(), tuple()]
        descriptions = ["NonPrimitive", "Primitive"]
        primitive = [False, True]

        return intentions, args, contexts, descriptions, primitive

    def test3(self):
        loc = self._get_nearest_goal()
        intentions = [self.nav_to]
        args = [(loc, self._user_id)]
        contexts = [tuple()]
        descriptions = ["Primitive"]
        primitive = [True]

        return intentions, args, contexts, descriptions, primitive

    @staticmethod
    def _manhattan_distance(coords1, coords2):
        return sum(abs(np.array(coords1, dtype=int) -
                       np.array(coords2, dtype=int)))


if __name__ == "__main__":
    a_list = []
    for i in range(1, 3):
        a_list.append(TesterA(f"agentA{i}", "1"))
        a_list[i - 1].start()

    b_list = []
    for i in range(1, 3):
        b_list.append(TesterB(f"agentB{i}", "1"))
        b_list[i - 1].start()
