import os

class SourceRetriever():

    # FIXME: move to config
    MERGE_INFO_FILENAME = "merge.lst"
    SOURCE_EXTENSION = ".src"

    def __init__(self, dir_path):
        self.dir_path = dir_path


    def list_speakers(self):
        return [filename[:len(filename)-len(SourceRetriever.SOURCE_EXTENSION)]
            for filename in os.listdir(self.dir_path)
            if filename.endswith(SourceRetriever.SOURCE_EXTENSION)]


    def get_merge_info(self):
        if not os.path.isfile(SourceRetriever.MERGE_INFO_FILENAME):
            return []

        with open(SourceRetriever.MERGE_INFO_FILENAME) as merge_info_file:
            return merge_info_file.readlines()


    def retrieve(self, speaker_name):
        speaker_filename = os.path.join(self.dir_path, speaker_name + SourceRetriever.SOURCE_EXTENSION)

        if not os.path.isfile(speaker_filename):
            return []

        with open(speaker_filename, encoding="utf8", errors="ignore") as speaker_file:
            return speaker_file.readlines()
