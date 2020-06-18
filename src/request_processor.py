class RequestProcessor:

    # TODO: find a better place for this
    GENERATE_TRIGGER = "!"

    def __init__(self, transition_retriever, generator):
        self.transition_retriever = transition_retriever
        self.generator = generator


    def process(self, request):
        request = request.strip()
        if not request:
            return ""

        response = ""
        if request.startswith(RequestProcessor.GENERATE_TRIGGER):
            response = self.process_generate_request(request)
        return response


    def process_generate_request(self, request):
        speaker_nicks, seed_tokens = self.split_generate_request(request)
        speaker_names, transitions = self.transition_retriever.get(speaker_nicks)

        if transitions:
            quote = self.generator.generate(transitions, seed_tokens)
            if quote:
                return ("[{0}] {1}".format(":".join(speaker_names), " ".join(quote)))

        return ""


    def split_generate_request(self, request):
        request_tokens = request.split()
        speaker_token = request_tokens[0][len(RequestProcessor.GENERATE_TRIGGER):].lower()
        speaker_nicks = speaker_token.split(":")
        seed_tokens = tuple(request_tokens[1:])
        return speaker_nicks, seed_tokens
