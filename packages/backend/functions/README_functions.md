# Pure Functions

This directory contains pure functions that implement the core business logic of the application.

## What is a Pure Function?

A pure function has the following characteristics:
1. **Deterministic**: Given the same input, it always produces the same output
2. **No Side Effects**: It doesn't modify external state (no database calls, network requests, etc.)
3. **No Mutations**: It doesn't modify its input arguments
4. **Explicit Dependencies**: All dependencies are passed as arguments

## Structure

Functions are organized into subdirectories based on domain concepts or features.

## How to Write a Pure Function

### Template

```python
def function_name(arg1: Type1, arg2: Type2) -> ReturnType:
    """
    Brief description of what the function does.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of the return value
        
    Raises:
        ExceptionType: Description of when the exception is raised
    """
    # Implementation
    result = compute_something(arg1, arg2)
    return result
```

### Checklist

- [ ] Function has a clear, descriptive name
- [ ] All parameters have type annotations
- [ ] Return type is specified
- [ ] Comprehensive docstring is included
- [ ] No external dependencies (database, network, etc.)
- [ ] No global state modifications
- [ ] No input argument mutations
- [ ] Unit tests cover normal case, edge cases, and error cases

## Testing

All functions must have corresponding tests in the `tests/` directory. Tests should cover:

1. Normal operation
2. Edge cases
3. Error cases

## Design Differences

- Functions focus on business logic without infrastructure concerns
- Functions are composed in pipelines rather than calling each other directly
- Error handling is explicit and predictable 