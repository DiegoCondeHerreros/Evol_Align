#!/usr/bin/env python3
"""
Convert Alignment API Turtle files in a folder to SSSOM RDF/OWL (Turtle).

For each *.ttl file in INPUT_DIR, this script:
  - parses the alignment (Alignment API format, as in OAEI),
  - extracts cells with entity1, entity2, relation, measure (+ optional cid),
  - generates a SSSOM MappingSet as OWL/RDF Turtle,
  - writes OUTPUT_DIR/<stem>_sssom.ttl (or in the same dir if no output dir).

Usage:
    python alignment_to_sssom_rdf.py INPUT_DIR [--out-dir OUTPUT_DIR]

Dependencies:
    pip install rdflib
"""

import argparse
from pathlib import Path

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, OWL, XSD, NamespaceManager

# Namespaces for output
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SSSOM = Namespace("https://w3id.org/sssom/")
SEMAPV = Namespace("https://w3id.org/semapv/vocab/")


def local_name(uri):
    """
    Return something like the local name of a URI.

    For your alignments, URIs look like:
      http://.../alignmentonto1
    so local_name(...) will be 'alignmentonto1'.
    We then match by suffix (e.g. endswith('onto1')).
    """
    s = str(uri)
    if "#" in s:
        return s.rsplit("#", 1)[-1]
    return s.rstrip("/").rsplit("/", 1)[-1]


def find_predicates_and_classes(g: Graph):
    """
    Discover Alignment API predicates and classes by *suffix* of their local name:
      - Alignment, Cell (classes)
      - onto1, onto2, map, entity1, entity2, measure, relation (predicates)
      - cid (predicate; may be in a different namespace)

    Returns a dict with keys:
      onto1, onto2, map, entity1, entity2, measure, relation, cid, Alignment, Cell
    """
    onto1_pred = onto2_pred = map_pred = entity1_pred = entity2_pred = None
    measure_pred = relation_pred = cid_pred = None
    alignment_class = cell_class = None

    for s, p, o in g.triples((None, None, None)):
        lname_p = local_name(p)

        # Match by suffix because your IRIs look like ".../alignmentonto1"
        if lname_p.endswith("onto1"):
            onto1_pred = p
        elif lname_p.endswith("onto2"):
            onto2_pred = p
        elif lname_p.endswith("map"):
            map_pred = p
        elif lname_p.endswith("entity1"):
            entity1_pred = p
        elif lname_p.endswith("entity2"):
            entity2_pred = p
        elif lname_p.endswith("measure"):
            measure_pred = p
        elif lname_p.endswith("relation"):
            relation_pred = p
        elif lname_p.endswith("cid"):
            cid_pred = p

        # Classes Alignment and Cell
        if p == RDF.type and isinstance(o, URIRef):
            lname_o = local_name(o)
            if lname_o.endswith("Alignment"):
                alignment_class = o
            elif lname_o.endswith("Cell"):
                cell_class = o

    return {
        "onto1": onto1_pred,
        "onto2": onto2_pred,
        "map": map_pred,
        "entity1": entity1_pred,
        "entity2": entity2_pred,
        "measure": measure_pred,
        "relation": relation_pred,
        "cid": cid_pred,  # may be None
        "Alignment": alignment_class,
        "Cell": cell_class,
    }


