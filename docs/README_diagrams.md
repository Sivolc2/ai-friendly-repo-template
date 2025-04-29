# Function and Pipeline Diagrams

This directory contains automatically generated diagrams that visualize:

1. **Function Overview**: All functions from the `functions/` directory grouped by module
2. **Pipeline Diagrams**: Individual pipeline functions showing their dependencies and relationships to other functions

## Generating Diagrams

Diagrams are generated using the `generate_diagrams.py` script. You can run it with:

```bash
# Using npm/pnpm script
pnpm diagrams:generate

# Or directly
python repo_src/scripts/generate_diagrams.py
```

## Prerequisites

The diagram generator requires:

1. Python's `graphviz` package:
   ```bash
   pip install graphviz
   ```

2. Graphviz system binaries:
   - macOS: `brew install graphviz`
   - Linux: `apt-get install graphviz`
   - Windows: See https://graphviz.org/download/

## Diagram Types

### Function Overview

The function overview diagram (`function_overview.svg`) provides a high-level view of all functions in the codebase, grouped by module. This helps developers understand the overall structure of the application's functional core.

### Pipeline Diagrams

Each pipeline function gets its own diagram (`pipelines/{pipeline_name}.svg`) showing:

- The pipeline function (in green)
- Functions it directly calls (in blue for regular functions, yellow for other pipeline functions)
- Relationships between functions (shown with arrows)

## Documentation

Along with each pipeline diagram, the generator creates detailed Markdown documentation in the `docs/pipelines/` directory with:

- Function descriptions
- Parameters
- Return values
- Example usage

## Integrating into Development Workflow

For best results:

1. Run `pnpm diagrams:generate` after implementing significant changes to functions or pipelines
2. Commit the generated diagrams to version control for reference
3. Review diagrams during code reviews to ensure proper function composition and prevent circular dependencies 