from .helpers import Agent


class Spy(Agent):

    def get_intention(self):
        """
        Gets intentions of this type of agent.
        """
        # Example of what to return:
        #   intentions = [self.nav_to]
        #   args = [((3, 3), self._user_id)]
        #   contexts = [tuple()]
        #   descriptions = ["Primitive"]
        #   primitive = [True]
        #
        # return intentions, args, contexts, descriptions, primitive
        pass

    def follow_enemy(self):
        """
        Main task
        """
        pass

    def patrol_highways(self):
        """
        Main task
        """
        pass

    def classify_task(self):
        """
        Sub task
        """
        pass

    def classify_enemy(self):
        """
        Sub task
        """
        pass
