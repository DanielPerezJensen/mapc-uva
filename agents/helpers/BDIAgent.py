from collections import namedtuple
from collections import deque


class BDIAgent():
    def __init__(self):
        self.intentions = deque()
        self.Template = namedtuple('Intention', ['intention', 'args',
                                                 'context', 'description'])

    def add_intention(self, intention, args, context, description):
        """
        Adds an intention (function call) with given args and context
        to the intention queue
        args:
            intention: bound function
            args: arguments for intention
            context
            description
        """
        self.intentions.append(self.Template(intention, args,
                                             context, description))

    def drop_intention(self):
        for intention in self.intentions:
            # TODO: drop impossible intentions, an intention is impossible if
            # it's context is no longer believed
            pass

    def execute_intention(self):
        """
        Returns the action JSON resulting from the first intention in the queue
        """
        intention = self.intentions[0]
        action = intention.intention(*intention.args)
        # Only remove intention from queue if it succeeds
        if action:
            self.intentions.pop()

        return action
