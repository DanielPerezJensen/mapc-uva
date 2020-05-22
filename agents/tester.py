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
        return self.test()

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
        intentions = [self.nav_to]
        args = [((3, 3), self._user_id)]
        contexts = [tuple()]
        descriptions = ["Primitive"]
        primitive = [True]

        return intentions, args, contexts, descriptions, primitive


if __name__ == "__main__":
    a_list = []
    for i in range(1, 2):
        a_list.append(Tester(f"agentA{i}", "1"))
        a_list[i - 1].start()
