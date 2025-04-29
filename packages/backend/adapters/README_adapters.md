# Adapters

This directory contains adapters that handle side effects and interactions with external systems.

## What is an Adapter?

An adapter:
1. **Encapsulates** side effects (database, network, file I/O, etc.)
2. **Translates** between the domain model and external systems
3. **Isolates** the application from infrastructure details
4. **Provides** a clean interface for pipelines to use

## Structure

Adapters are organized by the external system they interact with:

- `database/`: Database interactions
- `http/`: HTTP clients for external APIs
- `messaging/`: Message broker interactions
- `storage/`: File storage interactions
- `cache/`: Caching mechanisms

## Example Adapter

```python
from typing import Optional
from ..data.models import User
from .database_connection import get_connection

def save_user(user: User) -> bool:
    """
    Save a user to the database.
    
    Args:
        user: The user model to save
        
    Returns:
        True if the save was successful, False otherwise
        
    Raises:
        DatabaseError: If there's an issue with the database connection
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (id, name, email, created_at, is_active) VALUES (%s, %s, %s, %s, %s)",
            (user.id, user.name, user.email, user.created_at, user.is_active)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise DatabaseError(f"Failed to save user: {str(e)}") from e
    finally:
        conn.close()

def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Retrieve a user from the database by ID.
    
    Args:
        user_id: The ID of the user to retrieve
        
    Returns:
        User model if found, None otherwise
        
    Raises:
        DatabaseError: If there's an issue with the database connection
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, created_at, is_active FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
            
        return User(
            id=row[0],
            name=row[1],
            email=row[2],
            created_at=row[3],
            is_active=row[4]
        )
    except Exception as e:
        raise DatabaseError(f"Failed to get user: {str(e)}") from e
    finally:
        conn.close()
```

## Adapter Contract

All adapters should:
1. Take domain models as input and return domain models as output
2. Handle infrastructure errors and translate them to domain errors
3. Encapsulate all side effects
4. Have clear documentation of their behavior
5. Be mockable for testing

## Testing

Adapters should be tested with:
1. Integration tests that verify interaction with the actual external system
2. Unit tests with mocks to verify error handling

## Design Differences

- Adapters are the only components allowed to have side effects
- Adapters are typically injected into pipelines, not directly imported
- Adapters translate between domain models and external system formats 