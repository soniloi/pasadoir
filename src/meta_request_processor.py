import config
import message_templates

class MetaRequestProcessor:

    STATS_DATE_FORMAT = "%Y-%m-%d at %H.%M.%S"

    def __init__(self, transition_retriever, speaker_collection, rand, start_time):
        self.transition_retriever = transition_retriever
        self.speaker_collection = speaker_collection
        self.rand = rand
        self.start_time = start_time


    def process(self, request, options={}):
        request = request.lower().split()
        command = request[0]
        arguments = request[1:]

        if command in MetaRequestProcessor.COMMANDS:
            return MetaRequestProcessor.COMMANDS[command](self, arguments)

        return ""


    def process_help(self, arguments):
        return message_templates.META_HELP.format(config.BOT_NAME)


    def process_refresh(self, arguments):
        self.speaker_collection.refresh()
        self.transition_retriever.refresh()
        return message_templates.META_REFRESH


    def process_stats(self, arguments):
        if arguments:
            return self.process_speaker_stats(arguments[0])
        return self.process_general_stats()


    def process_general_stats(self):
        speaker_count = self.speaker_collection.get_speaker_count()
        start_date = self.format_date_for_stats(self.start_time)
        source_gen_date = self.format_date_for_stats(self.speaker_collection.get_source_generated_date())
        source_channels = self.format_list_for_stats(self.speaker_collection.get_source_channels())
        return message_templates.META_STATS_GENERAL.format(speaker_count, start_date, source_gen_date,
            source_channels)


    def format_date_for_stats(self, date):
        return date.strftime(MetaRequestProcessor.STATS_DATE_FORMAT)


    def format_list_for_stats(self, lis):
        return ", ".join(lis[:-1]) + ", and " + lis[-1]


    def process_speaker_stats(self, speaker_nick):
        speaker = self.speaker_collection.resolve_speaker(speaker_nick)
        if not speaker:
            return ""

        speaker_aliases = self.format_speaker_aliases_for_stats(list(speaker.aliases), speaker_nick, speaker.name)

        transitions = self.transition_retriever.get_by_name(speaker.name)
        transition_count = self.count_transitions(transitions)

        return message_templates.META_STATS_SPEAKER.format(speaker.name, speaker_aliases, transition_count)


    #TODO: fix this up and put elsewhere
    def format_speaker_aliases_for_stats(self, speaker_aliases, given_nick, speaker_name):
        if len(speaker_aliases) < 1:
            return ""

        outer_template = "(AKA {0}) "
        if len(speaker_aliases) == 1:
            return outer_template.format(speaker_aliases[0])

        speaker_aliases = self.rand.shuffled(speaker_aliases)
        if given_nick != speaker_name:
            speaker_aliases.remove(given_nick)
            speaker_aliases = [given_nick] + speaker_aliases

        if len(speaker_aliases) == 2:
            inner_template = "{0} and {1}"
            return outer_template.format(inner_template.format(speaker_aliases[0], speaker_aliases[1]))

        additional_alias_count = len(speaker_aliases) - config.STATS_SPEAKER_ALIAS_COUNT

        if additional_alias_count < 1:
            inner_template = "{0}, and {1}"
            return outer_template.format(inner_template.format(", ".join(speaker_aliases[:-1]), speaker_aliases[-1]))

        speaker_aliases = speaker_aliases[:config.STATS_SPEAKER_ALIAS_COUNT]
        if additional_alias_count == 1:
            inner_template = "{0}, and 1 other nick"
            return outer_template.format(inner_template.format(", ".join(speaker_aliases)))

        inner_template = "{0}, and {1} other nicks"
        return outer_template.format(inner_template.format(", ".join(speaker_aliases), additional_alias_count))


    def count_transitions(self, transitions):
        return sum(len(follows) for follows in transitions.values())


    COMMANDS = {
        "help" : process_help,
        "refresh" : process_refresh,
        "stats" : process_stats,
    }
