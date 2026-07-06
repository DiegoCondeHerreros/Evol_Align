from chunking.locality import Locality
from chunking.taxonomic import Taxonomic
from chunking.semantic import Semantic


class ChunkingInterface:

    def __init__(self):
        self.locality = Locality()
        self.taxonomic = Taxonomic()
        self.semantic = Semantic()

    def run_chunking(self, method, onto):
        if method == "Locality":
            self.locality.input(onto)
            chunks = self.locality.generate_chunks()
            self.locality.clear()
            return chunks
        elif method == "Taxonomic":
            self.taxonomic.input(onto)
            chunks = self.taxonomic.generate_chunks(onto)
            self.taxonomic.clear()
            return chunks
        elif method == "Semantic":
            self.semantic.input(onto)
            chunks = self.semantic.generate_chunks(onto)
            self.taxonomic.clear()
            return chunks