def convert_alignment_file(in_path: Path, out_path: Path):
    print(f"Processing {in_path} -> {out_path}")

    g_in = Graph()
    g_in.parse(in_path, format="turtle")

    preds = find_predicates_and_classes(g_in)

    # Required pieces (cid is optional)
    required_keys = [
        "onto1",
        "onto2",
        "map",
        "entity1",
        "entity2",
        "measure",
        "relation",
        "Alignment",
    ]
    missing = [k for k in required_keys if preds.get(k) is None]
    if missing:
        print(f"  [WARN] Missing expected elements in {in_path.name}: {missing}. Skipping.")
        return

    onto1_pred = preds["onto1"]
    onto2_pred = preds["onto2"]
    map_pred = preds["map"]
    entity1_pred = preds["entity1"]
    entity2_pred = preds["entity2"]
    measure_pred = preds["measure"]
    relation_pred = preds["relation"]
    cid_pred = preds["cid"]  # may be None
    alignment_class = preds["Alignment"]

    # Find all alignments in this file
    alignments = set(s for s, _, _ in g_in.triples((None, RDF.type, alignment_class)))
    if not alignments:
        print(f"  [WARN] No :Alignment instances found in {in_path.name}. Skipping.")
        return

    # New graph for SSSOM output
    g_out = Graph()
    nm = NamespaceManager(g_out)
    nm.bind("rdf", RDF)
    nm.bind("owl", OWL)
    nm.bind("xsd", XSD)
    nm.bind("skos", SKOS)
    nm.bind("sssom", SSSOM)
    nm.bind("semapv", SEMAPV)
    g_out.namespace_manager = nm

    # One mapping set per file
    mapping_set_iri = URIRef(f"http://example.org/mappings/{in_path.stem}")
    g_out.add((mapping_set_iri, RDF.type, OWL.Ontology))
    g_out.add((mapping_set_iri, RDF.type, SSSOM.MappingSet))

    all_mapping_nodes = []

    subj_source = obj_source = None

    for aln in alignments:
        # subject_source and object_source (ontologies)
        s1 = g_in.value(aln, onto1_pred)
        s2 = g_in.value(aln, onto2_pred)
        if s1 and subj_source is None:
            subj_source = s1
        if s2 and obj_source is None:
            obj_source = s2

        # Iterate over mapping cells
        for cell in g_in.objects(aln, map_pred):
            # cid is optional and may be in a different namespace
            cid_val = g_in.value(cell, cid_pred) if cid_pred is not None else None
            subj = g_in.value(cell, entity1_pred)
            obj = g_in.value(cell, entity2_pred)
            measure = g_in.value(cell, measure_pred)
            rel = g_in.value(cell, relation_pred)

            if subj is None or obj is None:
                # Incomplete mapping, skip
                continue

            # Build mapping IRI
            cid_str = (
                str(cid_val)
                if isinstance(cid_val, Literal)
                else (cid_val and str(cid_val)) or ""
            )
            if cid_str:
                mapping_node = URIRef(f"{mapping_set_iri}#m{cid_str}")
            else:
                # Fallback: not ideal, but ensures uniqueness when cid is absent
                mapping_node = URIRef(
                    f"{mapping_set_iri}#m{abs(hash((subj, obj)))}"
                )

            all_mapping_nodes.append(mapping_node)

            # Add SSSOM mapping triples
            g_out.add((mapping_node, RDF.type, SSSOM.Mapping))
            if cid_str:
                g_out.add((mapping_node, SSSOM.record_id, Literal(cid_str)))

            g_out.add((mapping_node, SSSOM.subject_id, subj))

            # Map Alignment "=" to skos:exactMatch; otherwise skos:relatedMatch
            if isinstance(rel, Literal) and str(rel) == "=":
                pred_uri = SKOS.exactMatch
            else:
                pred_uri = SKOS.relatedMatch

            g_out.add((mapping_node, SSSOM.predicate_id, pred_uri))
            g_out.add((mapping_node, SSSOM.object_id, obj))

            # measure -> confidence
            if measure is not None:
                try:
                    conf_val = float(str(measure))
                    g_out.add(
                        (mapping_node,
                         SSSOM.confidence,
                         Literal(conf_val, datatype=XSD.double))
                    )
                except ValueError:
                    # Non-numeric measures are ignored
                    pass

            # Neutral justification (not a placeholder; generic SEMAPV type)
            g_out.add(
                (mapping_node,
                 SSSOM.mapping_justification,
                 SEMAPV.UnspecifiedMatching)
            )

    # Add mapping set–level links, if we discovered sources
    if subj_source is not None:
        g_out.add((mapping_set_iri, SSSOM.subject_source, subj_source))
    if obj_source is not None:
        g_out.add((mapping_set_iri, SSSOM.object_source, obj_source))

    # Link mapping set to all mappings
    for m in set(all_mapping_nodes):
        g_out.add((mapping_set_iri, SSSOM.mappings, m))

    # Serialize
    out_path.parent.mkdir(parents=True, exist_ok=True)
    g_out.serialize(destination=str(out_path), format="turtle")
    print(f"  [OK] Wrote {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert Alignment API Turtle files to SSSOM RDF/OWL."
    )
    parser.add_argument("input_dir", help="Input directory containing .ttl alignment files")
    parser.add_argument(
        "--out-dir", help="Output directory (default: same as input)", default=None
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    out_dir = Path(args.out_dir) if args.out_dir else input_dir

    if not input_dir.is_dir():
        raise SystemExit(f"Input path is not a directory: {input_dir}")

    for ttl_path in sorted(input_dir.glob("*.ttl")):
        out_path = out_dir / f"{ttl_path.stem}_sssom.ttl"
        convert_alignment_file(ttl_path, out_path)


if __name__ == "__main__":
    main()
