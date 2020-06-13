class TransitionBuilder:

    def build(self, lines, lookback_length):
        transitions = {}

        for line in lines:
            words = line.split()
            if len(words) >= lookback_length:
                self.process_source_line(words, transitions, lookback_length)

        return transitions


    def process_source_line(self, words, transitions, lookback_length):
        lookback = tuple(words[:lookback_length])

        for i, follow in enumerate(words[lookback_length:]):
            if not lookback in transitions:
                transitions[lookback] = []
            transitions[lookback].append(follow)

            lookback = self.update_lookback(lookback, follow, lookback_length)


    def update_lookback(self, lookback, follow, lookback_length):
        next_lookback = list(lookback[1:lookback_length])
        next_lookback.append(follow)
        return tuple(next_lookback)
