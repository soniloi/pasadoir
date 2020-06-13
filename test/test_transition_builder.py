import unittest

from transition_builder import TransitionBuilder

class TestTransitionBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = TransitionBuilder()


    def tearDown(self):
        pass


    def test_build_empty(self):
        transitions = self.builder.build([], 2)

        self.assertEqual(len(transitions), 0)


    def test_build_short_line(self):
        transitions = self.builder.build(["hello"], 2)

        self.assertEqual(len(transitions), 0)


    def test_build_single(self):
        source = [
            "the cat sat on the mat",
        ]

        transitions = self.builder.build(source, 2)

        self.assertEqual(len(transitions), 4)
        self. assertEqual(transitions[("the", "cat")], ["sat"])
        self. assertEqual(transitions[("cat", "sat")], ["on"])
        self. assertEqual(transitions[("sat", "on")], ["the"])
        self. assertEqual(transitions[("on", "the")], ["mat"])


    def test_build_multiple(self):
        source = [
            "humpty dumpty sat on a wall",
            "humpty dumpty had a great fall",
            "all the king's horses and all the king's men",
            "couldn't put humpty together again",
        ]

        transitions = self.builder.build(source, 2)

        self.assertEqual(len(transitions), 15)
        self. assertEqual(transitions[("humpty", "dumpty")], ["sat", "had"])
        self. assertEqual(transitions[("all", "the")], ["king's", "king's"])
        self. assertEqual(transitions[("the", "king's")], ["horses", "men"])


if __name__ == "__main__":
    unittest.main()
