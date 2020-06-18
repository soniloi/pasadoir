import config
import message_templates

class MetaRequestProcessor:

    def process(self, request):
        request = request.lower().split()
        command = request[0]
        arguments = request[1:]

        if command in MetaRequestProcessor.COMMANDS:
            return MetaRequestProcessor.COMMANDS[command](self, arguments)

        return ""


    def process_help(self, arguments):
        return message_templates.META_HELP.format(config.BOT_NAME)


    COMMANDS = {
        "help" : process_help,
    }
