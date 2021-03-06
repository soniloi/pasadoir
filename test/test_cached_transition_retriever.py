import unittest
from unittest.mock import call, Mock

from cached_transition_retriever import CachedTransitionRetriever

class TestCachedTransitionRetriever(unittest.TestCase):

    def setUp(self):
        self.setup_data()
        self.setup_source_retriever()
        self.setup_transition_builder()
        self.setup_speaker_collection()
        self.transition_retriever = CachedTransitionRetriever(self.source_retriever, self.transition_builder, self.speaker_collection,
            capacity=6, min_lookbacks=2)


    def tearDown(self):
        pass


    def setup_data(self):
        self.saoi_source = ["aithníonn ciaróg ciaróg eile"]
        self.faidh_source = ["is leor nod don eolach"]
        self.eolai_source = ["is binn béal ina thost"]
        self.eagnai_source = ["bíonn gach tosú lag"]
        self.draoi_source = ["tús maith leath na hoibre"]
        self.cailleach_source = ["ní bhíonn tréan buan"]
        self.asarlai_source = ["bíonn an fhírinne searbh"]
        self.beag_source = ["bailíonn brobh beart"]
        self.folamh_source = []
        self.saoi_transitions = {("fillean", "an") : ["feall"], ("an", "feall") : ["ar"], ("feall", "ar") : ["an"], ("ar", "an") : ["bhfeallaire"]}
        self.saoi_transitions_reversed = {("feall", "an") : ["filleann"], ("ar", "feall") : ["an"], ("an", "ar") : ["feall"], ("bhfeallaire", "an") : ["ar"]}
        self.faidh_transitions = {("is", "leor") : ["nod"], ("leor", "nod") : ["don"], ("nod", "don") : ["eolach"]}
        self.eolai_transitions = {("bíonn", "blas") : ["ar"], ("blas", "ar") : ["an"], ("ar", "an") : ["mbeagán"]}
        self.eagnai_transitions = {("bíonn", "gach") : ["tosú"], ("gach", "tosú") : ["lag"]}
        self.draoi_transitions = {("tús", "maith") : ["leath"], ("maith", "leath") : ["na"], ("leath", "na") : ["hoibre"]}
        self.cailleach_transitions = {("ní", "bhíonn") : ["treán"], ("bhíonn", "tréan") : ["buan"]}
        self.asarlai_transitions = {("bíonn", "an") : ["fhírinne"], ("an", "fhírinne") : ["searbh"]}
        self.beag_transitions = {("bailíonn", "brobh") : ["beart"]}
        self.eolai_saoi_transitions = {("bíonn", "blas") : ["ar"], ("blas", "ar") : ["an"], ("ar", "an") : ["mbeagán", "bhfeallaire"], ("fillean", "an") : ["feall"], ("an", "feall") : ["ar"], ("feall", "ar") : ["an"]}


    def setup_source_retriever(self):
        self.source_retriever = Mock()
        self.source_retriever.retrieve.return_value = []


    def setup_transition_builder(self):
        self.transition_builder = Mock()
        self.transition_builder.build.return_value = {}


    def setup_speaker_collection(self):
        self.speaker_collection = Mock()


    def test_get_unknown_speaker(self):
        self.speaker_collection.resolve_names.return_value = []

        speaker_names, transitions = self.transition_retriever.get(["anaithnid"])

        self.assertIsNone(speaker_names)
        self.assertEqual(transitions, {})
        self.assertEqual(self.transition_retriever.cache[0], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.cache[1], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.age_counter, 0)
        self.speaker_collection.resolve_names.assert_called_once_with(["anaithnid"])
        self.source_retriever.retrieve.assert_not_called()
        self.transition_builder.build.assert_not_called()


    def test_get_no_source(self):
        self.speaker_collection.resolve_names.return_value = ["folamh"]
        self.source_retriever.retrieve.return_value = []

        speaker_names, transitions = self.transition_retriever.get(["folamh"])

        self.assertEqual(speaker_names, ["folamh"])
        self.assertEqual(transitions, {})
        self.assertEqual(self.transition_retriever.cache[0], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.cache[1], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.age_counter, 0)
        self.speaker_collection.resolve_names.assert_called_once_with(["folamh"])
        self.source_retriever.retrieve.assert_called_once_with("folamh")
        self.transition_builder.build.assert_not_called()


    def test_get_no_transitions(self):
        self.speaker_collection.resolve_names.return_value = ["saoi"]
        self.source_retriever.retrieve.return_value = self.saoi_source
        self.transition_builder.build.return_value = {}

        speaker_names, transitions = self.transition_retriever.get(["saoi"])

        self.assertEqual(speaker_names, ["saoi"])
        self.assertEqual(transitions, {})
        self.assertEqual(self.transition_retriever.cache[0], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.cache[1], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.age_counter, 0)
        self.speaker_collection.resolve_names.assert_called_once_with(["saoi"])
        self.source_retriever.retrieve.assert_called_once_with("saoi")
        self.transition_builder.build.assert_called_once_with(self.saoi_source, 2, False)


    def test_get_uncached_first(self):
        self.speaker_collection.resolve_names.return_value = ["saoi"]
        self.source_retriever.retrieve.return_value = self.saoi_source
        self.transition_builder.build.return_value = self.saoi_transitions

        speaker_names, transitions = self.transition_retriever.get(["saoi"])

        self.assertEqual(speaker_names, ["saoi"])
        self.assertEqual(transitions, self.saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "saoi", self.saoi_transitions, False))
        self.assertEqual(self.transition_retriever.cache[1], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.age_counter, 1)
        self.speaker_collection.resolve_names.assert_called_once_with(["saoi"])
        self.source_retriever.retrieve.assert_called_once_with("saoi")
        self.transition_builder.build.assert_called_once_with(self.saoi_source, 2, False)


    def test_get_uncached_multiple(self):
        self.speaker_collection.resolve_names.side_effect = [["saoi"], ["fáidh"], ["eolaí"]]
        self.source_retriever.retrieve.side_effect = [self.saoi_source, self.faidh_source, self.eolai_source]
        self.transition_builder.build.side_effect = [self.saoi_transitions, self.faidh_transitions, self.eolai_transitions]

        self.transition_retriever.get(["saoi"])
        self.transition_retriever.get(["fáidh"])
        speaker_names, transitions = self.transition_retriever.get(["eolaí"])

        self.assertEqual(speaker_names, ["eolaí"])
        self.assertEqual(transitions, self.eolai_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "saoi", self.saoi_transitions, False))
        self.assertEqual(self.transition_retriever.cache[1], (1, "fáidh", self.faidh_transitions, False))
        self.assertEqual(self.transition_retriever.cache[2], (2, "eolaí", self.eolai_transitions, False))
        self.assertEqual(self.transition_retriever.age_counter, 3)
        self.assertEqual(self.source_retriever.retrieve.call_count, 3)
        self.speaker_collection.resolve_names.assert_has_calls([call(["saoi"]), call(["fáidh"]), call(["eolaí"])], any_order=False)
        self.source_retriever.retrieve.assert_has_calls([call("saoi"), call("fáidh"), call("eolaí")], any_order=False)
        self.assertEqual(self.transition_builder.build.call_count, 3)
        self.transition_builder.build.assert_has_calls([call(self.saoi_source, 2, False), call(self.faidh_source, 2, False), call(self.eolai_source, 2, False)], any_order=False)


    def test_get_do_not_cache_small(self):
        self.speaker_collection.resolve_names.return_value = ["beag"]
        self.source_retriever.retrieve.return_value = self.beag_source
        self.transition_builder.build.return_value = self.beag_transitions

        speaker_names, transitions = self.transition_retriever.get(["beag"])

        self.assertEqual(speaker_names, ["beag"])
        self.assertEqual(transitions, self.beag_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.cache[1], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.age_counter, 0)
        self.speaker_collection.resolve_names.assert_called_once_with(["beag"])
        self.source_retriever.retrieve.assert_called_once_with("beag")
        self.transition_builder.build.assert_called_once_with(self.beag_source, 2, False)


    def test_get_cached_singular(self):
        self.speaker_collection.resolve_names.return_value = ["saoi"]
        self.source_retriever.retrieve.return_value = self.saoi_source
        self.transition_builder.build.return_value = self.saoi_transitions

        self.transition_retriever.get(["saoi"])
        speaker_names, transitions = self.transition_retriever.get(["saoi"])

        self.assertEqual(speaker_names, ["saoi"])
        self.assertEqual(transitions, self.saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (1, "saoi", self.saoi_transitions, False))
        self.assertEqual(self.transition_retriever.cache[1], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.age_counter, 2)
        self.speaker_collection.resolve_names.assert_has_calls([call(["saoi"]), call(["saoi"])], any_order=False)
        self.source_retriever.retrieve.assert_called_once_with("saoi")
        self.transition_builder.build.assert_called_once_with(self.saoi_source, 2, False)


    def test_get_cached_multiple(self):
        self.speaker_collection.resolve_names.side_effect = [["saoi"], ["fáidh"], ["eolaí"], ["eolaí"], ["eolaí"], ["saoi"], ["fáidh"]]
        self.source_retriever.retrieve.side_effect = [self.saoi_source, self.faidh_source, self.eolai_source, self.saoi_source]
        self.transition_builder.build.side_effect = [self.saoi_transitions, self.faidh_transitions, self.eolai_transitions, self.saoi_transitions_reversed]

        self.transition_retriever.get(["saoi"])
        self.transition_retriever.get(["fáidh"])
        self.transition_retriever.get(["eolaí"])
        self.transition_retriever.get(["eolaí"])
        self.transition_retriever.get(["eolaí"])
        self.transition_retriever.get(["saoi"], True)
        speaker_names, transitions = self.transition_retriever.get(["fáidh"])

        self.assertEqual(speaker_names, ["fáidh"])
        self.assertEqual(transitions, self.faidh_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "saoi", self.saoi_transitions, False))
        self.assertEqual(self.transition_retriever.cache[1], (6, "fáidh", self.faidh_transitions, False))
        self.assertEqual(self.transition_retriever.cache[2], (4, "eolaí", self.eolai_transitions, False))
        self.assertEqual(self.transition_retriever.cache[3], (5, "saoi", self.saoi_transitions_reversed, True))
        self.assertEqual(self.transition_retriever.age_counter, 7)
        self.assertEqual(self.source_retriever.retrieve.call_count, 4)
        self.speaker_collection.resolve_names.assert_has_calls([call(["saoi"]), call(["fáidh"]), call(["eolaí"]), call(["eolaí"]), call(["eolaí"]), call(["saoi"]), call(["fáidh"])], any_order=False)
        self.source_retriever.retrieve.assert_has_calls([call("saoi"), call("fáidh"), call("eolaí")], any_order=False)
        self.assertEqual(self.transition_builder.build.call_count, 4)
        self.transition_builder.build.assert_has_calls([call(self.saoi_source, 2, False), call(self.faidh_source, 2, False), call(self.eolai_source, 2, False), call(self.saoi_source, 2, True)], any_order=False)


    def test_get_cache_full(self):
        self.speaker_collection.resolve_names.side_effect = [["saoi"], ["fáidh"], ["eolaí"], ["saoi"], ["draoi"], ["cailleach"], ["asarlaí"], ["eagnaí"]]
        self.source_retriever.retrieve.side_effect = [self.saoi_source, self.faidh_source, self.eolai_source, self.draoi_source, self.cailleach_source, self.asarlai_source, self.eagnai_source]
        self.transition_builder.build.side_effect = [self.saoi_transitions, self.faidh_transitions, self.eolai_transitions, self.draoi_transitions, self.cailleach_transitions, self.asarlai_transitions, self.eagnai_transitions]

        self.transition_retriever.get(["saoi"])
        self.transition_retriever.get(["fáidh"])
        self.transition_retriever.get(["eolaí"])
        self.transition_retriever.get(["saoi"])
        self.transition_retriever.get(["draoi"])
        self.transition_retriever.get(["cailleach"])
        self.transition_retriever.get(["asarlaí"])
        speaker_names, transitions = self.transition_retriever.get(["eagnaí"])

        self.assertEqual(speaker_names, ["eagnaí"])
        self.assertEqual(transitions, self.eagnai_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (3, "saoi", self.saoi_transitions, False))
        self.assertEqual(self.transition_retriever.cache[1], (7, "eagnaí", self.eagnai_transitions, False))
        self.assertEqual(self.transition_retriever.cache[2], (2, "eolaí", self.eolai_transitions, False))
        self.assertEqual(self.transition_retriever.cache[3], (4, "draoi", self.draoi_transitions, False))
        self.assertEqual(self.transition_retriever.cache[4], (5, "cailleach", self.cailleach_transitions, False))
        self.assertEqual(self.transition_retriever.cache[5], (6, "asarlaí", self.asarlai_transitions, False))
        self.assertEqual(self.transition_retriever.age_counter, 8)
        self.assertEqual(self.source_retriever.retrieve.call_count, 7)
        self.speaker_collection.resolve_names.assert_has_calls([call(["saoi"]), call(["fáidh"]), call(["eolaí"]), call(["saoi"]), call(["draoi"]), call(["cailleach"]), call(["asarlaí"]), call(["eagnaí"])], any_order=False)
        self.source_retriever.retrieve.assert_has_calls([call("saoi"), call("fáidh"), call("eolaí"), call("draoi"), call("cailleach"), call("asarlaí"), call("eagnaí")], any_order=False)
        self.assertEqual(self.transition_builder.build.call_count, 7)
        self.transition_builder.build.assert_has_calls([call(self.saoi_source, 2, False), call(self.faidh_source, 2, False), call(self.eolai_source, 2, False), call(self.draoi_source, 2, False), call(self.cailleach_source, 2, False), call(self.asarlai_source, 2, False), call(self.eagnai_source, 2, False)], any_order=False)


    def test_get_aliased(self):
        self.speaker_collection.resolve_names.return_value = ["saoi"]
        self.source_retriever.retrieve.return_value = self.saoi_source
        self.transition_builder.build.return_value = self.saoi_transitions

        speaker_names, transitions = self.transition_retriever.get(["saoi0"])

        self.assertEqual(speaker_names, ["saoi"])
        self.assertEqual(transitions, self.saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "saoi", self.saoi_transitions, False))
        self.assertEqual(self.transition_retriever.cache[1], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.age_counter, 1)
        self.speaker_collection.resolve_names.assert_called_once_with(["saoi0"])
        self.source_retriever.retrieve.assert_called_once_with("saoi")
        self.transition_builder.build.assert_called_once_with(self.saoi_source, 2, False)


    def test_get_different_directions(self):
        self.speaker_collection.resolve_names.return_value = ["saoi"]
        self.source_retriever.retrieve.return_value = self.saoi_source
        self.transition_builder.build.side_effect = [self.saoi_transitions, self.saoi_transitions_reversed]

        self.transition_retriever.get(["saoi"])
        speaker_names, transitions = self.transition_retriever.get(["saoi"], reverse=True)

        self.assertEqual(speaker_names, ["saoi"])
        self.assertEqual(transitions, self.saoi_transitions_reversed)
        self.assertEqual(self.transition_retriever.cache[0], (0, "saoi", self.saoi_transitions, False))
        self.assertEqual(self.transition_retriever.cache[1], (1, "saoi", self.saoi_transitions_reversed, True))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.age_counter, 2)
        self.speaker_collection.resolve_names.assert_has_calls([call(["saoi"]), call(["saoi"])], any_order=False)
        self.source_retriever.retrieve.assert_has_calls([call("saoi"), call("saoi")], any_order=False)
        self.transition_builder.build.assert_has_calls([call(self.saoi_source, 2, False), call(self.saoi_source, 2, True)], any_order=False)


    def test_get_merged_in_order(self):
        self.speaker_collection.resolve_names.return_value = ["eolaí", "saoi"]
        self.source_retriever.retrieve.side_effect = [self.eolai_source, self.saoi_source]
        self.transition_builder.build.side_effect = [self.eolai_transitions, self.saoi_transitions]

        speaker_names, transitions = self.transition_retriever.get(["eolaí", "saoi"])

        self.assertEqual(speaker_names, ["eolaí", "saoi"])
        self.assertEqual(transitions, self.eolai_saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "eolaí", self.eolai_transitions, False))
        self.assertEqual(self.transition_retriever.cache[1], (1, "saoi", self.saoi_transitions, False))
        self.assertEqual(self.transition_retriever.cache[2], (2, "eolaí:saoi", self.eolai_saoi_transitions, False))
        self.assertEqual(self.transition_retriever.age_counter, 3)
        self.speaker_collection.resolve_names.assert_called_once_with(["eolaí", "saoi"])
        self.source_retriever.retrieve.assert_has_calls([call("eolaí"), call("saoi")], any_order=False)
        self.transition_builder.build.assert_has_calls([call(self.eolai_source, 2, False), call(self.saoi_source, 2, False)], any_order=False)


    def test_get_merged_out_of_order(self):
        self.speaker_collection.resolve_names.return_value = ["saoi", "eolaí"]
        self.source_retriever.retrieve.side_effect = [self.eolai_source, self.saoi_source]
        self.transition_builder.build.side_effect = [self.eolai_transitions, self.saoi_transitions]

        speaker_names, transitions = self.transition_retriever.get(["saoi", "eolaí"])

        self.assertEqual(speaker_names, ["eolaí", "saoi"])
        self.assertEqual(transitions, self.eolai_saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "eolaí", self.eolai_transitions, False))
        self.assertEqual(self.transition_retriever.cache[1], (1, "saoi", self.saoi_transitions, False))
        self.assertEqual(self.transition_retriever.cache[2], (2, "eolaí:saoi", self.eolai_saoi_transitions, False))
        self.assertEqual(self.transition_retriever.age_counter, 3)
        self.speaker_collection.resolve_names.assert_called_once_with(["saoi", "eolaí"])
        self.source_retriever.retrieve.assert_has_calls([call("eolaí"), call("saoi")], any_order=False)
        self.transition_builder.build.assert_has_calls([call(self.eolai_source, 2, False), call(self.saoi_source, 2, False)], any_order=False)


    def test_get_merged_some_unknown(self):
        self.speaker_collection.resolve_names.return_value = ["eolaí", "saoi"]
        self.source_retriever.retrieve.side_effect = [self.eolai_source, self.saoi_source]
        self.transition_builder.build.side_effect = [self.eolai_transitions, self.saoi_transitions]

        speaker_names, transitions = self.transition_retriever.get(["eolaí", "saoi", "anaithnid"])

        self.assertEqual(speaker_names, ["eolaí", "saoi"])
        self.assertEqual(transitions, self.eolai_saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "eolaí", self.eolai_transitions, False))
        self.assertEqual(self.transition_retriever.cache[1], (1, "saoi", self.saoi_transitions, False))
        self.assertEqual(self.transition_retriever.cache[2], (2, "eolaí:saoi", self.eolai_saoi_transitions, False))
        self.assertEqual(self.transition_retriever.age_counter, 3)
        self.speaker_collection.resolve_names.assert_called_once_with(["eolaí", "saoi", "anaithnid"])
        self.source_retriever.retrieve.assert_has_calls([call("eolaí"), call("saoi")], any_order=False)
        self.transition_builder.build.assert_has_calls([call(self.eolai_source, 2, False), call(self.saoi_source, 2, False)], any_order=False)


    def test_get_merged_too_many_speakers(self):
        self.speaker_collection.resolve_names.return_value = ["eolaí", "saoi", "fáidh"]
        self.source_retriever.retrieve.side_effect = [self.eolai_source, self.saoi_source]
        self.transition_builder.build.side_effect = [self.eolai_transitions, self.saoi_transitions]

        speaker_names, transitions = self.transition_retriever.get(["eolaí", "saoi", "fáidh"])

        self.assertEqual(speaker_names, ["eolaí", "saoi"])
        self.assertEqual(transitions, self.eolai_saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "eolaí", self.eolai_transitions, False))
        self.assertEqual(self.transition_retriever.cache[1], (1, "saoi", self.saoi_transitions, False))
        self.assertEqual(self.transition_retriever.cache[2], (2, "eolaí:saoi", self.eolai_saoi_transitions, False))
        self.assertEqual(self.transition_retriever.age_counter, 3)
        self.speaker_collection.resolve_names.assert_called_once_with(["eolaí", "saoi", "fáidh"])
        self.source_retriever.retrieve.assert_has_calls([call("eolaí"), call("saoi")], any_order=False)
        self.transition_builder.build.assert_has_calls([call(self.eolai_source, 2, False), call(self.saoi_source, 2, False)], any_order=False)


    def test_get_merged_cached_in_order(self):
        self.speaker_collection.resolve_names.side_effect = [["eolaí", "saoi"], ["eolaí", "saoi"]]
        self.source_retriever.retrieve.side_effect = [self.eolai_source, self.saoi_source]
        self.transition_builder.build.side_effect = [self.eolai_transitions, self.saoi_transitions]

        self.transition_retriever.get(["eolaí", "saoi"])
        speaker_names, transitions = self.transition_retriever.get(["eolaí", "saoi"])

        self.assertEqual(speaker_names, ["eolaí", "saoi"])
        self.assertEqual(transitions, self.eolai_saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "eolaí", self.eolai_transitions, False))
        self.assertEqual(self.transition_retriever.cache[1], (1, "saoi", self.saoi_transitions, False))
        self.assertEqual(self.transition_retriever.cache[2], (3, "eolaí:saoi", self.eolai_saoi_transitions, False))
        self.assertEqual(self.transition_retriever.age_counter, 4)
        self.speaker_collection.resolve_names.assert_has_calls([call(["eolaí", "saoi"]), call(["eolaí", "saoi"])], any_order=False)
        self.source_retriever.retrieve.assert_has_calls([call("eolaí"), call("saoi")], any_order=False)
        self.transition_builder.build.assert_has_calls([call(self.eolai_source, 2, False), call(self.saoi_source, 2, False)], any_order=False)


    def test_get_merged_cached_differing_order(self):
        self.speaker_collection.resolve_names.side_effect = [["eolaí", "saoi"], ["eolaí", "saoi"]]
        self.source_retriever.retrieve.side_effect = [self.eolai_source, self.saoi_source]
        self.transition_builder.build.side_effect = [self.eolai_transitions, self.saoi_transitions]

        self.transition_retriever.get(["saoi", "eolaí"])
        speaker_names, transitions = self.transition_retriever.get(["eolaí", "saoi"])

        self.assertEqual(speaker_names, ["eolaí", "saoi"])
        self.assertEqual(transitions, self.eolai_saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "eolaí", self.eolai_transitions, False))
        self.assertEqual(self.transition_retriever.cache[1], (1, "saoi", self.saoi_transitions, False))
        self.assertEqual(self.transition_retriever.cache[2], (3, "eolaí:saoi", self.eolai_saoi_transitions, False))
        self.assertEqual(self.transition_retriever.age_counter, 4)
        self.speaker_collection.resolve_names.assert_has_calls([call(["saoi", "eolaí"]), call(["eolaí", "saoi"])], any_order=False)
        self.source_retriever.retrieve.assert_has_calls([call("eolaí"), call("saoi")], any_order=False)
        self.transition_builder.build.assert_has_calls([call(self.eolai_source, 2, False), call(self.saoi_source, 2, False)], any_order=False)


    def test_get_merged_same_speaker(self):
        self.speaker_collection.resolve_names.return_value = ["saoi", "saoi"]
        self.source_retriever.retrieve.side_effect = [self.saoi_source]
        self.transition_builder.build.side_effect = [self.saoi_transitions]

        speaker_names, transitions = self.transition_retriever.get(["saoi", "saoi0"])

        self.assertEqual(speaker_names, ["saoi"])
        self.assertEqual(transitions, self.saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "saoi", self.saoi_transitions, False))
        self.assertEqual(self.transition_retriever.cache[1], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.age_counter, 1)
        self.speaker_collection.resolve_names.assert_called_once_with(["saoi", "saoi0"])
        self.source_retriever.retrieve.assert_called_once_with("saoi")
        self.transition_builder.build.assert_called_once_with(self.saoi_source, 2, False)


    def test_get_merged_two_many_speakers_one_duplicated(self):
        self.speaker_collection.resolve_names.return_value = ["saoi", "saoi", "eolaí"]
        self.source_retriever.retrieve.side_effect = [self.eolai_source, self.saoi_source]
        self.transition_builder.build.side_effect = [self.eolai_transitions, self.saoi_transitions]

        speaker_names, transitions = self.transition_retriever.get(["saoi", "saoi0", "eolaí"])

        self.assertEqual(speaker_names, ["eolaí", "saoi"])
        self.assertEqual(transitions, self.eolai_saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "eolaí", self.eolai_transitions, False))
        self.assertEqual(self.transition_retriever.cache[1], (1, "saoi", self.saoi_transitions, False))
        self.assertEqual(self.transition_retriever.cache[2], (2, "eolaí:saoi", self.eolai_saoi_transitions, False))
        self.assertEqual(self.transition_retriever.age_counter, 3)
        self.speaker_collection.resolve_names.assert_called_once_with(["saoi", "saoi0", "eolaí"])
        self.source_retriever.retrieve.assert_has_calls([call("eolaí"), call("saoi")], any_order=False)
        self.transition_builder.build.assert_has_calls([call(self.eolai_source, 2, False), call(self.saoi_source, 2, False)], any_order=False)


    def test_refresh(self):
        self.speaker_collection.resolve_names.side_effect = [["saoi"], ["fáidh"], ["eolaí"]]
        self.source_retriever.retrieve.side_effect = [self.saoi_source, self.faidh_source, self.eolai_source]
        self.transition_builder.build.side_effect = [self.saoi_transitions, self.faidh_transitions, self.eolai_transitions]

        self.transition_retriever.get(["saoi"])
        self.transition_retriever.get(["fáidh"])
        self.transition_retriever.get(["eolaí"])
        self.transition_retriever.refresh()

        self.assertEqual(self.transition_retriever.cache[0], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.cache[1], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.cache[2], (-1, "", {}, False))
        self.assertEqual(self.transition_retriever.age_counter, 0)
        self.assertEqual(self.source_retriever.retrieve.call_count, 3)
        self.speaker_collection.resolve_names.assert_has_calls([call(["saoi"]), call(["fáidh"]), call(["eolaí"])], any_order=False)
        self.source_retriever.retrieve.assert_has_calls([call("saoi"), call("fáidh"), call("eolaí")], any_order=False)
        self.assertEqual(self.transition_builder.build.call_count, 3)
        self.transition_builder.build.assert_has_calls([call(self.saoi_source, 2, False), call(self.faidh_source, 2, False), call(self.eolai_source, 2, False)], any_order=False)


if __name__ == "__main__":
    unittest.main()
