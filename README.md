# Evol_Align

This repository hosts the materials developed for research on **parallel evolution of ontologies and ontology alignments**. This research has been performed as a collaboration between the Knowledge Engineering Group (KEG) and the Ontology Engineering Group (OEG).

## Overview

Evol_Align is a Python-based framework for generating, managing, and reviewing ontology alignments using Large Language Models (LLMs). The project integrates multiple LLM providers (OpenAI, Gemini, Ollama) to create SSSOM (Simple Standard for Sharing Ontology Mappings) formatted alignment sets with structured outputs.

## Repository Structure

### Core Python Modules

- **`llm_interface.py`** - Main interface for interacting with multiple LLM providers
  - Supports OpenAI, Google Gemini, and Ollama LLMs
  - Handles API key management and model parameter configuration
  - Provides unified `prompt()` method for all providers

- **`structured_outputs.py`** - Pydantic models for SSSOM alignment structures
  - Defines `SSSOMAlignmentStrictCore` for alignment set metadata
  - Defines `MappingRow` for individual ontology mappings
  - Includes enums for `EntityType`, `MappingPredicate`, and `SemaPVJustification`

- **`prompt_engineering.py`** - Prompt design and engineering utilities
  - Contains reusable prompts for ontology alignment tasks

- **`response_conversion.py`** - Utilities for converting LLM responses to SSSOM format
  - Handles conversion of LLM-generated text to structured mapping objects

- **`alignement_review.py`** - Interactive tool for manually reviewing and curating alignments
  - Load SSSOM alignments from Turtle format
  - Interactive review interface for accepting, rejecting, or refining mappings
  - Extends SSSOM with reviewer metadata (reviewer_id, reviewer_decision, reviewer_justification)

- **`utils.py`** - Utility functions
  - Custom argparse actions for key-value parameter handling

### Data and Configuration Directories

- **`ANIML_Allignments/`** - AnIML (Analytical Information Markup Language) ontology alignments
- **`AnIML Technique Definition Documents/`** - Technical documentation for AnIML techniques
- **`LLM_SSSOM_Output/`** - Output directory for LLM-generated SSSOM files
- **`OAEI_data/`** - Data from OAEI (Ontology Alignment Evaluation Initiative)
- **`LogMap/`** - Output/data from LogMap alignment tool
- **`sys_prompts/`** - System prompts for LLM configuration
- **`user_prompts/`** - User-defined prompts for alignment generation
- **`testOntologies/`** - Test ontology files for development and validation
- **`output/`** - Output directory for alignment review results

### Data Files

- **`animl_manual.owl`** - Manual AnIML ontology in OWL format
- **`skeleton_ontology_1.ttl`** - Skeleton ontology in Turtle format used as test/reference data
- **`api_key.txt`** - Configuration file for LLM API credentials (see setup below)

## Prerequisites

- Python 3.8+
- pip package manager

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DiegoCondeHerreros/Evol_Align.git
   cd Evol_Align
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Key dependencies include:
   - `openai` - OpenAI API client
   - `ollama` - Ollama LLM interface
   - `google-genai` - Google Gemini API client
   - `pydantic` - Data validation using Python type annotations
   - `rdflib` - RDF/OWL ontology handling

3. **Configure API credentials:**
   
   Create an `api_key.txt` file in the repository root with the following structure:
   ```json
   [
     {
       "OpenAI": {
         "API_KEY": "your_openai_api_key",
         "Models": {
           "gpt-4": ["temperature", "top_p", "max_tokens"],
           "gpt-3.5-turbo": ["temperature", "max_tokens"]
         }
       },
       "Gemini": {
         "API_KEY": "your_gemini_api_key",
         "Models": {
           "gemini-2.0-flash": ["temperature"],
           "gemini-1.5-pro": ["temperature"]
         }
       },
       "Ollama": {
         "Models": {
           "llama2": ["temperature", "top_k", "top_p"],
           "mistral": ["temperature"]
         }
       }
     }
   ]
   ```

   - Replace placeholder values with your actual API keys
   - For Ollama (local LLM), no API_KEY is required; the tool will automatically pull models
   - Supported parameters depend on each provider's API specifications

## Usage

### 1. Generating Alignments with LLMs

Use the LLM interface to generate ontology alignments:

```python
from llm_interface import LLM
from structured_outputs import SSSOMAlignmentStrictCore

# Initialize LLM
llm = LLM(
    model_family="OpenAI",  # or "Gemini", "Ollama"
    model="gpt-4",
    params={"temperature": 0.7, "max_tokens": 2000},
    context=None  # Optional: list of ontology files for context
)

# Create messages for alignment generation
messages = [
    {"role": "system", "content": "You are an ontology alignment expert."},
    {"role": "user", "content": "Generate alignments between these ontologies..."}
]

# Get structured response
response = llm.prompt(messages, SSSOMAlignmentStrictCore, context=None)
```

