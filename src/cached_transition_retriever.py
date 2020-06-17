from collections import namedtuple

CacheItem = namedtuple("CacheItem", ["age", "key", "value"])

class CachedTransitionRetriever:

    LOOKBACK_LENGTH = 2
    DEFAULT_CAPACITY = 12

    def __init__(self, source_retriever, transition_builder, capacity=DEFAULT_CAPACITY):
        self.source_retriever = source_retriever
        self.transition_builder = transition_builder
        self.age_counter = 0
        self.speaker_names, self.aliases = self.build_alias_map()
        self.cache = [CacheItem(age=-1, key="", value={})] * capacity
        self.max_merged_speakers = capacity - 1


    def build_alias_map(self):
        aliases = {}

        speaker_names = self.source_retriever.list_speakers()
        for name in speaker_names:
            aliases[name] = name

        merge_info_lines = self.source_retriever.get_merge_info()
        for line in merge_info_lines:
            self.add_alias_line(aliases, speaker_names, line)

        return speaker_names, aliases


    def add_alias_line(self, aliases, speaker_names, line):
        tokens = line.strip().split()
        if len(tokens) < 2:
            return

        primary = tokens[0]
        if not primary in speaker_names:
            return

        secondaries = tokens[1:]
        for alias in secondaries:
            aliases[alias] = primary


    def get(self, speaker_nicks):
        speaker_names = self.resolve_speaker_names(speaker_nicks)
        if len(speaker_names) < 1:
            return None, {}

        transitions = self.get_by_name(speaker_names[0])
        if len(speaker_names) > 1:
            transitions = self.copy_transitions(transitions)

        for speaker_name in speaker_names[1:]:
            additional_transitions = self.get_by_name(speaker_name)
            self.merge_transitions(transitions, additional_transitions)

        return speaker_names, transitions


    def resolve_speaker_names(self, speaker_nicks):
        speaker_names = []

        for nick in speaker_nicks[:self.max_merged_speakers]:
            if nick in self.aliases:
                speaker_names.append(self.aliases[nick])

        speaker_names.sort()
        return speaker_names


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
            transitions = self.transition_builder.build(source, CachedTransitionRetriever.LOOKBACK_LENGTH)
            if transitions:
                self.update_cache_line(min_age_index, speaker_name, transitions)

        return transitions


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


    def update_cache_line(self, index, key, value):
        self.cache[index] = CacheItem(self.age_counter, key, value)
        self.age_counter += 1
        #print(["{0}:{1}:{2}".format(item.key, item.age, len(item.value)) for item in self.cache])
