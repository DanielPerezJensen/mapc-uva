import random
import time

if __name__ == "__main__":
    from helpers.agent import Agent
    from helpers.BDIAgent import BDIAgent

else:
    from .helpers import Agent
    from .helpers import BDIAgent


class Generator(Agent, BDIAgent):

    def __init__(self, user, pw, print_json=False):
        Agent.__init__(self, user, pw, print_json)
        BDIAgent.__init__(self)
        self.local_random = random.Random()
        seed = int(''.join(str(ord(c)) for c in user))
        self.local_random.seed(seed)
        self.paths = []

    def run(self):

        last_msg = "init"

        curr_path = []

        while True:

            time.sleep(0.2)  # uncomment to add delay per step in agent.

            msg = self.receive_msg()

            if msg:

                if msg["type"] == "request-action":

                    request_id = self._get_request_id(msg)

                    if msg['content']['percept']['lastActionResult'] == \
                            'failed_random':
                        self.add_last_intention()

                    self.beliefs.update(msg, self._user_id)

                    if not self.intention_queue:

                        intention_addition = self.get_intention()
                        self.add_intention(*intention_addition)

                    action = self.execute_intention()

                    # Perform move commands and add current location
                    # to current path to use later
                    if action:
                        curr_path.append(self.current_location())
                        self.send_request(self._add_request_id(action,
                                          request_id))
                    else:
                        action = self.skip()
                        self.send_request(
                            self._add_request_id(action, request_id))
                        self.pretty_print("Done with action", request_id)

                    # If the goal has been reached, append current path
                    if self.current_goal == self.current_location():

                        self.paths.append(curr_path)
                        curr_path = []

            # If the simulation is ended (socket connection closed)
            # write all paths to a file
            elif not last_msg and not msg:
                with open("data.txt", "a") as text_file:
                    for path in self.paths:
                        print(path)
                        text_file.write(";".join(str(i) for i in path))
                        text_file.write("\n")
                return

            last_msg = msg

    def get_intention(self):
        return self.walk_to_random_goal()

    def walk_to_random_goal(self):
        goal = (self.local_random.randint(-5, 5),
                self.local_random.randint(-5, 5))

        self.current_goal = goal

        # Create and return the new intentions
        intentions = [self.nav_to]
        args = [(goal, self._user_id)]
        contexts = [tuple()]
        descriptions = ["navRandomly"]
        primitives = [True]

        return intentions, args, contexts, descriptions, primitives


a_list = []
b_list = []

for i in range(1, 5 + 1):
    a_list.append(Generator(f"agentA{i}", "1"))
    a_list[-1].start()
    b_list.append(Generator(f"agentB{i}", "1"))
    b_list[-1].start()
