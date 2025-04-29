# Pipelines

This directory contains pipeline orchestrators that compose pure functions to implement features.

## What is a Pipeline?

A pipeline:
1. **Orchestrates** multiple pure functions to achieve a business goal
2. **Manages** the flow of data between functions
3. **Handles** errors and edge cases
4. **Delegates** side effects to adapters

## Structure

Pipelines are organized by feature or domain concept, with each pipeline in its own file.

## Example Pipeline

```python
from typing import Dict, Any, Optional
from ..functions.validation import validate_input
from ..functions.processing import process_data
from ..functions.formatting import format_result
from ..adapters.database import save_result
from ..data.models import InputData, ProcessedData, FormattedResult

def process_and_save_pipeline(input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Process input data and save the result to the database.
    
    Args:
        input_data: Raw input data as a dictionary
        
    Returns:
        Formatted result or None if validation fails
        
    Raises:
        DatabaseError: If there's an issue saving to the database
    """
    # Validation step
    try:
        validated_data = validate_input(InputData(**input_data))
    except ValueError as e:
        # Handle validation error
        return None
    
    # Processing step
    processed_data = process_data(validated_data)
    
    # Formatting step
    formatted_result = format_result(processed_data)
    
    # Side effect delegated to adapter
    save_result(formatted_result)
    
    return formatted_result.dict()
```

## Pipeline Contract

All pipelines should:
1. Have clear input and output types
2. Document exceptions that might be raised
3. Handle errors from the functions they compose
4. Delegate side effects to adapters
5. Have corresponding integration tests

## Testing

Pipelines should have integration tests that verify:
1. The happy path works end-to-end
2. Error cases are handled appropriately
3. Side effects are correctly delegated to adapters

## Documentation

Pipeline documentation is automatically summarized in the `registry/pipeline_context.md` file. When adding or updating a pipeline:

1. Create a README_[feature].md file in the pipeline's subdirectory
2. Include a clear title (h1) and description
3. Document the purpose, key functions, and example usage
4. Run `pnpm ctx:sync` to update the pipeline context

The pipeline context is used by AI tools to understand the high-level structure of the application.

## Design Differences

- Pipelines are the primary composition mechanism, not inheritance
- Error handling is centralized in the pipeline
- Side effects are clearly marked and delegated to adapters
- Pipelines are the API surface of the application 