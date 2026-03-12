from __future__ import annotations
from datetime import date
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict, HttpUrl, constr

class TestStructure(BaseModel):
    response: str

# -----------------------------
# Core "row" of SSSOM mappings
# -----------------------------
class SSSOMMapping(BaseModel):
    """
    Represents one mapping row in a TSV-faithful JSON representation.
    Column set mirrors typical SSSOM TSV headers.

    If your JSON Schema restricts enums/patterns more strictly, add them here.
    """
    model_config = ConfigDict(extra="forbid")

    subject_id: constr(min_length=1) = Field(..., description="Subject CURIE/IRI")
    subject_label: Optional[str] = Field(None, description="Human label for subject")

    predicate_id: constr(min_length=1) = Field(..., description="Mapping predicate CURIE/IRI")

    object_id: constr(min_length=1) = Field(..., description="Object CURIE/IRI")
    object_label: Optional[str] = Field(None, description="Human label for object")

    mapping_justification: Optional[str] = Field(
        None, description="Justification code/term for why mapping holds"
    )

    mapping_date: Optional[date] = Field(
        None, description="Date the mapping was created (ISO 8601 date)"
    )
    author_id: Optional[str] = Field(None, description="Author CURIE/IRI")

    subject_source: Optional[str] = Field(None, description="Source ontology/dataset for subject")
    subject_source_version: Optional[str] = Field(None, description="Version string for subject source")

    object_source: Optional[str] = Field(None, description="Source ontology/dataset for object")
    object_source_version: Optional[str] = Field(None, description="Version string for object source")

    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Confidence in [0,1]"
    )

    comment: Optional[str] = Field(None, description="Free-text comments")


# ---------------------------------
# Top-level SSSOM alignment document
# ---------------------------------
class SSSOMAlignmentSet(BaseModel):
    """
    Top-level container for a TSV-faithful JSON encoding of an SSSOM mapping set.
    """
    model_config = ConfigDict(extra="forbid")

    # From your snippet:
    sssom_version: Optional[constr(min_length=1)] = Field(
        None, description="SSSOM spec version the set claims compliance with"
    )

    mapping_set_id: constr(pattern=r"^https?://\S+$") = Field(
        ..., description="Globally unique ID for the mapping set (IRI-like)"
    )

    mapping_set_version: Optional[constr(min_length=1)] = Field(
        None, description="Version string for the mapping set"
    )

    # Required in your snippet
    license: constr(min_length=1) = Field(..., description="License identifier/IRI")
    subject_source: constr(min_length=1) = Field(..., description="Default subject source")
    object_source: constr(min_length=1) = Field(..., description="Default object source")

    subject_type: constr(min_length=1) = Field(..., description="Type/class of subject terms")
    object_type: constr(min_length=1) = Field(..., description="Type/class of object terms")

    # curie_map is typically { "prefix": "https://base/" }
    curie_map: Dict[str, constr(min_length=1)] = Field(
        ..., description="Prefix map for CURIE expansion"
    )

    # The list of mapping rows
    mappings: List[SSSOMMapping] = Field(..., description="List of mapping rows")

    # If your schema includes additional top-level metadata (creator, title, etc.),
    # add Optional[...] fields here.


# Convenience alias if your code wants "structure" to be a single class name
Structure = SSSOMAlignmentSet