import unittest
from unittest.mock import call, Mock

from cached_transition_retriever import CachedTransitionRetriever

class TestCachedTransitionRetriever(unittest.TestCase):

    def setUp(self):
        self.setup_data()
        self.setup_source_retriever()
        self.setup_transition_builder()
        self.transition_retriever = CachedTransitionRetriever(self.source_retriever, self.transition_builder, 3)


    def tearDown(self):
        pass


    def setup_data(self):
        self.saoi_source = ["aithníonn ciaróg ciaróg eile"]
        self.faidh_source = ["is leor nod don eolach"]
        self.eolai_source = ["is binn béal ina thost"]
        self.eagnai_source = ["bíonn gach tosú lag"]
        self.folamh_source = []
        self.saoi_transitions = {("fillean", "an") : ["feall"], ("an", "feall") : ["ar"], ("feall", "ar") : ["an"], ("ar", "an") : ["bhfeallaire"]}
        self.faidh_transitions = {("is", "leor") : ["nod"], ("leor", "nod") : ["don"], ("nod", "don") : ["eolach"]}
        self.eolai_transitions = {("bíonn", "blas") : ["ar"], ("blas", "ar") : ["an"], ("ar", "an") : ["mbeagán"]}
        self.eagnai_transitions = {("bíonn", "gach") : ["tosú"], ("gach", "tosú") : ["lag"]}
        self.eolai_saoi_transitions = {("bíonn", "blas") : ["ar"], ("blas", "ar") : ["an"], ("ar", "an") : ["mbeagán", "bhfeallaire"], ("fillean", "an") : ["feall"], ("an", "feall") : ["ar"], ("feall", "ar") : ["an"]}

    def setup_source_retriever(self):
        self.source_retriever = Mock()
        self.source_retriever.retrieve.return_value = []
        self.source_retriever.list_speakers.return_value = ["eagnaí", "eolaí", "fáidh", "folamh", "saoi"]
        self.source_retriever.get_merge_info.return_value = ["anaithnid\tanaithnid2", "eolaí", "saoi\tsaoi__\tsaoi0"]


    def setup_transition_builder(self):
        self.transition_builder = Mock()
        self.transition_builder.build.return_value = {}


    def test_init_aliasing(self):
        self.assertEqual(len(self.transition_retriever.aliases), 7)
        self.assertEqual(self.transition_retriever.aliases["eagnaí"], "eagnaí")
        self.assertEqual(self.transition_retriever.aliases["eolaí"], "eolaí")
        self.assertEqual(self.transition_retriever.aliases["fáidh"], "fáidh")
        self.assertEqual(self.transition_retriever.aliases["folamh"], "folamh")
        self.assertEqual(self.transition_retriever.aliases["saoi"], "saoi")
        self.assertEqual(self.transition_retriever.aliases["saoi__"], "saoi")
        self.assertEqual(self.transition_retriever.aliases["saoi0"], "saoi")


    def test_get_unknown_speaker(self):
        self.source_retriever.retrieve.return_value = []

        speaker_names, transitions = self.transition_retriever.get(["anaithnid"])

        self.assertIsNone(speaker_names)
        self.assertEqual(transitions, {})
        self.assertEqual(self.transition_retriever.cache[0], (-1, "", {}))
        self.assertEqual(self.transition_retriever.cache[1], (-1, "", {}))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}))
        self.assertEqual(self.transition_retriever.age_counter, 0)
        self.source_retriever.retrieve.assert_not_called()
        self.transition_builder.build.assert_not_called()


    def test_get_no_source(self):
        self.source_retriever.retrieve.return_value = []

        speaker_names, transitions = self.transition_retriever.get(["folamh"])

        self.assertEqual(speaker_names, ["folamh"])
        self.assertEqual(transitions, {})
        self.assertEqual(self.transition_retriever.cache[0], (-1, "", {}))
        self.assertEqual(self.transition_retriever.cache[1], (-1, "", {}))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}))
        self.assertEqual(self.transition_retriever.age_counter, 0)
        self.source_retriever.retrieve.assert_called_once_with("folamh")
        self.transition_builder.build.assert_not_called()


    def test_get_no_transitions(self):
        self.source_retriever.retrieve.return_value = self.saoi_source
        self.transition_builder.build.return_value = {}

        speaker_names, transitions = self.transition_retriever.get(["saoi"])

        self.assertEqual(speaker_names, ["saoi"])
        self.assertEqual(transitions, {})
        self.assertEqual(self.transition_retriever.cache[0], (-1, "", {}))
        self.assertEqual(self.transition_retriever.cache[1], (-1, "", {}))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}))
        self.assertEqual(self.transition_retriever.age_counter, 0)
        self.source_retriever.retrieve.assert_called_once_with("saoi")
        self.transition_builder.build.assert_called_once_with(self.saoi_source, 2)


    def test_get_uncached_first(self):
        self.source_retriever.retrieve.return_value = self.saoi_source
        self.transition_builder.build.return_value = self.saoi_transitions

        speaker_names, transitions = self.transition_retriever.get(["saoi"])

        self.assertEqual(speaker_names, ["saoi"])
        self.assertEqual(transitions, self.saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "saoi", self.saoi_transitions))
        self.assertEqual(self.transition_retriever.cache[1], (-1, "", {}))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}))
        self.assertEqual(self.transition_retriever.age_counter, 1)
        self.source_retriever.retrieve.assert_called_once_with("saoi")
        self.transition_builder.build.assert_called_once_with(self.saoi_source, 2)


    def test_get_uncached_multiple(self):
        self.source_retriever.retrieve.side_effect = [self.saoi_source, self.faidh_source, self.eolai_source]
        self.transition_builder.build.side_effect = [self.saoi_transitions, self.faidh_transitions, self.eolai_transitions]

        self.transition_retriever.get(["saoi"])
        self.transition_retriever.get(["fáidh"])
        speaker_names, transitions = self.transition_retriever.get(["eolaí"])

        self.assertEqual(speaker_names, ["eolaí"])
        self.assertEqual(transitions, self.eolai_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "saoi", self.saoi_transitions))
        self.assertEqual(self.transition_retriever.cache[1], (1, "fáidh", self.faidh_transitions))
        self.assertEqual(self.transition_retriever.cache[2], (2, "eolaí", self.eolai_transitions))
        self.assertEqual(self.transition_retriever.age_counter, 3)
        self.assertEqual(self.source_retriever.retrieve.call_count, 3)
        self.source_retriever.retrieve.assert_has_calls([call("saoi"), call("fáidh"), call("eolaí")], any_order=False)
        self.assertEqual(self.transition_builder.build.call_count, 3)
        self.transition_builder.build.assert_has_calls([call(self.saoi_source, 2), call(self.faidh_source, 2), call(self.eolai_source, 2)], any_order=False)


    def test_get_cached_singular(self):
        self.source_retriever.retrieve.return_value = self.saoi_source
        self.transition_builder.build.return_value = self.saoi_transitions

        self.transition_retriever.get(["saoi"])
        speaker_names, transitions = self.transition_retriever.get(["saoi"])

        self.assertEqual(speaker_names, ["saoi"])
        self.assertEqual(transitions, self.saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (1, "saoi", self.saoi_transitions))
        self.assertEqual(self.transition_retriever.cache[1], (-1, "", {}))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}))
        self.assertEqual(self.transition_retriever.age_counter, 2)
        self.source_retriever.retrieve.assert_called_once_with("saoi")
        self.transition_builder.build.assert_called_once_with(self.saoi_source, 2)


    def test_get_cached_multiple(self):
        self.source_retriever.retrieve.side_effect = [self.saoi_source, self.faidh_source, self.eolai_source, self.eolai_source, self.eolai_source, self.faidh_source]
        self.transition_builder.build.side_effect = [self.saoi_transitions, self.faidh_transitions, self.eolai_transitions, self.eolai_transitions, self.eolai_transitions, self.faidh_transitions]

        self.transition_retriever.get(["saoi"])
        self.transition_retriever.get(["fáidh"])
        self.transition_retriever.get(["eolaí"])
        self.transition_retriever.get(["eolaí"])
        self.transition_retriever.get(["eolaí"])
        speaker_names, transitions = self.transition_retriever.get(["fáidh"])

        self.assertEqual(speaker_names, ["fáidh"])
        self.assertEqual(transitions, self.faidh_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "saoi", self.saoi_transitions))
        self.assertEqual(self.transition_retriever.cache[1], (5, "fáidh", self.faidh_transitions))
        self.assertEqual(self.transition_retriever.cache[2], (4, "eolaí", self.eolai_transitions))
        self.assertEqual(self.transition_retriever.age_counter, 6)
        self.assertEqual(self.source_retriever.retrieve.call_count, 3)
        self.source_retriever.retrieve.assert_has_calls([call("saoi"), call("fáidh"), call("eolaí")], any_order=False)
        self.assertEqual(self.transition_builder.build.call_count, 3)
        self.transition_builder.build.assert_has_calls([call(self.saoi_source, 2), call(self.faidh_source, 2), call(self.eolai_source, 2)], any_order=False)


    def test_get_cache_full(self):
        self.source_retriever.retrieve.side_effect = [self.saoi_source, self.faidh_source, self.eolai_source, self.eagnai_source]
        self.transition_builder.build.side_effect = [self.saoi_transitions, self.faidh_transitions, self.eolai_transitions, self.eagnai_transitions]

        self.transition_retriever.get(["saoi"])
        self.transition_retriever.get(["fáidh"])
        self.transition_retriever.get(["eolaí"])
        self.transition_retriever.get(["saoi"])
        speaker_names, transitions = self.transition_retriever.get(["eagnaí"])

        self.assertEqual(speaker_names, ["eagnaí"])
        self.assertEqual(transitions, self.eagnai_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (3, "saoi", self.saoi_transitions))
        self.assertEqual(self.transition_retriever.cache[1], (4, "eagnaí", self.eagnai_transitions))
        self.assertEqual(self.transition_retriever.cache[2], (2, "eolaí", self.eolai_transitions))
        self.assertEqual(self.transition_retriever.age_counter, 5)
        self.assertEqual(self.source_retriever.retrieve.call_count, 4)
        self.source_retriever.retrieve.assert_has_calls([call("saoi"), call("fáidh"), call("eolaí"), call("eagnaí")], any_order=False)
        self.assertEqual(self.transition_builder.build.call_count, 4)
        self.transition_builder.build.assert_has_calls([call(self.saoi_source, 2), call(self.faidh_source, 2), call(self.eolai_source, 2), call(self.eagnai_source, 2)], any_order=False)


    def test_get_aliased(self):
        self.source_retriever.retrieve.return_value = self.saoi_source
        self.transition_builder.build.return_value = self.saoi_transitions

        speaker_names, transitions = self.transition_retriever.get(["saoi0"])

        self.assertEqual(speaker_names, ["saoi"])
        self.assertEqual(transitions, self.saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "saoi", self.saoi_transitions))
        self.assertEqual(self.transition_retriever.cache[1], (-1, "", {}))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}))
        self.assertEqual(self.transition_retriever.age_counter, 1)
        self.source_retriever.retrieve.assert_called_once_with("saoi")
        self.transition_builder.build.assert_called_once_with(self.saoi_source, 2)


    def test_get_merged_in_order(self):
        self.source_retriever.retrieve.side_effect = [self.eolai_source, self.saoi_source]
        self.transition_builder.build.side_effect = [self.eolai_transitions, self.saoi_transitions]

        speaker_names, transitions = self.transition_retriever.get(["eolaí", "saoi"])

        self.assertEqual(speaker_names, ["eolaí", "saoi"])
        self.assertEqual(transitions, self.eolai_saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "eolaí", self.eolai_transitions))
        self.assertEqual(self.transition_retriever.cache[1], (1, "saoi", self.saoi_transitions))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}))
        self.assertEqual(self.transition_retriever.age_counter, 2)
        self.source_retriever.retrieve.assert_has_calls([call("eolaí"), call("saoi")], any_order=False)
        self.transition_builder.build.assert_has_calls([call(self.eolai_source, 2), call(self.saoi_source, 2)], any_order=False)


    def test_get_merged_out_of_order(self):
        self.source_retriever.retrieve.side_effect = [self.eolai_source, self.saoi_source]
        self.transition_builder.build.side_effect = [self.eolai_transitions, self.saoi_transitions]

        speaker_names, transitions = self.transition_retriever.get(["saoi", "eolaí"])

        self.assertEqual(speaker_names, ["eolaí", "saoi"])
        self.assertEqual(transitions, self.eolai_saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "eolaí", self.eolai_transitions))
        self.assertEqual(self.transition_retriever.cache[1], (1, "saoi", self.saoi_transitions))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}))
        self.assertEqual(self.transition_retriever.age_counter, 2)
        self.source_retriever.retrieve.assert_has_calls([call("eolaí"), call("saoi")], any_order=False)
        self.transition_builder.build.assert_has_calls([call(self.eolai_source, 2), call(self.saoi_source, 2)], any_order=False)


    def test_get_merged_some_unknown(self):
        self.source_retriever.retrieve.side_effect = [self.eolai_source, self.saoi_source]
        self.transition_builder.build.side_effect = [self.eolai_transitions, self.saoi_transitions]

        speaker_names, transitions = self.transition_retriever.get(["eolaí", "saoi", "anaithnid"])

        self.assertEqual(speaker_names, ["eolaí", "saoi"])
        self.assertEqual(transitions, self.eolai_saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "eolaí", self.eolai_transitions))
        self.assertEqual(self.transition_retriever.cache[1], (1, "saoi", self.saoi_transitions))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}))
        self.assertEqual(self.transition_retriever.age_counter, 2)
        self.source_retriever.retrieve.assert_has_calls([call("eolaí"), call("saoi")], any_order=False)
        self.transition_builder.build.assert_has_calls([call(self.eolai_source, 2), call(self.saoi_source, 2)], any_order=False)


    def test_get_merged_too_many_speakers(self):
        self.source_retriever.retrieve.side_effect = [self.eolai_source, self.saoi_source]
        self.transition_builder.build.side_effect = [self.eolai_transitions, self.saoi_transitions]

        speaker_names, transitions = self.transition_retriever.get(["eolaí", "saoi", "fáidh"])

        self.assertEqual(speaker_names, ["eolaí", "saoi"])
        self.assertEqual(transitions, self.eolai_saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "eolaí", self.eolai_transitions))
        self.assertEqual(self.transition_retriever.cache[1], (1, "saoi", self.saoi_transitions))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}))
        self.assertEqual(self.transition_retriever.age_counter, 2)
        self.source_retriever.retrieve.assert_has_calls([call("eolaí"), call("saoi")], any_order=False)
        self.transition_builder.build.assert_has_calls([call(self.eolai_source, 2), call(self.saoi_source, 2)], any_order=False)


if __name__ == "__main__":
    unittest.main()
