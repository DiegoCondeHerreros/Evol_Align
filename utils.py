import argparse

from collections import defaultdict
from typing import Dict, Iterable, Tuple, Any
import math

import numpy as np
from rdflib import Graph, RDFS, RDF, OWL, URIRef
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class KeyValue(argparse.Action):
    # Constructor calling
    def __call__(self, parser, namespace,
                 values, option_string=None):
        setattr(namespace, self.dest, dict())

        for value in values:
            # split it into key and value
            key, value = value.split('=')
            # assign into dictionary
            getattr(namespace, self.dest)[key] = float(value)


def rough_similarty(onto_1: Graph, onto_2: Graph, model):
    top_k = 1
    weights = {
        "textual": 0.60,
        "neighbourhood": 0.35,
        "type": 0.05,
    }

    def entities(g):
        found = set()

        for cls in [OWL.Class, RDF.Property, OWL.ObjectProperty, OWL.DatatypeProperty]:
            for s in g.subjects(RDF.type, cls):
                if isinstance(s, URIRef):
                    found.add(s)

        for s, p, o, in g:
            if isinstance(s, URIRef):
                found.add(s)
            if isinstance(o, URIRef):
                found.add(o)
        return sorted(found, key=str)

    def label_for(g, e):
        label = list(g.objects(e, RDFS.label))
        comments = list(g.objects(e, RDFS.comment))
        parts = [str(x) for x in label + comments]

        if not parts:
            iri = str(e)
            local = iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]
            parts.append(local.replace("_", " ").replace("-", " "))

        return " ".join(parts)

    def neighbor_signature(g, e):
        sig = set()

        for _, p, o in g.triples((e, None, None)):
            sig.add(f"out:{local_name(p)}:{local_name(o)}")
        for s, p, _ in g.triples((None, None, e)):
            sig.add(f"in:{local_name(p)}:{local_name(s)}")

        return sig

    def type_signature(g, e):
        return {local_name(o) for o in g.objects(e, RDF.type)}

    def local_name(x):
        x = str(x)
        return x.split("#", 1)[-1].rsplit("/", 1)[-1]

    def jaccard(a, b):
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    e1 = entities(onto_1)
    e2 = entities(onto_2)

    if not e1 or not e2:
        return {
            "score": 0.0,
            "textual_similarity": 0.0,
            "neighbourhood_similarity": 0.0,
            "type_similarity": 0.0,
            "matches": [],
        }

    labels1 = [label_for(onto_1, e) for e in e1]
    labels2 = [label_for(onto_2, e) for e in e2]

    emb1 = model.encode(labels1, normalize_embeddings=True)
    emb2 = model.encode(labels2, normalize_embeddings=True)

    sim_matrix = cosine_similarity(emb1, emb2)
    matches = []
    text_scores = []
    neighborhood_scores = []
    type_scores = []

    for i, ent1 in enumerate(e1):
        best_indices = np.argsort(sim_matrix[i])[-top_k:][::-1]

        for j in best_indices:
            ent2 = e2[j]
            text_sim = float(sim_matrix[i, j])
            neigh_sim = jaccard(
                neighbor_signature(onto_1, ent1),
                neighbor_signature(onto_2, ent2),
            )
            type_sim = jaccard(
                type_signature(onto_1, ent1),
                type_signature(onto_2, ent2)
            )
            combined = (
                weights["textual"] * text_sim
                + weights["neighbourhood"] * neigh_sim
                + weights["type"] * type_sim
            )
            matches.append({
                "entity_a": str(ent1),
                "entity_b": str(ent2),
                "textual_similarity": text_sim,
                "neighborhood_similarity": neigh_sim,
                "type_similarity": type_sim,
                "combined_similarity": combined
            })

            text_scores.append(text_sim)
            neighborhood_scores.append(neigh_sim)
            type_scores.append(type_sim)

    overall_text = float(np.mean(text_scores))
    overall_neighbourhood = float(np.mean(neighborhood_scores))
    overall_type = float(np.mean(type_scores))
    final_score = (
        weights["textual"] * overall_text
        + weights["neighbourhood"] * overall_neighbourhood
        + weights["type"]
    )

    matches = sorted(
        matches,
        key=lambda x: x["combined_similarity"],
        reverse=True,
    )

    return {
        "score": final_score,
        "textual_similarity": overall_text,
        "neighborhood_similarity": overall_neighbourhood,
        "type_similarity": overall_type,
        "matches": matches
    }
