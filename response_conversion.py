from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


def split_mapping_rows(text: str) -> list[str]:
    """
    Extract the contents of each MappingRow(...) block, while correctly handling:
    - nested parentheses in enum-like values
    - commas inside quoted strings
    - escaped quotes
    """
    start_token = "MappingRow("
    rows = []
    pos = 0

    while True:
        start = text.find(start_token, pos)
        if start == -1:
            break

        i = start + len(start_token)
        depth = 1
        in_string = False
        escape = False

        while i < len(text):
            ch = text[i]

            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == "'":
                    in_string = False
            else:
                if ch == "'":
                    in_string = True
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        rows.append(text[start + len(start_token):i])
                        pos = i + 1
                        break

            i += 1
        else:
            raise ValueError("Unterminated MappingRow(...) block found.")

    return rows


def extract_field(pattern: str, block: str, default: str = "") -> str:
    match = re.search(pattern, block, re.DOTALL)
    return match.group(1) if match else default


def parse_mapping_row(block: str) -> dict[str, str]:
    return {
        "record_id": extract_field(r"record_id='(.*?)'", block),
        "subject_id": extract_field(r"subject_id='(.*?)'", block),
        "object_id": extract_field(r"object_id='(.*?)'", block),
        "predicate_id": extract_field(r"predicate_id=<[^:]+:\s*'(.*?)'>", block),
        "mapping_justification": extract_field(
            r"mapping_justification=<[^:]+:\s*'(.*?)'>", block
        ),
        "author_id": extract_field(r"author_id='(.*?)'", block),
        "confidence": extract_field(r"confidence=([0-9.]+)", block),
        "comment": extract_field(r"comment='(.*?)'\s*$", block),
    }


def convert_alignment_file(input_path: Path, output_path: Path) -> int:
    text = input_path.read_text(encoding="utf-8").strip()
    mapping_blocks = split_mapping_rows(text)
    rows = [parse_mapping_row(block) for block in mapping_blocks]

    fieldnames = [
        "record_id",
        "subject_id",
        "object_id",
        "predicate_id",
        "mapping_justification",
        "author_id",
        "confidence",
        "comment",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            delimiter="\t",
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a serialized alignment-set file into TSV."
    )
    parser.add_argument("input_file", type=Path, help="Path to the input file")
    parser.add_argument("output_file", type=Path, help="Path to the output TSV file")
    args = parser.parse_args()

    row_count = convert_alignment_file(args.input_file, args.output_file)
    print(f"Wrote {row_count} alignment rows to {args.output_file}")


if __name__ == "__main__":
    main()
