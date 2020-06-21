import unittest
from unittest.mock import Mock

from meta_request_processor import MetaRequestProcessor
from speaker_collection import Speaker

class TestMetaRequestProcessor(unittest.TestCase):

    def setUp(self):
        self.transition_retriever = Mock()
        self.speaker_collection = Mock()
        self.rand = Mock()
        self.processor = MetaRequestProcessor(self.transition_retriever, self.speaker_collection, self.rand)


    def tearDown(self):
        pass


    def make_speaker(self, name, aliases):
        speaker = Speaker(name)
        for alias in aliases:
            speaker.add_alias(alias)
        return speaker


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


    def test_process_stats_non_speaker(self):
        response = self.processor.process("stats")

        self.assertEqual(response, "")
        self.speaker_collection.resolve_speaker.assert_not_called()
        self.transition_retriever.get_by_name.assert_not_called()
        self.rand.shuffled.assert_not_called()


    def test_process_stats_speaker_unknown(self):
        self.speaker_collection.resolve_speaker.return_value = None

        response = self.processor.process("stats anaithnid")

        self.assertEqual(response, "")
        self.speaker_collection.resolve_speaker.assert_called_once_with("anaithnid")
        self.rand.shuffled.assert_not_called()
        self.transition_retriever.get_by_name.assert_not_called()


    def test_process_stats_speaker_no_aliases(self):
        self.speaker_collection.resolve_speaker.return_value = self.make_speaker("cainteoir", [])
        self.transition_retriever.get_by_name.return_value = {("bíonn", "gach") : ["tosú"], ("gach", "tosú") : ["lag"]}

        response = self.processor.process("stats cainteoir")

        self.assertEqual(response, "The speaker cainteoir has 2 transitions.")
        self.speaker_collection.resolve_speaker.assert_called_once_with("cainteoir")
        self.rand.shuffled.assert_not_called()
        self.transition_retriever.get_by_name.assert_called_once_with("cainteoir")


    def test_process_stats_speaker_one_alias(self):
        self.speaker_collection.resolve_speaker.return_value = self.make_speaker("cainteoir", ["cainteoir_"])
        self.transition_retriever.get_by_name.return_value = {("bíonn", "gach") : ["tosú"], ("gach", "tosú") : ["lag"]}

        response = self.processor.process("stats cainteoir")

        self.assertEqual(response, "The speaker cainteoir (AKA cainteoir_) has 2 transitions.")
        self.speaker_collection.resolve_speaker.assert_called_once_with("cainteoir")
        self.rand.shuffled.assert_not_called()
        self.transition_retriever.get_by_name.assert_called_once_with("cainteoir")


    def test_process_stats_speaker_two_aliases(self):
        cainteoir_aliases = ["cainteoir0", "cainteoir1"]
        self.speaker_collection.resolve_speaker.return_value = self.make_speaker("cainteoir", cainteoir_aliases)
        self.rand.shuffled.return_value = ["cainteoir1", "cainteoir0"]
        self.transition_retriever.get_by_name.return_value = {("bíonn", "gach") : ["tosú"], ("gach", "tosú") : ["lag"]}

        response = self.processor.process("stats cainteoir")

        self.assertEqual(response, "The speaker cainteoir (AKA cainteoir1 and cainteoir0) has 2 transitions.")
        self.speaker_collection.resolve_speaker.assert_called_once_with("cainteoir")
        self.rand.shuffled.assert_called_once_with(cainteoir_aliases)
        self.transition_retriever.get_by_name.assert_called_once_with("cainteoir")


    def test_process_stats_speaker_three_aliases(self):
        cainteoir_aliases = ["cainteoir0", "cainteoir1", "cainteoir2"]
        self.speaker_collection.resolve_speaker.return_value = self.make_speaker("cainteoir", cainteoir_aliases)
        self.rand.shuffled.return_value = ["cainteoir1", "cainteoir2", "cainteoir0"]
        self.transition_retriever.get_by_name.return_value = {("bíonn", "gach") : ["tosú"], ("gach", "tosú") : ["lag"]}

        response = self.processor.process("stats cainteoir")

        self.assertEqual(response, "The speaker cainteoir (AKA cainteoir1, cainteoir2, and cainteoir0) has 2 transitions.")
        self.speaker_collection.resolve_speaker.assert_called_once_with("cainteoir")
        self.rand.shuffled.assert_called_once_with(cainteoir_aliases)
        self.transition_retriever.get_by_name.assert_called_once_with("cainteoir")


    def test_process_stats_speaker_four_aliases(self):
        cainteoir_aliases = ["cainteoir0", "cainteoir1", "cainteoir2", "cainteoir3"]
        self.speaker_collection.resolve_speaker.return_value = self.make_speaker("cainteoir", cainteoir_aliases)
        self.rand.shuffled.return_value = ["cainteoir3", "cainteoir1", "cainteoir2", "cainteoir0"]
        self.transition_retriever.get_by_name.return_value = {("bíonn", "gach") : ["tosú"], ("gach", "tosú") : ["lag"]}

        response = self.processor.process("stats cainteoir")

        self.assertEqual(response, "The speaker cainteoir (AKA cainteoir3, cainteoir1, cainteoir2, and 1 other nick) has 2 transitions.")
        self.speaker_collection.resolve_speaker.assert_called_once_with("cainteoir")
        self.rand.shuffled.assert_called_once_with(cainteoir_aliases)
        self.transition_retriever.get_by_name.assert_called_once_with("cainteoir")


    def test_process_stats_speaker_multiple_aliases(self):
        cainteoir_aliases = ["cainteoir0", "cainteoir1", "cainteoir2", "cainteoir3", "cainteoir4", "cainteoir5"]
        self.speaker_collection.resolve_speaker.return_value = self.make_speaker("cainteoir", cainteoir_aliases)
        self.rand.shuffled.return_value = ["cainteoir3", "cainteoir5", "cainteoir0", "cainteoir4", "cainteoir2", "cainteoir1"]
        self.transition_retriever.get_by_name.return_value = {("bíonn", "gach") : ["tosú"], ("gach", "tosú") : ["lag"]}

        response = self.processor.process("stats cainteoir")

        self.assertEqual(response, "The speaker cainteoir (AKA cainteoir3, cainteoir5, cainteoir0, and 3 other nicks) has 2 transitions.")
        self.speaker_collection.resolve_speaker.assert_called_once_with("cainteoir")
        self.rand.shuffled.assert_called_once_with(cainteoir_aliases)
        self.transition_retriever.get_by_name.assert_called_once_with("cainteoir")


    def test_process_stats_speaker_called_with_alias(self):
        cainteoir_aliases = ["cainteoir0", "cainteoir1", "cainteoir2", "cainteoir3", "cainteoir4", "cainteoir5"]
        self.speaker_collection.resolve_speaker.return_value = self.make_speaker("cainteoir", cainteoir_aliases)
        self.rand.shuffled.return_value = ["cainteoir3", "cainteoir5", "cainteoir0", "cainteoir4", "cainteoir2", "cainteoir1"]
        self.transition_retriever.get_by_name.return_value = {("bíonn", "gach") : ["tosú"], ("gach", "tosú") : ["lag"]}

        response = self.processor.process("stats cainteoir4")

        self.assertEqual(response, "The speaker cainteoir (AKA cainteoir4, cainteoir3, cainteoir5, and 3 other nicks) has 2 transitions.")
        self.speaker_collection.resolve_speaker.assert_called_once_with("cainteoir4")
        self.rand.shuffled.assert_called_once_with(cainteoir_aliases)
        self.transition_retriever.get_by_name.assert_called_once_with("cainteoir")


if __name__ == "__main__":
    unittest.main()
