from collections import namedtuple, OrderedDict

import config

CacheItem = namedtuple("CacheItem", ["age", "key", "value"])

class CachedTransitionRetriever:

    def __init__(self, source_retriever, transition_builder, speaker_collection,
            capacity=config.CACHE_CAPACITY, min_lookbacks=config.CACHE_MIN_LOOKBACKS):
        self.source_retriever = source_retriever
        self.transition_builder = transition_builder
        self.speaker_collection = speaker_collection
        self.capacity = capacity
        self.min_lookbacks = min_lookbacks
        self.max_merged_speakers = self.capacity - 1
        self.refresh()


    def refresh(self):
        self.cache = [CacheItem(age=-1, key="", value={})] * self.capacity
        self.age_counter = 0


    def get(self, speaker_nicks):
        speaker_names = self.resolve_speaker_names(speaker_nicks)
        if len(speaker_names) < 1:
            return None, {}

        if len(speaker_names) == 1:
            return speaker_names, self.get_by_name(speaker_names[0])

        return speaker_names, self.get_merged(speaker_names)


    def resolve_speaker_names(self, speaker_nicks):
        names = self.speaker_collection.resolve_names(speaker_nicks)
        trimmed_names = list(OrderedDict.fromkeys(names))[:self.max_merged_speakers]
        trimmed_names.sort()
        return trimmed_names


    def get_by_name(self, speaker_name):
        min_age = self.cache[0].age
        min_age_index = 0

        for i, item in enumerate(self.cache):

            if item.key == speaker_name:
                self.update_cache_line(i, item.key, item.value)
                return item.value

            if item.age < min_age:
                min_age = item.age
                min_age_index = i

        transitions = {}
        source = self.source_retriever.retrieve(speaker_name)
        if source:
            transitions = self.transition_builder.build(source, config.LOOKBACK_LENGTH)
            if transitions:
                self.update_cache_line(min_age_index, speaker_name, transitions)

        return transitions


    def get_merged(self, speaker_names):
        key = self.make_merged_speaker_key(speaker_names)

        transitions = self.get_by_name_cached_only(key)
        if not transitions:
            transitions = self.copy_transitions(self.get_by_name(speaker_names[0]))
            for speaker_name in speaker_names[1:]:
                additional_transitions = self.get_by_name(speaker_name)
                self.merge_transitions(transitions, additional_transitions)

            if transitions:
                self.update_cache_line(self.get_min_cache_age_index(), key, transitions)

        return transitions


    def make_merged_speaker_key(self, speaker_names):
        return ":".join(speaker_names)


    def get_by_name_cached_only(self, speaker_name):
        for i, item in enumerate(self.cache):
            if item.key == speaker_name:
                self.update_cache_line(i, item.key, item.value)
                return item.value
        return {}


    def get_min_cache_age_index(self):
        min_age = self.cache[0].age
        min_age_index = 0

        for i, item in enumerate(self.cache):
            if item.age < min_age:
                min_age = item.age
                min_age_index = i

        return min_age_index


    def copy_transitions(self, original):
        result = {}
        for lookback, follows in original.items():
            result[lookback] = list(follows)
        return result


    def merge_transitions(self, transitions, additional_transitions):
        for lookback, follows in additional_transitions.items():
            if not lookback in transitions:
                transitions[lookback] = []
            transitions[lookback] += follows


    def update_cache_line(self, index, key, transitions):
        if len(transitions) >= self.min_lookbacks:
            self.cache[index] = CacheItem(self.age_counter, key, transitions)
            self.age_counter += 1
        #print(["{0}|{1}|{2}".format(item.key, item.age, len(item.value)) for item in self.cache])
