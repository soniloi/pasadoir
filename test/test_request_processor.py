import unittest
from unittest.mock import Mock

from request_processor import RequestProcessor

class TestRequestProcessor(unittest.TestCase):

    def setUp(self):
        self.saoi_transitions = {("is", "glas") : "iad", ("glas", "iad") : "na", ("iad", "na") : "cnoic", ("na", "cnoic") : "i", ("cnoic", "i") : "bhfad", ("i", "bhfad") : "uainn"}

        self.retriever = Mock()
        self.retriever.get.return_value = {}

        self.generator = Mock()
        self.generator.generate.return_value = ""

        self.processor = RequestProcessor(self.retriever, self.generator)


    def tearDown(self):
        pass


    def test_process_empty_request(self):
        response = self.processor.process("")

        self.assertEqual(response, "")
        self.retriever.get.assert_not_called()
        self.generator.generate.assert_not_called()


    def test_process_whitespace_request(self):
        response = self.processor.process("      \t  ")

        self.assertEqual(response, "")
        self.retriever.get.assert_not_called()
        self.generator.generate.assert_not_called()


    def test_process_unknown_request(self):
        response = self.processor.process("hello")

        self.assertEqual(response, "")
        self.retriever.get.assert_not_called()
        self.generator.generate.assert_not_called()


    def test_process_trigger_only(self):
        response = self.processor.process("!  ")

        self.assertEqual(response, "")
        self.retriever.get.assert_called_once_with("")
        self.generator.generate.assert_not_called()


    def test_process_generate_request_no_source(self):
        response = self.processor.process("!anaithnid")

        self.assertEqual(response, "")
        self.retriever.get.assert_called_once_with("anaithnid")
        self.generator.generate.assert_not_called()


    def test_process_generate_request_no_transitions(self):
        self.retriever.get.return_value = {}

        response = self.processor.process("!cat")

        self.assertEqual(response, "")
        self.retriever.get.assert_called_once_with("cat")
        self.generator.generate.assert_not_called()


    def test_process_generate_request_no_quote(self):
        self.retriever.get.return_value = self.saoi_transitions

        response = self.processor.process("!saoi lá amháin")

        self.assertEqual(response, "")
        self.retriever.get.assert_called_once_with("saoi")
        self.generator.generate.assert_called_once_with(self.saoi_transitions, ("lá", "amháin"))


    def test_process_generate_request_valid_no_whitespace(self):
        self.retriever.get.return_value = self.saoi_transitions
        self.generator.generate.return_value = ["na", "cnoic", "i", "bhfad", "uainn"]

        response = self.processor.process("!saoi")

        self.assertEqual(response, "[saoi] na cnoic i bhfad uainn")
        self.retriever.get.assert_called_once_with("saoi")
        self.generator.generate.assert_called_once_with(self.saoi_transitions, ())


    def test_process_generate_request_valid_with_whitespace(self):
        self.retriever.get.return_value = self.saoi_transitions
        self.generator.generate.return_value = ["na", "cnoic", "i", "bhfad", "uainn"]

        response = self.processor.process("     !saoi")

        self.assertEqual(response, "[saoi] na cnoic i bhfad uainn")
        self.retriever.get.assert_called_once_with("saoi")
        self.generator.generate.assert_called_once_with(self.saoi_transitions, ())


if __name__ == "__main__":
    unittest.main()
