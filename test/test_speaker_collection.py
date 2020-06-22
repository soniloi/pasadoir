import datetime
import unittest
from unittest.mock import Mock

from speaker_collection import SpeakerCollection

class TestSpeakerCollection(unittest.TestCase):

    def setUp(self):
        self.setup_source_retriever()
        self.collection = SpeakerCollection(self.source_retriever)


    def tearDown(self):
        pass


    def setup_source_retriever(self):
        self.source_retriever = Mock()
        self.source_retriever.retrieve.return_value = []
        self.source_retriever.list_speakers.return_value = ["beag", "eagnaí", "eolaí", "fáidh", "folamh", "saoi"]
        self.source_retriever.get_merge_info.return_value = ["anaithnid\tanaithnid2", "eolaí", "saoi\tsaoi__\tsaoi0"]
        self.source_retriever.get_source_info.return_value = ["date=695280768", "channels=#farraige #oileán #rúin", "unknownkey=unknownvalue"]


    def test_init_aliasing_and_source_info(self):
        self.assertEqual(len(self.collection.speakers), 8)
        self.assertEqual(self.collection.speakers["beag"].name, "beag")
        self.assertEqual(self.collection.speakers["eagnaí"].name, "eagnaí")
        self.assertEqual(self.collection.speakers["eolaí"].name, "eolaí")
        self.assertEqual(self.collection.speakers["fáidh"].name, "fáidh")
        self.assertEqual(self.collection.speakers["folamh"].name, "folamh")
        self.assertEqual(self.collection.speakers["saoi"].name, "saoi")
        self.assertEqual(self.collection.speakers["saoi__"].name, "saoi")
        self.assertEqual(self.collection.speakers["saoi0"].name, "saoi")
        saoi = self.collection.speakers["saoi"]
        self.assertEqual(len(saoi.aliases), 2)
        self.assertTrue("saoi__" in saoi.aliases)
        self.assertTrue("saoi0" in saoi.aliases)

        self.assertEqual(len(self.collection.source_info), 2)
        self.assertEqual(self.collection.source_info["date"], datetime.datetime.utcfromtimestamp(695280768))
        self.assertEqual(self.collection.source_info["channels"], ["#farraige", "#oileán", "#rúin"])


    def test_resolve_names_single_known_same(self):
        names = self.collection.resolve_names(["saoi"])

        self.assertEqual(["saoi"], names)


    def test_resolve_names_single_known_aliased(self):
        names = self.collection.resolve_names(["saoi__"])

        self.assertEqual(["saoi"], names)


    def test_resolve_names_single_unknown(self):
        names = self.collection.resolve_names(["anaithnid"])

        self.assertEqual([], names)


    def test_resolve_names_multiple_known(self):
        names = self.collection.resolve_names(["fáidh", "saoi0", "eolaí"])

        self.assertEqual(["fáidh", "saoi", "eolaí"], names)


    def test_resolve_names_mixed_known_and_unknown(self):
        names = self.collection.resolve_names(["fáidh", "anaithnid", "saoi"])

        self.assertEqual(["fáidh", "saoi"], names)


if __name__ == "__main__":
    unittest.main()
