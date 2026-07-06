class Chunker:

    def __init__(self):
        self.onto = None
        self.chunks = []

    def input(self, ontology):
        self.onto = ontology

    def output(self):
        return self.chunks
