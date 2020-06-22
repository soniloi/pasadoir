import datetime

import config

class Speaker:

    def __init__(self, name):
        self.name = name
        self.aliases = []


    def add_alias(self, alias):
        self.aliases.append(alias)


class SpeakerCollection:

    def __init__(self, source_retriever):
        self.source_retriever = source_retriever
        self.refresh()


    def refresh(self):
        self.source_info = self.build_source_info()
        self.speaker_names, self.speakers = self.build_speaker_map()


    def build_source_info(self):
        info = {}

        key_date = config.SOURCE_INFO_KEY_DATE
        key_channels = config.SOURCE_INFO_KEY_CHANNELS

        meta_lines = self.source_retriever.get_source_info()
        for line in meta_lines:
            tokens = line.split("=")

            if len(tokens) == 2:
                key = tokens [0]
                value = tokens[1]
                if key == key_date:
                    info[key_date] = datetime.datetime.fromtimestamp(int(value))
                elif key == key_channels:
                    info[key_channels] = value.split()

        return info


    def get_source_generated_date(self):
        return self.source_info.get(config.SOURCE_INFO_KEY_DATE, None)


    def get_source_channels(self):
        return self.source_info.get(config.SOURCE_INFO_KEY_CHANNELS, None)


    def get_speaker_count(self):
        return len(self.speaker_names)


    def build_speaker_map(self):
        speakers = {}

        speaker_names = self.source_retriever.list_speakers()
        for name in speaker_names:
            speakers[name] = Speaker(name)

        merge_info_lines = self.source_retriever.get_merge_info()
        for line in merge_info_lines:
            self.add_alias_line(speakers, speaker_names, line)

        return speaker_names, speakers


    def add_alias_line(self, speakers, speaker_names, line):
        tokens = line.strip().split()
        if len(tokens) < 2:
            return

        name = tokens[0]
        if not name in speaker_names:
            return

        secondaries = tokens[1:]
        for alias in secondaries:
            speakers[alias] = speakers[name]
            speakers[name].add_alias(alias)


    def resolve_speaker(self, nick):
        return self.speakers.get(nick, None)


    def resolve_names(self, nicks):
        names = []

        for nick in nicks:
            if nick in self.speakers:
                names.append(self.speakers[nick].name)

        return names
