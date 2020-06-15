import unittest
from unittest.mock import Mock

from request_processor import RequestProcessor

class TestRequestProcessor(unittest.TestCase):

    def setUp(self):
        self.saoi_transitions = {("is", "glas") : "iad", ("glas", "iad") : "na", ("iad", "na") : "cnoic", ("na", "cnoic") : "i", ("cnoic", "i") : "bhfad", ("i", "bhfad") : "uainn"}

        self.retriever = Mock()
        self.retriever.retrieve.return_value = []

        self.builder = Mock()
        self.builder.build.return_value = {}

        self.generator = Mock()
        self.generator.generate.return_value = ""

        self.processor = RequestProcessor(self.retriever, self.builder, self.generator)


    def tearDown(self):
        pass


    def test_process_empty_request(self):
        response = self.processor.process("")

        self.assertEqual(response, "")
        self.retriever.retrieve.assert_not_called()
        self.builder.build.assert_not_called()
        self.generator.generate.assert_not_called()


    def test_process_whitespace_request(self):
        response = self.processor.process("      \t  ")

        self.assertEqual(response, "")
        self.retriever.retrieve.assert_not_called()
        self.builder.build.assert_not_called()
        self.generator.generate.assert_not_called()


    def test_process_unknown_request(self):
        response = self.processor.process("hello")

        self.assertEqual(response, "")
        self.retriever.retrieve.assert_not_called()
        self.builder.build.assert_not_called()
        self.generator.generate.assert_not_called()


    def test_process_trigger_only(self):
        response = self.processor.process("!  ")

        self.assertEqual(response, "")
        self.retriever.retrieve.assert_called_once_with("")
        self.builder.build.assert_called_once_with([], 2)
        self.generator.generate.assert_called_once_with({}, ())


    def test_process_generate_request_no_source(self):
        response = self.processor.process("!anaithnid")

        self.assertEqual(response, "")
        self.retriever.retrieve.assert_called_once_with("anaithnid")
        self.builder.build.assert_called_once_with([], 2)
        self.generator.generate.assert_called_once_with({}, ())


    def test_process_generate_request_no_transitions(self):
        self.retriever.retrieve.return_value = ["mew"]

        response = self.processor.process("!cat")

        self.assertEqual(response, "")
        self.retriever.retrieve.assert_called_once_with("cat")
        self.builder.build.assert_called_once_with(["mew"], 2)
        self.generator.generate.assert_called_once_with({}, ())


    def test_process_generate_request_no_quote(self):
        self.retriever.retrieve.return_value = ["is glas iad na cnoic i bhfad uainn"]
        self.builder.build.return_value = self.saoi_transitions

        response = self.processor.process("!saoi lá amháin")

        self.assertEqual(response, "")
        self.retriever.retrieve.assert_called_once_with("saoi")
        self.builder.build.assert_called_once_with(["is glas iad na cnoic i bhfad uainn"], 2)
        self.generator.generate.assert_called_once_with(self.saoi_transitions, ("lá", "amháin"))


    def test_process_generate_request_valid_no_whitespace(self):
        self.retriever.retrieve.return_value = ["is glas iad na cnoic i bhfad uainn"]
        self.builder.build.return_value = self.saoi_transitions
        self.generator.generate.return_value = ["na", "cnoic", "i", "bhfad", "uainn"]

        response = self.processor.process("!saoi")

        self.assertEqual(response, "[saoi] na cnoic i bhfad uainn")
        self.retriever.retrieve.assert_called_once_with("saoi")
        self.builder.build.assert_called_once_with(["is glas iad na cnoic i bhfad uainn"], 2)
        self.generator.generate.assert_called_once_with(self.saoi_transitions, ())


    def test_process_generate_request_valid_with_whitespace(self):
        self.retriever.retrieve.return_value = ["is glas iad na cnoic i bhfad uainn"]
        self.builder.build.return_value = self.saoi_transitions
        self.generator.generate.return_value = ["na", "cnoic", "i", "bhfad", "uainn"]

        response = self.processor.process("     !saoi")

        self.assertEqual(response, "[saoi] na cnoic i bhfad uainn")
        self.retriever.retrieve.assert_called_once_with("saoi")
        self.builder.build.assert_called_once_with(["is glas iad na cnoic i bhfad uainn"], 2)
        self.generator.generate.assert_called_once_with(self.saoi_transitions, ())


if __name__ == "__main__":
    unittest.main()
