from collections import deque
from rdflib import Graph, RDF, RDFS, OWL, URIRef
from chunker import Chunker


class Semantic(Chunker):

    def __init__(self):
        super().__init__()

    def _get_named_classes(self):
        classes = set()
        for s in self.onto.subjects(RDF.type, OWL.Class):
            if isinstance(s, URIRef) and s != OWL.Thing:
                classes.add(s)
        return classes

    def _outgoing(self, concept, named_classes):

        items = []

        for sub in self.onto.subjects(RDFS.subClassOf, concept):
            if isinstance(sub, URIRef):
                items.append(({(sub, RDFS.subClassOf, concept)}, sub))

        for eq in self.onto.objects(concept, OWL.equivalentClass):
            if isinstance(eq, URIRef):
                items.append(({(concept, OWL.equivalentClass, eq)}, eq))
        for eq in self.onto.subjects(OWL.equivalentClass, concept):
            if isinstance(eq, URIRef):
                items.append(({(eq, OWL.equivalentClass, concept)}, eq))

        for dj in self.onto.objects(concept, OWL.disjointWith):
            if isinstance(dj, URIRef):
                items.append(({(concept, OWL.disjointWith, dj)}, dj))
        for dj in self.onto.subjects(OWL.disjointWith, concept):
            if isinstance(dj, URIRef):
                items.append(({(dj, OWL.disjointWith, concept)}, dj))

        for prop in self.onto.subjects(RDFS.domain, concept):
            for rng in self.onto.objects(prop, RDFS.range):
                if isinstance(rng, URIRef) and rng in named_classes:
                    triples = {
                        (prop, RDFS.domain, concept),
                        (prop, RDFS.range, rng),
                    }
                    items.append((triples, rng))

        return items

    def _extract_module(self, start, named_classes=None):
        
        if named_classes is None:
            named_classes = self._get_named_classes()
        excluded = set()
        for dj in self.onto.objects(start, OWL.disjointWith):
            excluded.add((start, OWL.disjointWith, dj))
            excluded.add((dj, OWL.disjointWith, start))
        for dj in self.onto.subjects(OWL.disjointWith, start):
            excluded.add((dj, OWL.disjointWith, start))
            excluded.add((start, OWL.disjointWith, dj))

        visited = set()
        vertices = set()
        edges = set()
        to_visit = deque([start])

        while to_visit:
            concept = to_visit.popleft()
            if concept in visited:
                continue
            visited.add(concept)
            vertices.add(concept)

            for triples, target in self._outgoing(concept, named_classes):
                if triples & excluded:
                    continue
                edges |= triples
                if target is not None:
                    vertices.add(target)
                    if target not in visited:
                        to_visit.append(target)

        return vertices, edges

    def _build_chunk_graph(self, vertices, edges):
        chunk = Graph()
        for prefix, ns in self.onto.namespaces():
            chunk.bind(prefix, ns)

        for v in vertices:
            chunk.add((v, RDF.type, OWL.Class))
            for label in self.onto.objects(v, RDFS.label):
                chunk.add((v, RDFS.label, label))
            for comment in self.onto.objects(v, RDFS.comment):
                chunk.add((v, RDFS.comment, comment))

        for (s, p, o) in edges:
            chunk.add((s, p, o))
            if p in (RDFS.domain, RDFS.range):
                # `s` is a property; declare and annotate it.
                chunk.add((s, RDF.type, OWL.ObjectProperty))
                for label in self.onto.objects(s, RDFS.label):
                    chunk.add((s, RDFS.label, label))

        return chunk

    def extract_module(self, start):
        if self.onto is None:
            raise ValueError("No ontology has been loaded; call input() first.")
        if not isinstance(start, URIRef):
            start = URIRef(start)
        vertices, edges = self._extract_module(start)
        return self._build_chunk_graph(vertices, edges)

    def generate_chunks(self):
        if self.onto is None:
            raise ValueError("No ontology has been loaded; call input() first.")

        self.chunks = []
        named_classes = self._get_named_classes()
        for concept in named_classes:
            vertices, edges = self._extract_module(concept, named_classes)
            self.chunks.append(self._build_chunk_graph(vertices, edges))

        return self.chunks
