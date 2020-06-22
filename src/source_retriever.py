import config

import os

class SourceRetriever():

    def __init__(self, dir_path):
        self.dir_path = dir_path


    def list_speakers(self):
        return [filename[:len(filename)-len(config.SOURCE_EXTENSION)]
            for filename in os.listdir(self.dir_path)
            if filename.endswith(config.SOURCE_EXTENSION)]


    def get_merge_info(self):
        return self.get_meta_info(config.MERGE_INFO_FILENAME)


    def get_source_info(self):
        return self.get_meta_info(config.SOURCE_INFO_FILENAME)


    def get_meta_info(self, filename):
        filepath = os.path.join(self.dir_path, filename)
        if not os.path.isfile(filepath):
            return []

        with open(filepath) as f:
            return f.readlines()


    def retrieve(self, speaker_name):
        speaker_filename = os.path.join(self.dir_path, speaker_name + config.SOURCE_EXTENSION)

        if not os.path.isfile(speaker_filename):
            return []

        with open(speaker_filename, encoding="utf8", errors="ignore") as speaker_file:
            return speaker_file.readlines()
