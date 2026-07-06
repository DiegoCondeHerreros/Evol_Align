from llm_interface import LLM
from chunking_interface import ChunkingInterface
from system_prompt import SYSTEM_PROMPT
from structured_outputs import SSSOMAlignmentStrictCore as FORMAT
import os
from rdflib import Graph


class OntoPair:

    def __init__(self, domain, pair):
        self.domain = domain
        self.pair = pair
        self.set_files()

    def set_files(self):
        path = f"caseData/{self.domain}/{self.pair}"
        source_path = f"{path}/source.owl"
        target_path = f"{path}/target.owl"
        ref_path = f"{path}/reference_sssom_alignments.ttl"
        S = Graph()
        self.source = S.parse(source_path)
        T = Graph()
        self.target = T.parse(target_path)
        R = Graph()
        self.reference = R.parse(ref_path)


class DomainCase:

    def __init__(self, domain):
        self.domain = domain
        self.onto_pairs = self.set_pairs()

    def set_pairs(self):
        cases = [
            c for c in os.listdir(f"caseData/{self.domain}")
            if os.path.isdir(os.path.join(f"caseData/{self.domain}", c))
        ]
        pairs = []
        for c in cases:
            pairs.append(OntoPair(self.domain, c))
        return pairs


class ChunkingExperiment:

    def __init__(self):
        self.models = self.get_models()
        self.datasets = self.get_datasets()
        self.sys_prompt = SYSTEM_PROMPT

    def get_models(self):
        model_1 = LLM(
            model_family="OpenAI",
            model="gpt-5.5",
            params={"temperature": 0.0, "seed": 7264},
            context=None
        )
        model_2 = LLM(
            model_family="OpenAI",
            model="gpt-5.4-mini",
            params={"temperature": 0.0, "seed": 7264},
            context=None
        )
        model_3 = LLM(
            model_family="Gemini",
            model="gemini-3.5-flash",
            params={"temperature": 0.0, "seed": 7264},
            context=None
        )
        return [model_1, model_2, model_3]

    def get_datasets(self):
        domains = [
            d for d in os.listdir("caseData")
            if os.path.isdir(os.path.join("caseData", d))
        ]
        datasets = []
        for d in domains:
            datasets.append(DomainCase(d))
        return datasets

    def set_user_prompt(self, source, target):
        user_prompt = """"""
        return user_prompt

    def generate_alignments(self, pair):
        chunker = ChunkingInterface()
        pair.source_chunks = chunker.run_chunking(pair.source)
        pair.target_chunks = chunker.run_chunking(pair.target)
        for s in pair.source_chunks:
            for t in pair.target_chunks:
                u_prompt = self.set_user_prompt(s, t)
                for m in self.models:
                    response = m.prompt(message_list, FORMAT, None)


def run_experiment():
    exp = ChunkingExperiment()

    # NOTE: Generate chunks and alignments
    for domain in exp.datasets:
        print(f"Working on domain: {domain.domain}")
        for onto_pair in domain.onto_pairs:
            print(f"Working on ontology pair: {onto_pair.pair}")
            exp.generate_alignments(onto_pair)


run_experiment()
