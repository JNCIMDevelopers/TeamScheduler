"""
Application Layer

This package contains application services and data transfer objects (DTOs):

- models.py: Pydantic models for API request/response validation and serialization

This layer acts as a bridge between the API layer and the core domain layer.
It defines the application's public interface through DTOs and handles
data transformation between external representations and domain entities.

Following Clean Architecture principles, this layer depends only on the core layer
and provides contracts that outer layers (API, Infrastructure) can implement.
"""
