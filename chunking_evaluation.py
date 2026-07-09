from llm_interface import LLM
from rdflib import Graph, Namespace, RDF, OWL, Literal
import csv
import os


class AlignmentEvaluation():

    def __init__(self, experiment):
        self.exp = experiment
        self.set_judge_model()

    def set_judge_model(self):
        # NOTE: Whilst LLM-as-a-judge has shown potential, there is
        # always the possibility of a simpler binary classification model
        # is there any way where we could use the a small human evaluation
        # session to fine tune an exisiting classifier? Do these even exist?
        model = LLM(
            model_family="Gemini",
            model="gemini-3.5-flash",
            params={"temperature": 0.0, "seed": 7264},
            context=None
        )
        self.judge = model

    def load_dummy_alignments(self, dir):
        path = f"{dir}/dummy_alignments.csv"
        alignments = []
        if not os.path.isfile(path):
            return alignments

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                alignment = ["dummy"]
                for i in row:
                    alignment.append(i)
                alignments.append(alignment)
            f.close()
        return alignments


    def load_reference_alignments(self, pair):
        path = f"{pair.path}/reference_sssom_alignments.ttl"
        alignments = []

        SSSOM = Namespace("https://w3id.org/sssom/")
        ref = Graph()
        ref.parse(path, format="turtle")

        for axiom in set(ref.subjects(RDF.type, OWL.Axiom)) | set(ref.subjects(RDF.type, SSSOM.Mapping)):
            subj = ref.value(axiom, SSSOM.subject_id)
            obj = ref.value(axiom, SSSOM.object_id)
            if subj is None or obj is None:
                continue

            pred = ref.value(axiom, SSSOM.predicate_id)
            conf = ref.value(axiom, SSSOM.confidence)

            alignment = [
                "real",
                str(subj),
                str(obj),
                str(pred) if pred else None,
                str(conf) if conf else None
            ]
            alignments.append(alignment)

        dummy = self.load_dummy_alignments(pair.path)
        for d in dummy:
            alignments.append(d)
        
        for row in alignments:
            pair.reference_alignments.append(row)
