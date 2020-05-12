if __name__ == "__main__":
    from helpers.agent import Agent
    from helpers.BDIAgent import BDIAgent
else:
    from .helpers import Agent


class Tester(Agent, BDIAgent):

    def __init__(self, user, pw, print_json=False):
        Agent.__init__(self, user, pw, print_json)
        BDIAgent.__init__(self)

    def run(self):
        while True:
            print(self.intention_queue)
            msg = self.receive_msg()
            if msg:
                if msg["type"] == "request-action":
                    if msg['content']['percept']['lastActionResult'] == 'failed_random':
                        self.add_last_action()
                    self.beliefs.update(msg)
                    intention_addition = self.get_intention()
                    self.add_intention(*intention_addition)
                    action = self.execute_intention()
                    if action:
                        request_id = self._get_request_id(msg)
                        self.send_request(self._add_request_id(action, request_id))
                    else:
                        print("Done with action")

    def get_intention(self):
        return self.test()

    def test(self):
        """
        Prevents enemy from moving towards goal
        """

        # TODO: Detect what goal state builder is moving towards
        # perhaps in connection with the spy

        # TODO: Detect if blocking is possible somehow

        # TODO: Stand in between builder and goal state
        # return self.nav_to, ((1, 2),), tuple(), "preventMoving"
        intentions = [self.nav_to]
        args = [(1, 2)]
        contexts = [tuple()]
        descriptions = ["RetrievingBlock"]

        return intentions, args, contexts, descriptions

if __name__ == "__main__":
    a_list = []
    for i in range(1, 2):
        a_list.append(Tester(f"agentA{i}", "1"))
        a_list[i - 1].start()