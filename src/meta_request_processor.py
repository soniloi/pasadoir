import config
import message_templates

class MetaRequestProcessor:

    def __init__(self, transition_retriever, speaker_collection):
        self.transition_retriever = transition_retriever
        self.speaker_collection = speaker_collection


    def process(self, request):
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


    COMMANDS = {
        "help" : process_help,
        "refresh" : process_refresh,
    }
