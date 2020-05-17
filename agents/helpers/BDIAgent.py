from collections import namedtuple
from collections import deque


class BDIAgent():
    def __init__(self):
        self.intention_queue = deque()
        self.Template = namedtuple('Intention', ['intention', 'args',
                                                 'context', 'description'])
        self.previous_additions = None
        self.last_action = None

    def add_intention(self, intentions, args, contexts, descriptions):
        """
        Adds an intention (function call) with given args and context
        to the intention queue
        args:
            intentions: list of bound functions
            args: list of tuples of arguments per bound function
            contexts: list of contexts
            descriptions: list of descriptions
        """
        additions = [self.Template(i, a, c, d) for i, a, c, d
                     in zip(intentions, args, contexts, descriptions)]
        if additions != self.previous_additions:
            self.intention_queue.extend(additions)
            self.previous_additions = additions

    def add_last_action(self):
        self.intention_queue.appendleft(self.last_action)

    def drop_intention(self):
        for intention in self.intention_queue:
            # TODO: drop impossible intentions, an intention is impossible if
            # it's context is no longer believed
            pass

    def execute_intention(self):
        """
        Returns the action JSON resulting from the first intention in the queue
        """
        if len(self.intention_queue) > 0:
            last_action = self.intention_queue[0]
        else:
            return None
        action, args, context, description = last_action
        # Only remove intention from queue if it succeeds
        return_value, flag = action(*args)
        print(return_value)
        print(flag)
        if flag:
            self.intention_queue.popleft()
        return return_value
