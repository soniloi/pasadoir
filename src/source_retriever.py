import os

class SourceRetriever():

    SOURCE_EXTENSION = ".src"

    def __init__(self, dir_path):
        self.dir_path = dir_path


    def retrieve(self, speaker_name):
        speaker_filename = os.path.join(self.dir_path, speaker_name + SourceRetriever.SOURCE_EXTENSION)

        if not os.path.exists(speaker_filename):
            return None

        with open(speaker_filename) as speaker_file:
            return speaker_file.readlines()
