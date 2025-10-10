"""
Domain Entities

This package contains the core domain entities of the Team Scheduler application:

- person.py: Person entity with roles, availability, and assignment tracking
- event.py: Event entity representing scheduled services with role assignments
- role.py: Role enumeration defining all possible team positions
- preacher.py: Preacher entity for guest speakers and their schedules

These entities represent the fundamental business concepts and contain the core
business logic. They are independent of any external frameworks or technologies,
following Domain-Driven Design (DDD) principles.

Key characteristics:
- Pure business logic with no external dependencies
- Rich domain models with behavior, not just data containers  
- Encapsulate business rules and invariants
- Form the foundation of the entire application
"""
