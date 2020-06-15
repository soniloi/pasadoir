from cached_transition_retriever import CachedTransitionRetriever
from generator import Generator
from rand import Rand
from request_processor import RequestProcessor
from source_retriever import SourceRetriever
from transition_builder import TransitionBuilder

class RequestHandler:

    def __init__(self, source_dir):
        source_retriever = SourceRetriever(source_dir)
        transition_builder = TransitionBuilder()
        transition_retriever = CachedTransitionRetriever(source_retriever, transition_builder)
        generator = Generator(Rand())
        self.processor = RequestProcessor(transition_retriever, generator)


    def handle(self, request):
        return self.processor.process(request)