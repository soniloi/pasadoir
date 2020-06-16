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
        self.cache = [CacheItem(age=-1, key=None, value=None)] * capacity


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


    def get(self, speaker_nick):
        min_age = self.cache[0].age
        min_age_index = 0

        speaker_name = self.aliases.get(speaker_nick, None)
        if not speaker_name:
            return None, {}

        for i, item in enumerate(self.cache):

            if item.key == speaker_name:
                self.update_cache_line(i, item.key, item.value)
                return speaker_name, item.value

            if item.age < min_age:
                min_age = item.age
                min_age_index = i

        transitions = {}
        source = self.source_retriever.retrieve(speaker_name)
        if source:
            transitions = self.transition_builder.build(source, CachedTransitionRetriever.LOOKBACK_LENGTH)
            if transitions:
                self.update_cache_line(min_age_index, speaker_name, transitions)

        return speaker_name, transitions


    def update_cache_line(self, index, key, value):
        self.cache[index] = CacheItem(self.age_counter, key, value)
        self.age_counter += 1
        #print(["{0}:{1}".format(item.key, item.age) for item in self.cache])
