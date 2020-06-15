import unittest
from unittest.mock import call, Mock

from cached_transition_retriever import CachedTransitionRetriever

class TestCachedTransitionRetriever(unittest.TestCase):

    def setUp(self):
        self.saoi_source = ["aithníonn ciaróg ciaróg eile"]
        self.faidh_source = ["is leor nod don eolach"]
        self.eolai_source = ["is binn béal ina thost"]
        self.eagnai_source = ["bíonn gach tosú lag"]
        self.saoi_transitions = {("aithníonn", "ciaróg") : "ciaróg", ("ciaróg", "ciaróg") : "eile"}
        self.faidh_transitions = {("is", "leor") : "nod", ("leor", "nod") : "don", ("nod", "don") : "eolach"}
        self.eolai_transitions = {("is", "binn") : "béal", ("binn", "béal") : "ina", ("béal", "ina") : "thost"}
        self.eagnai_transitions = {("bíonn", "gach") : "tosú", ("gach", "tosú") : "lag"}

        self.source_retriever = Mock()
        self.source_retriever.retrieve.return_value = []

        self.transition_builder = Mock()
        self.transition_builder.build.return_value = {}

        self.transition_retriever = CachedTransitionRetriever(self.source_retriever, self.transition_builder, 3)


    def tearDown(self):
        pass


    def test_get_no_source(self):
        self.source_retriever.retrieve.return_value = []

        transitions = self.transition_retriever.get("anaithnid")

        self.assertEqual(transitions, {})
        self.assertEqual(self.transition_retriever.cache[0], (-1, None, None))
        self.assertEqual(self.transition_retriever.cache[1], (-1, None, None))
        self.assertEqual(self.transition_retriever.cache[2], (-1, None, None))
        self.assertEqual(self.transition_retriever.age_counter, 0)
        self.source_retriever.retrieve.assert_called_once_with("anaithnid")
        self.transition_builder.build.assert_not_called()


    def test_get_no_transitions(self):
        self.source_retriever.retrieve.return_value = self.saoi_source
        self.transition_builder.build.return_value = {}

        transitions = self.transition_retriever.get("saoi")

        self.assertEqual(transitions, {})
        self.assertEqual(self.transition_retriever.cache[0], (-1, None, None))
        self.assertEqual(self.transition_retriever.cache[1], (-1, None, None))
        self.assertEqual(self.transition_retriever.cache[2], (-1, None, None))
        self.assertEqual(self.transition_retriever.age_counter, 0)
        self.source_retriever.retrieve.assert_called_once_with("saoi")
        self.transition_builder.build.assert_called_once_with(self.saoi_source, 2)


    def test_get_uncached_first(self):
        self.source_retriever.retrieve.return_value = self.saoi_source
        self.transition_builder.build.return_value = self.saoi_transitions

        transitions = self.transition_retriever.get("saoi")

        self.assertEqual(transitions, self.saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (0, "saoi", self.saoi_transitions))
        self.assertEqual(self.transition_retriever.cache[1], (-1, None, None))
        self.assertEqual(self.transition_retriever.cache[2], (-1, None, None))
        self.assertEqual(self.transition_retriever.age_counter, 1)
        self.source_retriever.retrieve.assert_called_once_with("saoi")
        self.transition_builder.build.assert_called_once_with(self.saoi_source, 2)


    def test_get_uncached_multiple(self):
        self.source_retriever.retrieve.side_effect = [self.saoi_source, self.faidh_source, self.eolai_source]
        self.transition_builder.build.side_effect = [self.saoi_transitions, self.faidh_transitions, self.eolai_transitions]

        self.transition_retriever.get("saoi")
        self.transition_retriever.get("fáidh")
        transitions = self.transition_retriever.get("eolaí")

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

        self.transition_retriever.get("saoi")
        transitions = self.transition_retriever.get("saoi")

        self.assertEqual(transitions, self.saoi_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (1, "saoi", self.saoi_transitions))
        self.assertEqual(self.transition_retriever.cache[1], (-1, None, None))
        self.assertEqual(self.transition_retriever.cache[2], (-1, None, None))
        self.assertEqual(self.transition_retriever.age_counter, 2)
        self.source_retriever.retrieve.assert_called_once_with("saoi")
        self.transition_builder.build.assert_called_once_with(self.saoi_source, 2)


    def test_get_cached_multiple(self):
        self.source_retriever.retrieve.side_effect = [self.saoi_source, self.faidh_source, self.eolai_source, self.eolai_source, self.eolai_source, self.faidh_source]
        self.transition_builder.build.side_effect = [self.saoi_transitions, self.faidh_transitions, self.eolai_transitions, self.eolai_transitions, self.eolai_transitions, self.faidh_transitions]

        self.transition_retriever.get("saoi")
        self.transition_retriever.get("fáidh")
        self.transition_retriever.get("eolaí")
        self.transition_retriever.get("eolaí")
        self.transition_retriever.get("eolaí")
        transitions = self.transition_retriever.get("fáidh")

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

        self.transition_retriever.get("saoi")
        self.transition_retriever.get("fáidh")
        self.transition_retriever.get("eolaí")
        self.transition_retriever.get("saoi")
        transitions = self.transition_retriever.get("eagnaí")

        self.assertEqual(transitions, self.eagnai_transitions)
        self.assertEqual(self.transition_retriever.cache[0], (3, "saoi", self.saoi_transitions))
        self.assertEqual(self.transition_retriever.cache[1], (4, "eagnaí", self.eagnai_transitions))
        self.assertEqual(self.transition_retriever.cache[2], (2, "eolaí", self.eolai_transitions))
        self.assertEqual(self.transition_retriever.age_counter, 5)
        self.assertEqual(self.source_retriever.retrieve.call_count, 4)
        self.source_retriever.retrieve.assert_has_calls([call("saoi"), call("fáidh"), call("eolaí"), call("eagnaí")], any_order=False)
        self.assertEqual(self.transition_builder.build.call_count, 4)
        self.transition_builder.build.assert_has_calls([call(self.saoi_source, 2), call(self.faidh_source, 2), call(self.eolai_source, 2), call(self.eagnai_source, 2)], any_order=False)


if __name__ == "__main__":
    unittest.main()
