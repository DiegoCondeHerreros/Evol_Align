from chunking_experiment import ChunkingExperiment
from utils import rough_similarty
from rdflib import Graph
from sentence_transformers import SentenceTransformer
from pushover_notifier import PushoverNotifier
from chunking_evaluation import AlignmentEvaluation
from types import SimpleNamespace

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


def noti_test():
    notifier = PushoverNotifier()
    notifier.send_high_priority(
        "This is a test"
    )


def build_alignment_test_experiment():
    exp = ChunkingExperiment.__new__(ChunkingExperiment)

    onto_pair = SimpleNamespace(
        domain="conference",
        pair="edas-ekaw",
        path="caseData/conference/edas-ekaw",
        reference_alignments=[],
        llm_alignments=[
            [
                "test-m1",
                "http://edas#Paper",
                "http://ekaw#Paper",
                "skos:exactMatch",
                "semapv:LexicalMatching",
                1.0,
                "Exact lexical and semantic match.",
                "test",
                "test-model",
            ],
            [
                "test-m2",
                "http://edas#AcceptedPaper",
                "http://ekaw#Accepted_Paper",
                "skos:exactMatch",
                "semapv:LexicalSimilarityThresholdMatching",
                0.95,
                "Equivalent accepted paper classes with different labels.",
                "test",
                "test-model",
            ],
        ],
    )
    domain = SimpleNamespace(domain="conference", onto_pairs=[onto_pair])

    exp.models = []
    exp.datasets = [domain]
    exp.sys_prompt = None
    return exp


def load_alignments_test():
    exp = build_alignment_test_experiment()

    evl = AlignmentEvaluation(exp)
    for domain in exp.datasets:
        print(f"Evaluating domain: {domain.domain}")
        for onto_pair in domain.onto_pairs:
            print(f"Working on ontology pair: {onto_pair.pair}")
            evl.load_reference_alignments(onto_pair)
            print(onto_pair.reference_alignments)


load_alignments_test()
# chunk_sim_test()
# noti_test()
