from chunking_experiment import ChunkingExperiment
from utils import rough_similarty
from rdflib import Graph
from sentence_transformers import SentenceTransformer


def chunk_sim_test():
    c_1 = Graph()
    c_2 = Graph()
    c_1.parse(data="""
    @prefix : <http://edas#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

    :AcceptedPaper a owl:Class ;
        rdfs:subClassOf :Paper .

    :ActivePaper a owl:Class ;
        rdfs:subClassOf :Paper .

    :MealMenu a owl:Class ;
        rdfs:subClassOf :Document .

    :PendingPaper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Programme a owl:Class ;
        rdfs:subClassOf :Document .

    :PublishedPaper a owl:Class ;
        rdfs:subClassOf :Paper .

    :RejectedPaper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Review a owl:Class ;
        rdfs:subClassOf :Document .

    :Slideset a owl:class ;
        rdfs:subClassOf :Document .

    :WithdrawnPaper a owl:class ;
        rdfs:subClassOf :Paper .

    :Document a owl:Class .

    :Paper a owl:Class ;
        rdfs:subClassOf :Document.
    """, format="turtle")
    c_2.parse(data="""
    @prefix : <http://ekaw#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

    :Camera_Ready_Paper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Conference_Paper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Demo_Paper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Industrial_Paper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Poster_Paper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Regular_Paper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Submitted_Paper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Workshop_Paper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Document a owl:Class .

    :Paper a owl:Class;
        rdfs:subClassOf :Document .
    """, format="turtle")

    print(rough_similarty(
        c_1, c_2, SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2"))["score"])


chunk_sim_test()
