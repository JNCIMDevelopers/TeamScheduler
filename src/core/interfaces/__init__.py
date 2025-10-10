"""
Domain Interfaces

This package defines abstract interfaces and contracts for the core domain:

- repositories.py: Repository interfaces for data persistence abstraction

These interfaces define contracts that outer layers must implement, following
the Dependency Inversion Principle. The core domain depends only on these
abstractions, not on concrete implementations.

Key principles:
- Abstract contracts independent of implementation details
- Enable testability through dependency injection
- Maintain separation between core business logic and external concerns
- Support multiple implementations (in-memory, database, external APIs, etc.)
"""
