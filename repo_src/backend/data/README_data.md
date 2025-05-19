# Data Schemas

This directory contains Pydantic schemas for data validation, serialization, and documentation.

## Purpose

- **Data Validation**: Define expected data structures and constraints
- **API Documentation**: Schemas are used to generate OpenAPI/Swagger documentation
- **Request/Response Models**: Used by FastAPI for input validation and output serialization
- **Type Safety**: Provide clear typing information for development and tooling

## Guidelines

1. **Separate Request/Response Models**: Create distinct schemas for:
   - Input data (e.g., `ItemCreate`, `ItemUpdate`)
   - Output data (e.g., `Item`, `ItemWithDetails`)
   
2. **Field Validation**: Use Pydantic validators and constraints:
   ```python
   class ItemCreate(BaseModel):
       name: str = Field(..., min_length=1, max_length=100)
       description: Optional[str] = Field(None, max_length=1000)
   ```

3. **Schema Organization**: Group related schemas in modules:
   - `item_schemas.py` - Everything related to Items
   - `user_schemas.py` - Everything related to Users

## Integration with Database Models

Use the `from_orm` method or model_config to convert SQLAlchemy models to Pydantic schemas:

```python
from pydantic import BaseModel, ConfigDict

class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
```

This allows converting SQLAlchemy model instances to Pydantic objects with:
```python
item_db = db.query(models.Item).first()
item_schema = schemas.Item.model_validate(item_db)
```

## Examples

The database uses `Item` model from `database/models.py`. Corresponding Pydantic schemas might include:

1. `ItemBase` - Common attributes
2. `ItemCreate` - For creating items (without id, created_at, etc.)
3. `ItemUpdate` - For updating items (all fields optional)
4. `Item` - Full item representation including all fields 