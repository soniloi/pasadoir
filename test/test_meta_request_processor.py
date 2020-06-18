import unittest
from unittest.mock import Mock

from meta_request_processor import MetaRequestProcessor

class TestMetaRequestProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = MetaRequestProcessor()


    def tearDown(self):
        pass


    def test_process_unknown(self):
        response = self.processor.process("raiméis")

        self.assertEqual(response, "")


    def test_process_help(self):
        response = self.processor.process("help")

        self.assertEqual(response, "Pasadóir is a bot that impersonates people based on their history")


if __name__ == "__main__":
    unittest.main()
