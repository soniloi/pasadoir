import unittest
from unittest.mock import Mock

from generator import Generator

class TestGenerator(unittest.TestCase):

    def setUp(self):
        self.rand = Mock()
        self.generator = Generator(self.rand)


    def tearDown(self):
        pass


    def test_generate_no_source(self):
        quote = self.generator.generate({})

        self.assertEqual(quote, None)


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


    def test_generate_with_invalid_initial(self):
        transitions = {
            ("the", "cat") : ["sat"],
            ("cat", "sat") : ["on"],
            ("sat", "on") : ["the"],
            ("on", "the") : ["mat"],
        }
        self.rand.rand_index.return_value = 0

        quote = self.generator.generate(transitions, ("one", "day"))

        self.assertEqual(quote, None)


    def test_generate_with_valid_initial(self):
        transitions = {
            ("the", "cat") : ["sat"],
            ("cat", "sat") : ["on"],
            ("sat", "on") : ["the"],
            ("on", "the") : ["mat"],
        }
        self.rand.rand_index.return_value = 0

        quote = self.generator.generate(transitions, ("sat", "on"))

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
