class QuoteRequestProcessor:

    def __init__(self, transition_retriever, generator):
        self.transition_retriever = transition_retriever
        self.generator = generator


    def process(self, request):
        speaker_nicks, seed_tokens = self.split_request(request)
        speaker_names, transitions = self.transition_retriever.get(speaker_nicks)

        if transitions:
            quote = self.generator.generate(transitions, seed_tokens)
            if quote:
                return ("[{0}] {1}".format(":".join(speaker_names), " ".join(quote)))

        return ""


    def split_request(self, request):
        request_tokens = request.split()
        speaker_nicks = request_tokens[0].lower().split(":")
        seed_tokens = tuple(request_tokens[1:])
        return speaker_nicks, seed_tokens