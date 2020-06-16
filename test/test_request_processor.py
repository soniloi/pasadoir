import unittest
from unittest.mock import Mock

from request_processor import RequestProcessor

class TestRequestProcessor(unittest.TestCase):

    def setUp(self):
        self.saoi_transitions = {("fillean", "an") : ["feall"], ("an", "feall") : ["ar"], ("feall", "ar") : ["an"], ("ar", "an") : ["bhfeallaire"]}
        self.eolai_saoi_transitions = {("bíonn", "blas") : ["ar"], ("blas", "ar") : ["an"], ("ar", "an") : ["mbeagán", "bhfeallaire"], ("fillean", "an") : ["feall"], ("an", "feall") : ["ar"], ("feall", "ar") : ["an"]}

        self.retriever = Mock()
        self.retriever.get.return_value = (["saoi"], {})

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
        self.retriever.get.assert_called_once_with([""])
        self.generator.generate.assert_not_called()


    def test_process_generate_request_no_source(self):
        response = self.processor.process("!anaithnid")

        self.assertEqual(response, "")
        self.retriever.get.assert_called_once_with(["anaithnid"])
        self.generator.generate.assert_not_called()


    def test_process_generate_request_no_transitions(self):
        self.retriever.get.return_value = (["saoi"], {})

        response = self.processor.process("!cat")

        self.assertEqual(response, "")
        self.retriever.get.assert_called_once_with(["cat"])
        self.generator.generate.assert_not_called()


    def test_process_generate_request_no_quote(self):
        self.retriever.get.return_value = (["saoi"], self.saoi_transitions)

        response = self.processor.process("!saoi lá amháin")

        self.assertEqual(response, "")
        self.retriever.get.assert_called_once_with(["saoi"])
        self.generator.generate.assert_called_once_with(self.saoi_transitions, ("lá", "amháin"))


    def test_process_generate_request_valid_no_whitespace(self):
        self.retriever.get.return_value = (["saoi"], self.saoi_transitions)
        self.generator.generate.return_value = ["feall", "ar", "an", "bhfeallaire"]

        response = self.processor.process("!saoi")

        self.assertEqual(response, "[saoi] feall ar an bhfeallaire")
        self.retriever.get.assert_called_once_with(["saoi"])
        self.generator.generate.assert_called_once_with(self.saoi_transitions, ())


    def test_process_generate_request_valid_with_whitespace(self):
        self.retriever.get.return_value = (["saoi"], self.saoi_transitions)
        self.generator.generate.return_value = ["feall", "ar", "an", "bhfeallaire"]

        response = self.processor.process("     !saoi")

        self.assertEqual(response, "[saoi] feall ar an bhfeallaire")
        self.retriever.get.assert_called_once_with(["saoi"])
        self.generator.generate.assert_called_once_with(self.saoi_transitions, ())


    def test_process_generate_request_valid_aliased(self):
        self.retriever.get.return_value = (["saoi"], self.saoi_transitions)
        self.generator.generate.return_value = ["feall", "ar", "an", "bhfeallaire"]

        response = self.processor.process("!saoi_")

        self.assertEqual(response, "[saoi] feall ar an bhfeallaire")
        self.retriever.get.assert_called_once_with(["saoi_"])
        self.generator.generate.assert_called_once_with(self.saoi_transitions, ())


    def test_process_generate_request_valid_merge(self):
        self.retriever.get.return_value = (["eolaí", "saoi"], self.eolai_saoi_transitions)
        self.generator.generate.return_value = ["bíonn", "blas", "ar", "an", "bhfeallaire"]

        response = self.processor.process("!eolaí:saoi")

        self.assertEqual(response, "[eolaí:saoi] bíonn blas ar an bhfeallaire")
        self.retriever.get.assert_called_once_with(["eolaí", "saoi"])
        self.generator.generate.assert_called_once_with(self.eolai_saoi_transitions, ())


if __name__ == "__main__":
    unittest.main()
