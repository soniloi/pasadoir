from enum import Enum


class QuoteDirection(Enum):
    BIDI = 0
    FORWARD = 1
    REVERSE = 2


class QuoteRequestProcessor:

    def __init__(self, transition_retriever, generator):
        self.transition_retriever = transition_retriever
        self.generator = generator


    def process(self, request, options={}):
        speaker_nicks, seed_tokens = self.split_request(request)
        direction = options.get("direction", QuoteDirection.BIDI)
        if direction == QuoteDirection.BIDI and not seed_tokens:
            direction = QuoteDirection.FORWARD

        speaker_names = []
        forward_transitions = {}
        reverse_transitions = {}

        if direction == QuoteDirection.FORWARD or direction == QuoteDirection.BIDI:
            speaker_names, forward_transitions = self.transition_retriever.get(speaker_nicks, reverse=False)
        if direction == QuoteDirection.REVERSE or direction == QuoteDirection.BIDI:
            speaker_names, reverse_transitions = self.transition_retriever.get(speaker_nicks, reverse=True)

        if not forward_transitions and not reverse_transitions:
            return ""

        if direction == QuoteDirection.FORWARD:
            quote = self.generator.generate(forward_transitions, seed_tokens)

        elif direction == QuoteDirection.REVERSE:
            reversed_seed_tokens = tuple(list(reversed(seed_tokens)))
            quote = self.generator.generate(reverse_transitions, reversed_seed_tokens)
            quote = list(reversed(quote))

        elif direction == QuoteDirection.BIDI:
            quote_forward = self.generator.generate(forward_transitions, seed_tokens)
            reversed_seed_tokens = tuple(list(reversed(seed_tokens)))
            quote_reverse = self.generator.generate(reverse_transitions, reversed_seed_tokens)
            quote_reverse = list(reversed(quote_reverse))
            quote = quote_reverse + quote_forward[len(seed_tokens):]

        if not quote:
            return ""

        return ("[{0}] {1}".format(":".join(speaker_names), " ".join(quote)))


    def split_request(self, request):
        request_tokens = request.split()
        speaker_nicks = request_tokens[0].lower().split(":")
        seed_tokens = tuple(request_tokens[1:])
        return speaker_nicks, seed_tokens

