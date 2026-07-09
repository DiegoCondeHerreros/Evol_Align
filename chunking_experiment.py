from llm_interface import LLM
from chunking_interface import ChunkingInterface
from system_prompt import SYSTEM_PROMPT
from structured_outputs import SSSOMAlignmentStrictCore as FORMAT
from utils import rough_similarty
from sentence_transformers import SentenceTransformer
import os
import csv
from rdflib import Graph
import tiktoken
from rich.console import Group
from rich.live import Live
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text


class OntoPair:

    def __init__(self, domain, pair):
        self.domain = domain
        self.pair = pair
        self.set_files()

    def set_files(self):
        path = f"caseData/{self.domain}/{self.pair}"
        self.path = path
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
        self.sim_model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2")

        model_1 = LLM(
            model_family="OpenAI",
            model="gpt-4.1-mini",
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
        user_prompt = {
            "role": "user",
            "content": f"""
            `source`: {source.serialize(format="turtle")}

            `target`: {target.serialize(format="turtle")}
            """
        }
        return user_prompt

    def estimate_prompt_tokens(self, model, messages):
        # NOTE: This uses OpenAI's token estimator
        supported_models = ["gpt-4o", "gpt-4o-mini, gpt-4-turbo"]
        if model.model not in supported_models:
            m_name = "gpt-4"
        else:
            m_name = model.model
        encoding = tiktoken.encoding_for_model(m_name)

        # NOTE: Default values from OpenAI example
        tokens_per_message = 3
        tokens_per_name = 1

        num_tokens = 0
        for m in messages:
            num_tokens += tokens_per_message
            for key, value in m.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3
        return num_tokens

    def resolve_dupes(self, alignments):
        # NOTE: Duplicates of alignments may exist resolve them based off confidence first and then order of creation second

        # [0] mapping_id
        # [1] subject
        # [2] object
        # [3] predicate
        # [4] justification
        # [5] confidence
        # [6] natural language explanation
        # [7] chunking method
        # [8] llm

        final_alignments = []
        for a in alignments:
            active_index = alignments.index(a)
            active_confidence = a[5]
            beaten = False
            for a1 in alignments:
                if [a[1], a[2]] == [a1[1], a1[2]]:
                    if active_confidence < a1[5]:
                        beaten = True
                    if active_index < alignments.index(a1):
                        beaten = True
            if not beaten:
                final_alignments.append(a)
        return final_alignments

    def generate_alignments(self, pair, chunk, model):
        chunker = ChunkingInterface()
        pair.source_chunks = chunker.run_chunking(chunk, pair.source)
        print(f"Generated {len(pair.source_chunks)} from source")
        pair.target_chunks = chunker.run_chunking(chunk, pair.target)
        print(f"Generated {len(pair.target_chunks)} from target")
        max_chunks = len(pair.source_chunks)*len(pair.target_chunks)
        all_alignments = []
        accepted_chunks = 0
        chunk_counter = 1
        threshold = 0.6

        progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(
                bar_width=None,
                style="grey35",
                complete_style="green",
                finished_style="bold green"
            ),
            TextColumn("{task.completed}/{task.total}"),
            TextColumn("{task.percentage:>3.0f}%"),
        )
        task = progress.add_task("Comparing chunks...", total=max_chunks)
        log = Text(" ")

        def render():
            return Group(progress, log)

        with Live(render(), refresh_per_second=10) as bar:
            for s in pair.source_chunks:
                for t in pair.target_chunks:
                    progress.update(task, advance=1)
                    bar.update(render())
                    sim = rough_similarty(s, t, self.sim_model)["score"]
                    chunk_counter += 1
                    if sim > threshold:
                        u_prompt = self.set_user_prompt(s, t)
                        message_list = [self.sys_prompt, u_prompt]
                        tokens = self.estimate_prompt_tokens(
                            model, message_list)
                        log = Text(f"""Estimated prompt token usage: {tokens} tokens

Estimated similarity between chunks: {rough_similarty(s, t, self.sim_model)["score"]}

=====================================

Running prompt...""")
                        bar.update(render())
                        accepted_chunks += 1
                        response = model.prompt(message_list, FORMAT, None)
                        maps = response.mappings
                        for m in maps:
                            log = Text(f"{m.subject_id} | {
                                m.predicate_id} | {m.object_id}")
                            bar.update(render())
                            m = list(m.__dict__.values())
                            m.append(chunk)
                            m.append(model.model)
                            all_alignments.append(m)

                            raise Exception
                    bar.update(render())
        pair.chunk_cull = [chunk, max_chunks, threshold, accepted_chunks]
        pair.llm_alignments = self.resolve_dupes(all_alignments)

    def write_alignments(self, pair):
        headers = [
            "Mapping_id",       # 0
            "Subject",          # 1
            "Object",           # 2
            "Predicate",        # 3
            "Justification",    # 4
            "Confidence",       # 5
            "Comment",          # 6
            "Chunking_Method",  # 7
            "Model_Name"        # 8
        ]

        culling_headers = [
            "Chunking_Method",          # 0
            "Total_Chunks_to_Compare",  # 1
            "Acceptance_Threshold",     # 2
            "Accepted_Chunks"           # 3
        ]

        print("Saving alignments...")
        align_output = f"{pair.path}/llm_alignments.csv"
        cull_output = f"{pair.path}/culling_performance.csv"

        align_exists = os.path.isfile(align_output)
        cull_exists = os.path.isfile(cull_output)

        with open(align_output, mode="a", newline="", encoding="utf-8") as align:
            writer = csv.writer(align)
            if not align_exists:
                print("No previous alignments found, creating new file...")
                writer.writerow(headers)
            else:
                print("Alignments found, extending...")
            for row in pair.llm_alignments:
                writer.writerow(row)
            align.close()
            print("Alignments saved successfully")

        with open(cull_output, mode="a", newline="", encoding="utf-8") as cull:
            writer = csv.writer(cull)
            if not cull_exists:
                print("No previous culling performance found, creating new file...")
                writer.writerow(culling_headers)
            else:
                print("Culling performance found, appending...")
            for row in pair.chunk_cull:
                writer.writerow(row)
            cull.close()
            print("Alignments saved successfully")
