from generator import Generator
from rand import Rand
from source_retriever import SourceRetriever
from transition_builder import TransitionBuilder

class RequestHandler:

    # TODO: find a better place for these
    GENERATE_TRIGGER = "!"
    LOOKBACK_LENGTH = 2

    def __init__(self, source_dir):
        self.source_retriever = SourceRetriever(source_dir)
        self.transition_builder = TransitionBuilder()
        self.generator = Generator(Rand())


    def handle(self, request):
        response = None
        request_tokens = request.split()
        speaker_token = request_tokens[0]

        if speaker_token.startswith(RequestHandler.GENERATE_TRIGGER):
            speaker_name = speaker_token[len(RequestHandler.GENERATE_TRIGGER):]
            source = self.source_retriever.retrieve(speaker_name)
            transitions = self.transition_builder.build(source, RequestHandler.LOOKBACK_LENGTH)
            quote = self.generator.generate(transitions)

            if quote:
                response = ("[{0}] {1}".format(speaker_name, " ".join(quote)))

        return response
