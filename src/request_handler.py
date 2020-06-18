import config
from cached_transition_retriever import CachedTransitionRetriever
from meta_request_processor import MetaRequestProcessor
from quote_generator import QuoteGenerator
from rand import Rand
from quote_request_processor import QuoteRequestProcessor
from source_retriever import SourceRetriever
from transition_builder import TransitionBuilder

class RequestHandler:

    def __init__(self, source_dir):
        source_retriever = SourceRetriever(source_dir)
        transition_builder = TransitionBuilder()
        transition_retriever = CachedTransitionRetriever(source_retriever, transition_builder)
        quote_generator = QuoteGenerator(Rand())
        self.quote_processor = QuoteRequestProcessor(transition_retriever, quote_generator)
        self.meta_processor = MetaRequestProcessor(transition_retriever)
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
