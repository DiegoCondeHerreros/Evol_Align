from __future__ import annotations
from datetime import date
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict, HttpUrl, constr, StringConstraints
from enum import Enum
from typing import Annotated

class TestStructure(BaseModel):
    response: str

# -----------------------------
# Core "row" of SSSOM mappings
# -----------------------------
class oldSSSOMMapping(BaseModel):
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
class oldSSSOMAlignmentSet(BaseModel):
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
    mappings: List[oldSSSOMMapping] = Field(..., description="List of mapping rows")

    # If your schema includes additional top-level metadata (creator, title, etc.),
    # add Optional[...] fields here.


# Convenience alias if your code wants "structure" to be a single class name
oldStructure = oldSSSOMAlignmentSet



# Updated structured response format

# ---------- Reusable constrained string types ----------

HttpUrlLike = Annotated[
    str,
    StringConstraints(pattern=r"^https?://\S+$"),
]

CurieOrIri = Annotated[
    str,
    StringConstraints(pattern=r"^(https?://\S+|[A-Za-z][A-Za-z0-9+.-]*:[^\s]+)$"),
]

CurieOrIriOrOrcid = Annotated[
    str,
    StringConstraints(
        pattern=r"^(https?://\S+|orcid:\d{4}-\d{4}-\d{4}-\d{3}[\dX]|[A-Za-z][A-Za-z0-9+.-]*:[^\s]+)$"
    ),
]

NonEmptyString = Annotated[
    str,
    StringConstraints(min_length=1),
]


# ---------- Enums ----------

class EntityType(str, Enum):
    owl_class = "owl:Class"
    owl_object_property = "owl:ObjectProperty"
    owl_datatype_property = "owl:DatatypeProperty"
    owl_named_individual = "owl:NamedIndividual"
    skos_concept = "skos:Concept"


class MappingPredicate(str, Enum):
    skos_exact_match = "skos:exactMatch"
    skos_close_match = "skos:closeMatch"
    skos_broad_match = "skos:broadMatch"
    skos_narrow_match = "skos:narrowMatch"
    skos_related_match = "skos:relatedMatch"
    owl_same_as = "owl:sameAs"
    owl_equivalent_class = "owl:equivalentClass"
    owl_equivalent_property = "owl:equivalentProperty"
    rdfs_subclass_of = "rdfs:subClassOf"
    rdfs_subproperty_of = "rdfs:subPropertyOf"


class SemaPVJustification(str, Enum):
    mapping_review = "semapv:MappingReview"
    manual_mapping_curation = "semapv:ManualMappingCuration"
    logical_reasoning = "semapv:LogicalReasoning"
    lexical_matching = "semapv:LexicalMatching"
    composite_matching = "semapv:CompositeMatching"
    unspecified_matching = "semapv:UnspecifiedMatching"
    semantic_similarity_threshold_matching = "semapv:SemanticSimilarityThresholdMatching"
    lexical_similarity_threshold_matching = "semapv:LexicalSimilarityThresholdMatching"
    mapping_chaining = "semapv:MappingChaining"
    mapping_inversion = "semapv:MappingInversion"
    structural_matching = "semapv:StructuralMatching"
    instance_based_matching = "semapv:InstanceBasedMatching"
    background_knowledge_based_matching = "semapv:BackgroundKnowledgeBasedMatching"


# ---------- Nested models ----------

class MappingRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: CurieOrIri | None = Field(
        default=None,
        description="Optional stable identifier for the row/record.",
    )
    subject_id: CurieOrIri
    object_id: CurieOrIri
    predicate_id: MappingPredicate
    mapping_justification: SemaPVJustification

    #author_id: CurieOrIriOrOrcid | list[CurieOrIriOrOrcid] | None = None

    confidence: Annotated[float, Field(ge=0, le=1)] | None = None
    comment: str | None = None


class SSSOMAlignmentStrictCore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sssom_version: NonEmptyString | None = Field(
        default=None,
        description="SSSOM spec version the set claims compliance with (optional).",
    )

    mapping_set_id: HttpUrlLike = Field(
        description="Globally unique ID for the mapping set (IRI-like)."
    )
    mapping_set_version: NonEmptyString | None = None
    mapping_set_title: str | None = None
    mapping_set_description: str | None = None

    creator_id: CurieOrIriOrOrcid | list[CurieOrIriOrOrcid] | None = Field(
        default=None,
        description=(
            "CURIE/IRI identifying creator(s). In TSV, multivalued are | separated; "
            "in JSON you can use either string or array."
        ),
    )

    license: HttpUrlLike = Field(
        description="License IRI (required by MappingSet)."
    )

    subject_source: CurieOrIri = Field(
        description="CURIE/IRI of the subject vocabulary/ontology."
    )
    object_source: CurieOrIri = Field(
        description="CURIE/IRI of the object vocabulary/ontology."
    )

    subject_source_version: str | None = None
    object_source_version: str | None = None

    subject_type: EntityType = Field(
        description="Entity type being mapped (alignment-level)."
    )
    object_type: EntityType = Field(
        description="Entity type being mapped (alignment-level)."
    )

    #curie_map: dict[str, HttpUrlLike] = Field(
    #    min_length=1,
    #    description="Prefix -> IRI expansion map (like TSV curie_map).",
    #)

    mappings: Annotated[list[MappingRow], Field(min_length=1)]
