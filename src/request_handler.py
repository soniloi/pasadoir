import datetime
import time

import config
from cached_transition_retriever import CachedTransitionRetriever
from meta_request_processor import MetaRequestProcessor
from quote_generator import QuoteGenerator
from rand import Rand
from quote_request_processor import QuoteRequestProcessor
from source_retriever import SourceRetriever
from speaker_collection import SpeakerCollection
from transition_builder import TransitionBuilder

class RequestHandler:

    def __init__(self, source_dir):
        source_retriever = SourceRetriever(source_dir)
        transition_builder = TransitionBuilder()
        speaker_collection = SpeakerCollection(source_retriever)
        transition_retriever = CachedTransitionRetriever(source_retriever, transition_builder, speaker_collection)
        rand = Rand()
        quote_generator = QuoteGenerator(rand)
        self.quote_processor = QuoteRequestProcessor(transition_retriever, quote_generator)
        start_time = datetime.datetime.fromtimestamp(time.time())
        self.meta_processor = MetaRequestProcessor(transition_retriever, speaker_collection, rand, start_time)
        self.processors = {
            config.GENERATE_REQUEST_TRIGGER : self.quote_processor,
            config.META_REQUEST_TRIGGER : self.meta_processor,
        }


    def handle(self, request):
        request = request.strip()
        if not request:
            return ""

        if request[0] in self.processors:
            processor = self.processors[request[0]]
            request = request[1:]
            if request:
                return processor.process(request)

        return ""
