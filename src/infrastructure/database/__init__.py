"""
Database Infrastructure

This package contains data persistence implementations:

- repositories.py: Concrete repository implementations (currently in-memory)
- Sample data initialization and management

Current implementation uses in-memory storage with sample data for development
and testing. This design makes it easy to replace with actual database
implementations (SQLAlchemy, MongoDB, etc.) without changing any business logic.

Repository implementations:
- InMemoryPersonRepository: Person entity persistence
- InMemoryEventRepository: Event entity persistence  
- InMemoryPreacherRepository: Preacher entity persistence

Future database implementations can be added here while maintaining the same
interface contracts defined in src.core.interfaces.repositories.

Key characteristics:
- Implements repository interfaces from core layer
- Provides data persistence abstraction
- Currently uses in-memory storage with sample data
- Ready for database migration (PostgreSQL, MySQL, etc.)
- Maintains data consistency and integrity
"""
