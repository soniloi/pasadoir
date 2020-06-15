class RequestProcessor:

    # TODO: find a better place for these
    GENERATE_TRIGGER = "!"
    LOOKBACK_LENGTH = 2

    def __init__(self, source_retriever, transition_builder, generator):
        self.source_retriever = source_retriever
        self.transition_builder = transition_builder
        self.generator = generator


    def process(self, request):
        request = request.strip()
        if not request:
            return ""

        response = ""

        if request.startswith(RequestProcessor.GENERATE_TRIGGER):
            request_tokens = request.split()
            speaker_name = request_tokens[0][len(RequestProcessor.GENERATE_TRIGGER):]
            seed_tokens = tuple(request_tokens[1:])

            source = self.source_retriever.retrieve(speaker_name)
            transitions = self.transition_builder.build(source, RequestProcessor.LOOKBACK_LENGTH)
            quote = self.generator.generate(transitions, seed_tokens)

            if quote:
                response = ("[{0}] {1}".format(speaker_name, " ".join(quote)))

        return response