### 2. Reviewing Alignments Interactively

Review generated alignments and provide manual curation:

```bash
python alignement_review.py -a path/to/alignments.ttl
```

**Process:**
- Load existing SSSOM alignments in Turtle format
- Review each alignment one by one
- For each mapping, provide feedback:
  - **y** (Yes): Accept the alignment
  - **n** (No): Reject the alignment
  - **r** (Requires Refinement): Flag for further refinement
- Provide justification comments for your decisions
- Output file saved to `output/` directory with reviewer metadata

### 3. Working with Structured Outputs

Define and validate alignment data using Pydantic models:

```python
from structured_outputs import SSSOMAlignmentStrictCore, MappingRow, MappingPredicate, SemaPVJustification

# Create a mapping row
mapping = MappingRow(
    subject_id="http://example.org/ontology1/Class1",
    object_id="http://example.org/ontology2/ClassA",
    predicate_id=MappingPredicate.skos_exact_match,
    mapping_justification=SemaPVJustification.lexical_matching,
    confidence=0.95
)

# Create a complete alignment set
alignment_set = SSSOMAlignmentStrictCore(
    mapping_set_id="http://example.org/alignments/set1",
    license="http://creativecommons.org/licenses/by/4.0/",
    subject_source="http://example.org/ontology1",
    object_source="http://example.org/ontology2",
    subject_type="owl:Class",
    object_type="owl:Class",
    mappings=[mapping]
)
```

## SSSOM Standard

The Simple Standard for Sharing Ontology Mappings (SSSOM) is used throughout this project. For more information, visit: https://w3id.org/sssom/

### Supported Mapping Predicates
- `skos:exactMatch`
- `skos:closeMatch`
- `skos:broadMatch`
- `skos:narrowMatch`
- `skos:relatedMatch`
- `owl:sameAs`
- `owl:equivalentClass`
- `owl:equivalentProperty`
- `rdfs:subClassOf`
- `rdfs:subPropertyOf`

### Justification Types
- Manual mapping curation
- Logical reasoning
- Lexical matching
- Composite matching
- Semantic similarity matching
- And more (see `SemaPVJustification` enum)

## Data Formats

### Input Ontologies
- **OWL format** (.owl files)
- **Turtle/RDF format** (.ttl files)
- **RDF/XML format** (.rdf files)

### Output Alignments
- **SSSOM Turtle format** (.ttl) - RDF representation with SSSOM metadata
- **JSON/Pydantic format** - Structured Python objects

## LLM Provider Configuration

### OpenAI
- Requires valid OpenAI API key
- Supports structured output via response schema
- Recommended models: gpt-4, gpt-3.5-turbo

### Google Gemini
- Requires valid Google GenAI API key
- Supports file uploads for ontology context
- Recommended models: gemini-2.0-flash, gemini-1.5-pro

### Ollama (Local)
- No API key required
- Runs locally on your machine
- Automatically downloads models on first use
- Recommended models: llama2, mistral, neural-chat

## Project Resources

### Key Files
- Ontology examples: `animl_manual.owl`, `skeleton_ontology_1.ttl`
- Alignment samples: Various SSSOM files in `LLM_SSSOM_Output/` and `ANIML_Allignments/`
- Test data: `testOntologies/` directory

### External Data Sources
- OAEI benchmark data in `OAEI_data/`
- LogMap outputs in `LogMap/`

## Example Workflow

1. **Prepare ontologies** - Place your ontology files in `testOntologies/`
2. **Configure LLM** - Set up API keys in `api_key.txt`
3. **Generate alignments** - Use `llm_interface.py` to generate SSSOM mappings
4. **Review alignments** - Use `alignement_review.py` for manual curation
5. **Export results** - Save reviewed alignments to `output/`

## References

- SSSOM Standard: https://w3id.org/sssom/
- OWL Ontology Language: https://www.w3.org/OWL/
- RDF/Turtle Format: https://www.w3.org/TR/turtle/
- OAEI (Ontology Alignment Evaluation Initiative): http://oaei.ontologymatching.org/

## License

This project is developed as a collaboration between the Knowledge Engineering Group (KEG) and the Ontology Engineering Group (OEG).

## Contact

For more information about this research, please refer to the associated publications or contact the research teams at KEG and OEG.

## Contributing

Contributions are welcome! Please ensure code follows the existing structure and includes proper documentation.
