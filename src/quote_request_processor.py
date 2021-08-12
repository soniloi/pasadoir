from enum import Enum


class QuoteDirection(Enum):
    BIDI = 0
    FORWARD = 1
    REVERSE = 2


class QuoteStyle:
  CLEAR = "\x0f"
  BOLD = "\x02"
  COLOUR = "\x03"


class QuoteColour:
  WHITE = "0"
  BLACK = "1"
  BLUE = "2"
  GREEN = "3"
  RED = "4"
  BROWN = "5"
  PURPLE = "6"
  ORANGE = "7"
  YELLOW = "8"
  LIGHT_GREEN = "9"
  CYAN = "10"
  LIGHT_CYAN = "11"
  LIGHT_BLUE = "12"
  PINK = "13"
  GREY = "14"
  LIGHT_GREY = "15"


class QuoteRequestProcessor:

    SEED_HIGHLIGHT_TEMPLATE = QuoteStyle.BOLD + QuoteStyle.COLOUR + QuoteColour.YELLOW + "{0}" + QuoteStyle.CLEAR

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

        seed_start_index = 0
        seed_end_index = 0

        if direction == QuoteDirection.FORWARD:
            quote = self.generator.generate(forward_transitions, seed_tokens)
            seed_start_index = 0
            seed_end_index = len(seed_tokens)

        elif direction == QuoteDirection.REVERSE:
            reversed_seed_tokens = tuple(list(reversed(seed_tokens)))
            quote = self.generator.generate(reverse_transitions, reversed_seed_tokens)
            quote = list(reversed(quote))
            seed_start_index = len(quote) - len(seed_tokens)
            seed_end_index = len(quote)

        elif direction == QuoteDirection.BIDI:
            quote_forward = self.generator.generate(forward_transitions, seed_tokens)
            reversed_seed_tokens = tuple(list(reversed(seed_tokens)))
            quote_reverse = self.generator.generate(reverse_transitions, reversed_seed_tokens)
            quote_reverse = list(reversed(quote_reverse))
            word_cutoff_index, seed_start_index, seed_end_index = self.get_bidi_quote_indices(quote_forward, quote_reverse, seed_tokens)
            quote = quote_reverse + quote_forward[word_cutoff_index:]

        if not quote:
            return ""

        return self.format_quote(quote, speaker_names, seed_tokens, seed_start_index, seed_end_index)


    def split_request(self, request):
        request_tokens = request.split()
        speaker_nicks = request_tokens[0].lower().split(":")
        seed_tokens = tuple(request_tokens[1:])
        return speaker_nicks, seed_tokens


    def get_bidi_quote_indices(self, quote_forward, quote_reverse, seed_tokens):
        reverse_length = len(quote_reverse)
        forward_length = len(quote_forward)
        seed_length = len(seed_tokens)
        if quote_forward and quote_reverse:
            return seed_length, reverse_length - seed_length, reverse_length
        if quote_forward:
            return 0, 0, seed_length
        return 0, reverse_length - seed_length, reverse_length


    def format_quote(self, quote, speaker_names, seed_tokens, seed_start_index, seed_end_index):
        highlighted_quote = quote
        if seed_start_index != seed_end_index:
            before_seed = quote[0:seed_start_index]
            seed = [self.SEED_HIGHLIGHT_TEMPLATE.format(" ".join(quote[seed_start_index:seed_end_index]))]
            after_seed = quote[seed_end_index:]
            highlighted_quote = before_seed + seed + after_seed
        return ("[{0}] {1}".format(":".join(speaker_names), " ".join(highlighted_quote)))
