from chunker import Chunker


class Locality(Chunker):

    def __init__(self, k):
        super().__init__()
        self.k = k

    def generate_chunks(self):
        pass
