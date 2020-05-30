if __name__ == "__main__":
    from helpers.agent import Agent
    from helpers.BDIAgent import BDIAgent

else:
    from .helpers import Agent
    from .helpers import BDIAgent


class Tester(Agent, BDIAgent):

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
            for neigh in self.neighbourhood(goal[0],goal[1]):
                if neigh.things:
                    
                    if list(neigh.things.values())[-1] == [('entity','B')]:
                        # print(ok)
                        count += 1
                    
            if count > max_enemies:
                best_goal = goal
                max_enemies = count
            print(count)
        return best_goal
            

    def test(self):
        """
        Prevents enemy from moving towards goal
        """
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
        loc = self.get_hot_goal()
        intentions = [self.nav_to]
        args = [(loc, self._user_id)]
        contexts = [tuple()]
        descriptions = ["Primitive"]
        primitive = [True]

        return intentions, args, contexts, descriptions, primitive


if __name__ == "__main__":
    a_list = []
    for i in range(1, 2):
        a_list.append(Tester(f"agentA{i}", "1"))
        a_list[i - 1].start()
