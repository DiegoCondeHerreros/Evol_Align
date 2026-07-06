from chunking.chunker import Chunker
from collections import deque
from rdflib import Graph, RDF, RDFS, OWL, URIRef, BNode
from chunker import Chunker


class Locality(Chunker):
    """Naive locality-based chunker.
    For every named class in the ontology, generates a chunk containing
    that class and every class reachable within k hops along the
    class-subsumption hierarchy (rdfs:subClassOf, traversed as an
    undirected relation, i.e. both ancestors and descendants count as
    "neighbours"). For this early approach k is locked to 2.
    """

    LOCKED_K = 2

    def __init__(self, k=2):
        super().__init__()
        if k != self.LOCKED_K:
            print(
                f"[Locality] k={k} was requested but this chunker is locked "
                f"to k={self.LOCKED_K}; ignoring the requested value."
            )
        self.k = self.LOCKED_K

    def _get_named_classes(self):
        """Return the set of named classes."""
        classes = set()
        for s in self.onto.subjects(RDF.type, OWL.Class):
            if isinstance(s, URIRef) and s != OWL.Thing:
                classes.add(s)
        return classes

    def _build_adjacency(self, classes):
        """Build an undirected adjacency map over the subsumption graph."""
        adjacency = {c: set() for c in classes}
        for s, _, o in self.onto.triples((None, RDFS.subClassOf, None)):
            if isinstance(s, BNode) or isinstance(o, BNode):
                continue
            if s in classes and o in classes and s != o:
                adjacency[s].add(o)
                adjacency[o].add(s)
        return adjacency

    def _neighbourhood(self, seed, adjacency):
        """BFS over adjacency collecting all nodes within k hops of seed."""
        visited = {seed}
        frontier = deque([(seed, 0)])
        while frontier:
            node, depth = frontier.popleft()
            if depth == self.k:
                continue
            for neighbour in adjacency[node]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    frontier.append((neighbour, depth + 1))
        return visited

    def _build_chunk_graph(self, class_set):
        """Materialise a chunk as a graph."""
        chunk = Graph()
        for ns_prefix, ns_uri in self.onto.namespaces():
            chunk.bind(ns_prefix, ns_uri)
        for c in class_set:
            chunk.add((c, RDF.type, OWL.Class))
            for _, _, label in self.onto.triples((c, RDFS.label, None)):
                chunk.add((c, RDFS.label, label))
            for _, _, comment in self.onto.triples((c, RDFS.comment, None)):
                chunk.add((c, RDFS.comment, comment))
            for _, _, parent in self.onto.triples((c, RDFS.subClassOf, None)):
                if parent in class_set:
                    chunk.add((c, RDFS.subClassOf, parent))
        return chunk

    def generate_chunks(self):
        """Populate self.chunks with one locality chunk per named class."""
        if self.onto is None:
            raise ValueError("No ontology has been loaded; call input() first.")
        self.chunks = []
        classes = self._get_named_classes()
        adjacency = self._build_adjacency(classes)
        for seed in classes:
            class_set = self._neighbourhood(seed, adjacency)
            self.chunks.append(self._build_chunk_graph(class_set))
        return self.chunks

