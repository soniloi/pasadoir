class Generator:

    MAX_QUOTE_TOKENS = 100

    def __init__(self, rand):
        self.rand = rand


    def generate(self, transitions, initial=None):
        if not transitions:
            return None

        initial = self.resolve_initial_lookback(transitions, initial)
        if not initial:
            return None

        return self.generate_from_initial(transitions, initial)


    def resolve_initial_lookback(self, transitions, given_initial):
        if not given_initial:
            return self.generate_initial_lookback(transitions)

        lookback_length = len(next(iter(transitions.keys())))

        if len(given_initial) >= lookback_length:
            if given_initial in transitions:
                return given_initial
            return None

        initial_candidates = self.list_initial_lookback_candidates(transitions, given_initial)
        return initial_candidates[self.rand.rand_index(len(initial_candidates))]


    def generate_initial_lookback(self, transitions):
        transition_keys = list(transitions.keys())
        return transition_keys[self.rand.rand_index(len(transition_keys))]


    def list_initial_lookback_candidates(self, transitions, partial_lookback):
        return [lookback for lookback in transitions.keys() if self.matches_partially(partial_lookback, lookback)]


    def matches_partially(self, partial, tup):
        return all(partial[i] == tup[i] for i in range(0, len(partial)))


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
