import random

class Rand:

    def rand_index(self, max):
        return random.randint(0, max - 1)


    def shuffled(self, lst):
        result = list(lst)
        random.shuffle(result)
        return result
