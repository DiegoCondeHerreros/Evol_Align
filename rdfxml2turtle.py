from rdflib import Graph
from pathlib import Path
import sys

def convert_folder(folder: Path):
    folder = folder.resolve()
    rdf_files = list(folder.glob("*.rdf"))
    if not rdf_files:
        print(f"No .rdf files found in {folder}")
        return
    for f in rdf_files:
        out = f.with_suffix(".ttl")
        try:
            g = Graph().parse(str(f), format="xml")  # RDF/XML
            g.serialize(destination=str(out), format="turtle")
            print(f"Converted: {f.name} -> {out.name}")
        except Exception as e:
            print(f"Failed to convert {f.name}: {e}")

if __name__ == "__main__":
    # usage: python rdf_transform.py [folder_path]
    folder_arg = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    convert_folder(folder_arg)