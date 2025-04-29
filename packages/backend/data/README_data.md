# Data Models

This directory contains the immutable data models used throughout the application.

## Principles

1. **Immutability**: All data models are immutable to prevent unexpected side effects
2. **Validation**: Models validate data on creation using Pydantic
3. **Serialization**: Models can be easily serialized to/from JSON
4. **Documentation**: All models have clear docstrings and type hints

## Conventions

- Use Pydantic for all data models
- Define models in separate files based on domain concepts
- Add validators where necessary to enforce business rules
- Include JSON serialization/deserialization methods
- Test all models with edge cases

## Example

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class User(BaseModel):
    """
    Represents a user in the system.
    """
    id: str = Field(..., description="Unique identifier for the user")
    name: str = Field(..., description="Full name of the user")
    email: str = Field(..., description="Email address of the user")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    roles: List[str] = Field(default_factory=list)
    metadata: Optional[dict] = Field(default=None)
```

## Design Differences

- Models are isolated from database concerns (no ORM dependencies)
- Focus on domain modeling rather than persistence concerns
- Models are used consistently across all layers of the application 