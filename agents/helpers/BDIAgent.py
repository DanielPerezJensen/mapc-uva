from collections import namedtuple
from collections import deque


class BDIAgent():
    def __init__(self):
        self.intention_queue = deque()
        self.Template = namedtuple('Intention', ['intention', 'args',
                                                 'context', 'description',
                                                 'primitive'])
        self.previous_additions = None
        self.last_intention = None

    def add_intention(self, intentions, args, contexts,
                      descriptions, primitives):
        """
        Adds an intention (function call) with given args and context
        to the intention queue
        args:
            intentions: list of bound functions
            args: list of tuples of arguments per bound function
            contexts: list of contexts
            descriptions: list of descriptions
        """
        additions = [self.Template(i, a, c, d, p) for i, a, c, d, p
                     in zip(intentions, args, contexts,
                            descriptions, primitives)]

        if additions != self.previous_additions:
            self.intention_queue.extend(additions)
            self.previous_additions = additions

    def add_last_intention(self):
        self.intention_queue.appendleft(self.last_intention)

    def drop_intention(self):
        for intention in self.intention_queue:
            # TODO: drop impossible intentions, an intention is impossible if
            # it's context is no longer believed
            pass

    def reduce_intention(self, intention):
        """
        Reduces given non-primitive intention into (possibly)
        multiple non-primitive and primitive intentions

        args:
            intention
                a non-primitive intention that must be reduced
        """
        method, args, _, _, _ = intention
        intentions, args, contexts, descriptions, primitives = method(*args)

        reduced_additions = [self.Template(i, a, c, d, p) for i, a, c, d, p
                             in zip(intentions, args, contexts,
                                    descriptions, primitives)]

        # Reverse the intentions because extendleft reverses the intentions
        reduced_additions.reverse()
        self.intention_queue.extendleft(reduced_additions)

    def execute_intention(self):
        """
        Returns the action JSON resulting from the first intention in the queue
        """
        if len(self.intention_queue) > 0:
            self.last_intention = self.intention_queue[0]
        else:
            self.last_intention = None
            return None

        method, args, context, description, primitive = self.last_intention

        if not primitive:
            self.reduce_intention(self.intention_queue.popleft())
            self.execute_intention()

        else:
            # Only remove intention from queue if it succeeds
            return_value, flag = method(*args)
            if flag:
                self.intention_queue.popleft()
            return return_value
