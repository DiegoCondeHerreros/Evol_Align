import argparse
from pathlib import Path
from rdflib import Graph, Namespace, RDF, OWL, Literal
from pprint import pprint


def get_file_name(path):
    file_path = Path(path)
    file_name = file_path.stem
    return file_name


def review_alignment():
    decision = input(
        'Is the above refinement acceptable? Yes(y), No(n), Needs Refinement(r): ')
    decision_text = {
        'y': 'accept',
        'n': 'reject',
        'r': 'requires_refinement',
        '': 'unspecified'
    }[decision]

    comment = input('Provide a justification for your decision: ')
    return decision_text, comment


def process_alignments(path, uid, uname):
    SSSOM = Namespace("https://w3id.org/sssom/")
    SEMAPV = Namespace(
        "https://w3id.org/semapv/vocab/LevenshteinEditDistance/")

    g = Graph()
    g.parse(path, format="turtle")

    #########################################################################
    # NOTE: This section is just to count the number of loaded SSSOM mappings
    alignments = []

    for axiom in g.subjects(RDF.type, OWL.Axiom):
        subj = g.value(axiom, SSSOM.subject_id)
        obj = g.value(axiom, SSSOM.object_id)

        # Skip Axioms that are not SSSOM mappings
        if subj is None or obj is None:
            continue

        pred = g.value(axiom, SSSOM.predicate_id)
        conf = g.value(axiom, SSSOM.confidence)
        rule = g.value(axiom, SSSOM.curation_rule)

        alignments.append({
            "axiom": axiom,
            "subject_id": str(subj),
            "object_id": str(obj),
            "predicate_id": str(pred) if pred else None,
            "confidence": float(conf) if conf else None,
            "curation_rule": str(rule) if rule else None,
        })

    print(f"Loaded {len(alignments)} SSSOM alignments")
    print('')
    print('======================BEGINNING REVIEW===========================')
    print('')

    #########################################################################

    count = 1
    for axiom in g.subjects(RDF.type, OWL.Axiom):
        subj = g.value(axiom, SSSOM.subject_id)
        obj = g.value(axiom, SSSOM.object_id)

        print(f'Alignment {count} of {len(alignments)}')
        print('')
        count += 1
        # Skip Axioms that are not SSSOM mappings
        if subj is None or obj is None:
            continue

        pred = g.value(axiom, SSSOM.predicate_id)
        conf = g.value(axiom, SSSOM.confidence)
        rule = g.value(axiom, SSSOM.curation_rule)

        alignment = {
            "axiom": axiom,
            "subject_id": str(subj),
            "object_id": str(obj),
            "predicate_id": str(pred) if pred else None,
            "confidence": float(conf) if conf else None,
            "curation_rule": str(rule) if rule else None,
        }
        pprint(alignment)

        decision, comment = review_alignment()

        # NOTE: I extend SSSOM to cover the review process
        g.add((axiom, SSSOM.reviewer_id, Literal(uid)))
        g.add((axiom, SSSOM.reviewer_label, Literal(uname)))
        g.add((axiom, SSSOM.reviewer_decision, Literal(decision)))
        g.add((axiom, SSSOM.reviewer_justification, Literal(comment)))

        print('')
        print('====================================================================')
        print('')

    print('======================REVIEW COMPLETE===========================')
    return g


def set_reviewer_id() -> str:
    set = False
    while not set:
        isOrcid = input(
            'Are you using an ORCID as your id? Y/n (type h for help): ')
        if isOrcid == 'h':
            print('Used to identify the person that reviewed and confirmed the mapping. Recommended to be an ORCID or otherwise identifying URI')
            continue
        elif isOrcid in ['', 'Y', 'y']:
            uid = 'orcid:' + input('Enter your ORCID: ')
            set = True
        else:
            uid = input('Enter your URI (include namespace or prefix): ')
            set = True
    return uid


def set_reviewer_name() -> str:
    name = input('Enter your name: ')
    return name


def run(args):
    alignments_path = args.alignments
    uid = set_reviewer_id()
    name = set_reviewer_name()
    reviewed_alignments = process_alignments(alignments_path, uid, name)
    reviewed_alignments.serialize(
        f'output/{get_file_name(alignments_path)}_{name}.ttl', format='turtle'
    )


def main():
    parser = argparse.ArgumentParser(
        prog="Alignemnt Review",
        description="A simple tool to review SSSOM alignments"
    )
    parser.add_argument(
        "-a",
        type=str,
        help="Path to the SSSOM alignments set",
        dest="alignments",
        required=True
    )
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
