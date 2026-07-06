from chunking.locality import Locality
from chunking.taxonomic import Taxonomic
from chunking.semantic import Semantic


class ChunkingInterface:

    def __init__(self):
        self.locality = Locality(2)
        self.taxonomic = Taxonomic()
        self.semantic = Semantic()
        self.chunks_dict = {}

    def run_chunking(self, onto):
        self.chunks_dict["Locality"] = self.locality.generate_chunks(onto)
        self.chunks_dict["Taxonomic"] = self.taxonomic.generate_chunks(onto)
        self.chunks_dict["Semantic"] = self.semantic.generate_chunks(onto)
