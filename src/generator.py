class Generator:

    MAX_QUOTE_TOKENS = 100

    def __init__(self, rand):
        self.rand = rand


    def generate(self, transitions, initial=None):
        if not transitions:
            return None

        if not initial:
            initial = self.get_initial_lookback(transitions)
        elif not initial in transitions:
            return None

        return self.generate_from_initial(transitions, initial)


    def get_initial_lookback(self, transitions):
        transition_keys = list(transitions.keys())
        return transition_keys[self.rand.rand_index(len(transition_keys))]


    def generate_from_initial(self, transitions, lookback):
        quote = list(lookback)
        i = len(quote)

        while i < Generator.MAX_QUOTE_TOKENS and lookback in transitions:
            follow = self.get_follow(transitions, lookback)
            quote.append(follow)
            lookback = self.update_lookback(lookback, follow)
            i += 1

        return quote


    def get_follow(self, transitions, lookback):
        lookback_transitions = transitions[lookback]
        return lookback_transitions[self.rand.rand_index(len(lookback_transitions))]


    def update_lookback(self, lookback, follow):
        lookback_list = list(lookback[1:])
        lookback_list.append(follow)
        return tuple(lookback_list)
