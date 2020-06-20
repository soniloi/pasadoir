class SpeakerCollection:

    def __init__(self, source_retriever):
        self.source_retriever = source_retriever
        self.refresh()


    def refresh(self):
        self.speakers = self.build_alias_map()


    def build_alias_map(self):
        aliases = {}

        speaker_names = self.source_retriever.list_speakers()
        for name in speaker_names:
            aliases[name] = name

        merge_info_lines = self.source_retriever.get_merge_info()
        for line in merge_info_lines:
            self.add_alias_line(aliases, speaker_names, line)

        return aliases


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


    def resolve_names(self, speaker_nicks):
        speaker_names = []

        for nick in speaker_nicks:
            if nick in self.speakers:
                speaker_names.append(self.speakers[nick])

        return speaker_names
