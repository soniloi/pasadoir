import unittest
from unittest.mock import call, Mock

from quote_request_processor import QuoteDirection, QuoteRequestProcessor

class TestQuoteRequestProcessor(unittest.TestCase):

    def setUp(self):
        self.saoi_transitions = {("fillean", "an") : ["feall"], ("an", "feall") : ["ar"], ("feall", "ar") : ["an"], ("ar", "an") : ["bhfeallaire"]}
        self.saoi_transitions_reversed = {("feall", "an") : ["filleann"], ("ar", "feall") : ["an"], ("an", "ar") : ["feall"], ("bhfeallaire", "an") : ["ar"]}
        self.eolai_saoi_transitions = {("bíonn", "blas") : ["ar"], ("blas", "ar") : ["an"], ("ar", "an") : ["mbeagán", "bhfeallaire"], ("fillean", "an") : ["feall"], ("an", "feall") : ["ar"], ("feall", "ar") : ["an"]}

        self.retriever = Mock()
        self.retriever.get.return_value = (["saoi"], {})

        self.generator = Mock()
        self.generator.generate.return_value = ""

        self.processor = QuoteRequestProcessor(self.retriever, self.generator)


    def tearDown(self):
        pass


    def test_process_generate_request_no_source(self):
        response = self.processor.process("anaithnid")

        self.assertEqual(response, "")
        self.retriever.get.assert_called_once_with(["anaithnid"], reverse=False)
        self.generator.generate.assert_not_called()


    def test_process_generate_request_no_transitions(self):
        self.retriever.get.return_value = (["saoi"], {})

        response = self.processor.process("cat")

        self.assertEqual(response, "")
        self.retriever.get.assert_called_once_with(["cat"], reverse=False)
        self.generator.generate.assert_not_called()


    def test_process_generate_request_no_quote(self):
        self.retriever.get.side_effect = [(["saoi"], self.saoi_transitions), (["saoi"], self.saoi_transitions_reversed)]
        self.generator.generate.side_effect = [[], []]

        response = self.processor.process("saoi lá amháin")

        self.assertEqual(response, "")
        self.retriever.get.assert_has_calls([
            call(["saoi"], reverse=False),
            call(["saoi"], reverse=True),
        ])
        self.generator.generate.assert_has_calls([
            call(self.saoi_transitions, ("lá", "amháin")),
            call(self.saoi_transitions_reversed, ("amháin", "lá")),
        ])


    def test_process_generate_request_valid_no_whitespace(self):
        self.retriever.get.return_value = (["saoi"], self.saoi_transitions)
        self.generator.generate.return_value = ["feall", "ar", "an", "bhfeallaire"]

        response = self.processor.process("saoi")

        self.assertEqual(response, "[saoi] feall ar an bhfeallaire")
        self.retriever.get.assert_called_once_with(["saoi"], reverse=False)
        self.generator.generate.assert_called_once_with(self.saoi_transitions, ())


    def test_process_generate_request_valid_with_whitespace(self):
        self.retriever.get.return_value = (["saoi"], self.saoi_transitions)
        self.generator.generate.return_value = ["feall", "ar", "an", "bhfeallaire"]

        response = self.processor.process("     saoi")

        self.assertEqual(response, "[saoi] feall ar an bhfeallaire")
        self.retriever.get.assert_called_once_with(["saoi"], reverse=False)
        self.generator.generate.assert_called_once_with(self.saoi_transitions, ())


    def test_process_generate_request_valid_aliased(self):
        self.retriever.get.return_value = (["saoi"], self.saoi_transitions)
        self.generator.generate.return_value = ["feall", "ar", "an", "bhfeallaire"]

        response = self.processor.process("saoi_")

        self.assertEqual(response, "[saoi] feall ar an bhfeallaire")
        self.retriever.get.assert_called_once_with(["saoi_"], reverse=False)
        self.generator.generate.assert_called_once_with(self.saoi_transitions, ())


    def test_process_generate_request_valid_uppercase(self):
        self.retriever.get.return_value = (["saoi"], self.saoi_transitions)
        self.generator.generate.return_value = ["feall", "ar", "an", "bhfeallaire"]

        response = self.processor.process("SAOI")

        self.assertEqual(response, "[saoi] feall ar an bhfeallaire")
        self.retriever.get.assert_called_once_with(["saoi"], reverse=False)
        self.generator.generate.assert_called_once_with(self.saoi_transitions, ())


    def test_process_generate_request_valid_with_seed_single(self):
        self.retriever.get.side_effect = [(["saoi"], self.saoi_transitions), (["saoi"], self.saoi_transitions_reversed)]
        self.generator.generate.side_effect = [["ar", "an", "bhfeallaire"], ["ar", "feall"]]

        response = self.processor.process("saoi ar")

        self.assertEqual(response, "[saoi] feall ar an bhfeallaire")
        self.retriever.get.assert_has_calls([
            call(["saoi"], reverse=False),
            call(["saoi"], reverse=True),
        ])
        self.generator.generate.assert_has_calls([
            call(self.saoi_transitions, ("ar",)),
            call(self.saoi_transitions_reversed, ("ar",)),
        ])


    def test_process_generate_request_valid_with_seed_double(self):
        self.retriever.get.side_effect = [(["saoi"], self.saoi_transitions), (["saoi"], self.saoi_transitions_reversed)]
        self.generator.generate.side_effect = [["ar", "an", "bhfeallaire"], ["an", "ar", "feall"]]

        response = self.processor.process("saoi ar an")

        self.assertEqual(response, "[saoi] feall ar an bhfeallaire")
        self.retriever.get.assert_has_calls([
            call(["saoi"], reverse=False),
            call(["saoi"], reverse=True),
        ])
        self.generator.generate.assert_has_calls([
            call(self.saoi_transitions, ("ar", "an")),
            call(self.saoi_transitions_reversed, ("an", "ar")),
        ])


    def test_process_generate_request_valid_merge(self):
        self.retriever.get.return_value = (["eolaí", "saoi"], self.eolai_saoi_transitions)
        self.generator.generate.return_value = ["bíonn", "blas", "ar", "an", "bhfeallaire"]

        response = self.processor.process("eolaí:saoi")

        self.assertEqual(response, "[eolaí:saoi] bíonn blas ar an bhfeallaire")
        self.retriever.get.assert_called_once_with(["eolaí", "saoi"], reverse=False)
        self.generator.generate.assert_called_once_with(self.eolai_saoi_transitions, ())


    def test_process_generate_request_valid_forward(self):
        self.retriever.get.return_value = (["saoi"], self.saoi_transitions)
        self.generator.generate.return_value = ["filleann", "an", "feall", "ar", "an", "bhfeallaire"]

        response = self.processor.process("saoi filleann an", options={"direction" : QuoteDirection.FORWARD})

        self.assertEqual(response, "[saoi] filleann an feall ar an bhfeallaire")
        self.retriever.get.assert_called_once_with(["saoi"], reverse=False)
        self.generator.generate.assert_called_once_with(self.saoi_transitions, ("filleann", "an"))


    def test_process_generate_request_valid_reverse(self):
        self.retriever.get.return_value = (["saoi"], self.saoi_transitions_reversed)
        self.generator.generate.return_value = ["bhfeallaire", "an", "ar", "feall", "an", "filleann"]

        response = self.processor.process("saoi an bhfeallaire", options={"direction" : QuoteDirection.REVERSE})

        self.assertEqual(response, "[saoi] filleann an feall ar an bhfeallaire")
        self.retriever.get.assert_called_once_with(["saoi"], reverse=True)
        self.generator.generate.assert_called_once_with(self.saoi_transitions_reversed, ("bhfeallaire", "an"))


if __name__ == "__main__":
    unittest.main()
