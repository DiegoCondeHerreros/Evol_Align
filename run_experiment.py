from site import execsitecustomize

from chunking_experiment import ChunkingExperiment
from chunking_evaluation import AlignmentEvaluation
from pushover_notifier import PushoverNotifier


def run_experiment():
    methods = ["Locality", "Taxonomic", "Semantic"]
    exp = ChunkingExperiment()

    # NOTE: Generate chunks and alignments
    for c in methods:
        for m in exp.models:
            for domain in exp.datasets:
                print(f"Working on domain: {domain.domain}")
                for onto_pair in domain.onto_pairs:
                    print(f"Working on ontology pair: {onto_pair.pair}")
                    exp.generate_alignments(onto_pair, c, m)
                    exp.write_alignments(onto_pair)

    # NOTE: Evaluate alignments:
    evl = AlignmentEvaluation(exp)
    for domain in exp.datasets:
        print(f"Evaluating domain: {domain.domain}")
        for onto_pair in domain.onto_pairs:
            print(f"Working on ontology pair: {onto_pair.pair}")
            evl.load_reference_alignments(onto_pair)


if __name__ == "__main__":
    noti = PushoverNotifier()
    try:
        run_experiment()
    except Exception as e:
        noti.send(
            message=str(type(e).__name__),
            title="🚨 An error has occured 🚨"
        )
        raise e
