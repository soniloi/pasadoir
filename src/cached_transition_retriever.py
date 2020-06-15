from collections import namedtuple

CacheItem = namedtuple("CacheItem", ["age", "key", "value"])

class CachedTransitionRetriever:

    LOOKBACK_LENGTH = 2
    DEFAULT_CAPACITY = 12

    def __init__(self, source_retriever, transition_builder, capacity=DEFAULT_CAPACITY):
        self.source_retriever = source_retriever
        self.transition_builder = transition_builder
        self.age_counter = 0
        self.cache = []
        for i in range(0, capacity):
            self.cache.append(CacheItem(age=-1, key=None, value=None))


    def get(self, speaker_name):
        min_age = self.cache[0].age
        min_age_index = 0

        for i, item in enumerate(self.cache):

            if item.key == speaker_name:
                self.cache[i] = CacheItem(self.age_counter, item.key, item.value)
                self.age_counter += 1
                return item.value

            if item.age < min_age:
                min_age = item.age
                min_age_index = i

        source = self.source_retriever.retrieve(speaker_name)
        if source:
            transitions = self.transition_builder.build(source, CachedTransitionRetriever.LOOKBACK_LENGTH)
            if transitions:
                self.cache[min_age_index] = CacheItem(self.age_counter, speaker_name, transitions)
                self.age_counter += 1
                return transitions

        return {}
