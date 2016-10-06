import random

class Rand:
    """
    A wrapper class for python's "random" module. This allows for proper unit testing.

    Note that this class MUST BE USED AS A SINGLETON
    """

    def randrange(self, start, stop):
        return random.randrange(start, stop)


class RandRangeMock:

    def __init__(self, orderedIndicies):
        """
        Object intended for mocking the randrange method.

        :param orderedIndicies:
        The indicies that are mockingly generated by this mock. E.g. [2,1,3]
        means the first call to randrange will produce 2, the second 1, the third 3
        """
        self.orderedIndicies = orderedIndicies
        self.current = 0;

    def randrange(self, start, stop):
        next = self.orderedIndicies[self.current]
        self.current += 1
        return next

