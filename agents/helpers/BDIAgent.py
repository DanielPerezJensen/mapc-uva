from collections import namedtuple
from collections import deque


class BDIAgent():
    def __init__(self):
        self.intention_queue = deque()
        self.Template = namedtuple('Intention', ['method', 'args',
                                                 'context', 'description',
                                                 'primitive'])
        self.previous_additions = None
        self.last_intention = None

    def add_intention(self, methods, args, contexts,
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
        additions = [self.Template(m, a, c, d, p) for m, a, c, d, p
                     in zip(methods, args, contexts,
                            descriptions, primitives)]

        self.intention_queue.extend(additions)
        self.previous_additions = additions

    def add_last_intention(self):
        self.intention_queue.appendleft(self.last_intention)

    def drop_intention(self, beliefs):
        """
        Checks next intention using context, if context is no longer believed
        drop intention and return True
        """
        if self.intention_queue:
            intention = self.intention_queue[0]
            _, _, context, _, _ = intention

            if context:
                crd, thing = context
                # Drop intention if the context is no longer believed
                if thing not in beliefs.get_node(crd).get_things(beliefs.step):
                    self.intention_queue.popleft()
                    return True

        return False

    def reduce_intention(self, intention):
        """
        Reduces given non-primitive intention into (possibly)
        multiple non-primitive and primitive intentions

        args:
            intention
                a non-primitive intention that must be reduced
        """
        method, args, _, _, _ = intention
        methods, args, contexts, descriptions, primitives = method(*args)

        reduced_additions = [self.Template(m, a, c, d, p) for m, a, c, d, p
                             in zip(methods, args, contexts,
                                    descriptions, primitives)]

        # Reverse the intentions because extendleft reverses the intentions
        reduced_additions.reverse()
        self.intention_queue.extendleft(reduced_additions)

    def execute_intention(self):
        """
        Returns the action JSON resulting from the first intention in the queue
        """

        if len(self.intention_queue) > 0:
            self.last_intention = self.intention_queue.popleft()

            method, args, context, description, primitive = self.last_intention

            if not primitive:
                self.reduce_intention(self.last_intention)
                return self.execute_intention()
            else:
                # Only remove intention from queue if it succeeds
                return_value = method(*args)
                if method.__name__ == "nav_to":
                    if return_value:
                        self.intention_queue.appendleft(self.last_intention)
                    else:
                        return self.execute_intention()
                return return_value

        else:
            self.last_intention = None
            return None
