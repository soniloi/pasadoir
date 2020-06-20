import unittest
from unittest.mock import Mock

from meta_request_processor import MetaRequestProcessor

class TestMetaRequestProcessor(unittest.TestCase):

    def setUp(self):
        self.transition_retriever = Mock()
        self.speaker_collection = Mock()
        self.processor = MetaRequestProcessor(self.transition_retriever, self.speaker_collection)


    def tearDown(self):
        pass


    def test_process_unknown(self):
        response = self.processor.process("raiméis")

        self.assertEqual(response, "")


    def test_process_help(self):
        response = self.processor.process("help")

        self.assertEqual(response, "Pasadóir is a bot that impersonates people based on their history.")


    def test_process_refresh(self):
        response = self.processor.process("refresh")

        self.assertEqual(response, "Refreshed.")
        self.transition_retriever.refresh.assert_called_once()
        self.speaker_collection.refresh.assert_called_once()


if __name__ == "__main__":
    unittest.main()
