from .helpers import Agent


class Builder(Agent):

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

        intentions, args, contexts, descriptions, primitive = self.test()
        return intentions, args, contexts, descriptions, primitive

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