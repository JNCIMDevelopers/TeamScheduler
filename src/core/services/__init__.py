"""
Domain Services

This package contains core business services and domain logic:

- schedule_service.py: Main service for schedule generation and management
- eligibility_service.py: Service for determining person eligibility for roles
- eligibility_rules.py: Business rules that determine assignment eligibility
- worship_leader_selector.py: Algorithms for worship leader rotation and selection

These services orchestrate domain entities and implement complex business processes
that don't naturally belong to a single entity. They contain the core business
logic of the Team Scheduler application.

Key characteristics:
- Stateless services that coordinate domain entities
- Complex business logic and rule processing
- Independent of external frameworks and infrastructure
- Can be easily unit tested in isolation
- Implement business processes that span multiple entities
"""
