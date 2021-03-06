import unittest
from unittest.mock import Mock

from quote_generator import QuoteGenerator

class TestQuoteGenerator(unittest.TestCase):

    def setUp(self):
        self.rand = Mock()
        self.generator = QuoteGenerator(self.rand)


    def tearDown(self):
        pass


    def test_generate_no_source(self):
        quote = self.generator.generate({})

        self.assertEqual(quote, [])


    def test_generate_single_choice(self):
        transitions = {
            ("the", "cat") : ["sat"],
            ("cat", "sat") : ["on"],
            ("sat", "on") : ["the"],
            ("on", "the") : ["mat"],
        }
        self.rand.rand_index.return_value = 0

        quote = self.generator.generate(transitions)

        self.assertEqual(quote, ["the", "cat", "sat", "on", "the", "mat"])


    def test_generate_with_unknown_initial(self):
        transitions = {
            ("the", "cat") : ["sat"],
            ("cat", "sat") : ["on"],
            ("sat", "on") : ["the"],
            ("on", "the") : ["mat"],
        }
        self.rand.rand_index.return_value = 0

        quote = self.generator.generate(transitions, ("one", "day"))

        self.assertEqual(quote, [])


    def test_generate_with_overlong_initial(self):
        transitions = {
            ("the", "cat") : ["sat"],
            ("cat", "sat") : ["on"],
            ("sat", "on") : ["the"],
            ("on", "the") : ["mat"],
        }
        self.rand.rand_index.return_value = 0

        quote = self.generator.generate(transitions, ("the", "cat", "sat"))

        self.assertEqual(quote, [])


    def test_generate_with_full_valid_initial(self):
        transitions = {
            ("the", "cat") : ["sat"],
            ("cat", "sat") : ["on"],
            ("sat", "on") : ["the"],
            ("on", "the") : ["mat"],
        }
        self.rand.rand_index.return_value = 0

        quote = self.generator.generate(transitions, ("sat", "on"))

        self.assertEqual(quote, ["sat", "on", "the", "mat"])


    def test_generate_with_partial_invalid_initial(self):
        transitions = {
            ("the", "cat") : ["sat"],
            ("cat", "sat") : ["on"],
            ("sat", "on") : ["the"],
            ("on", "the") : ["mat"],
        }
        self.rand.rand_index.return_value = 0

        quote = self.generator.generate(transitions, ("blah",))

        self.assertEqual(quote, [])


    def test_generate_with_partial_valid_initial(self):
        transitions = {
            ("the", "cat") : ["sat"],
            ("cat", "sat") : ["on"],
            ("sat", "on") : ["the"],
            ("on", "the") : ["mat"],
        }
        self.rand.rand_index.return_value = 0

        quote = self.generator.generate(transitions, ("sat",))

        self.assertEqual(quote, ["sat", "on", "the", "mat"])


    def test_generate_endless_repetition(self):
        transitions = {
            ("a", "a") : ["a"],
        }
        self.rand.rand_index.return_value = 0

        quote = self.generator.generate(transitions)

        self.assertEqual(len(quote), 100)
        for word in quote:
            self.assertEqual(word, "a")


if __name__ == "__main__":
    unittest.main()
