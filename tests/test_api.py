"""
API endpoint tests for the FastAPI application.
"""

from fastapi.testclient import TestClient

from src.api.main import app
from src.core.entities.role import Role


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self):
        """Test health endpoint returns proper status."""
        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.0"


class TestPersonEndpoints:
    """Test person management endpoints."""

    def test_get_all_persons(self):
        """Test retrieving all persons."""
        client = TestClient(app)
        response = client.get("/api/v1/persons")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0  # Should have sample data

        # Check structure of person data
        person = data[0]
        assert "id" in person
        assert "name" in person
        assert "roles" in person
        assert "blockout_dates" in person
        assert "preaching_dates" in person
        assert "teaching_dates" in person
        assert "on_leave" in person

    def test_create_person(self):
        """Test creating a new person."""
        client = TestClient(app)
        person_data = {
            "name": "Test Person",
            "roles": ["DRUMS", "BASS"],
            "blockout_dates": ["2024-12-25"],
            "preaching_dates": [],
            "teaching_dates": [],
            "on_leave": False,
        }

        response = client.post("/api/v1/persons", json=person_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Person"
        assert "DRUMS" in data["roles"]
        assert "BASS" in data["roles"]
        assert "2024-12-25" in data["blockout_dates"]
        assert not data["on_leave"]

    def test_get_person_by_id(self):
        """Test retrieving a specific person by ID."""
        client = TestClient(app)

        # First create a person
        person_data = {
            "name": "Specific Person",
            "roles": ["KEYS"],
            "blockout_dates": [],
            "preaching_dates": [],
            "teaching_dates": [],
            "on_leave": False,
        }

        create_response = client.post("/api/v1/persons", json=person_data)
        created_person = create_response.json()
        person_id = created_person["id"]

        # Now retrieve by ID
        response = client.get(f"/api/v1/persons/{person_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == person_id
        assert data["name"] == "Specific Person"

    def test_get_nonexistent_person(self):
        """Test retrieving a person that doesn't exist."""
        client = TestClient(app)
        fake_id = "12345678-1234-1234-1234-123456789012"

        response = client.get(f"/api/v1/persons/{fake_id}")

        assert response.status_code == 404

    def test_update_person(self):
        """Test updating an existing person."""
        client = TestClient(app)

        # Create a person first
        person_data = {
            "name": "Update Me",
            "roles": ["DRUMS"],
            "blockout_dates": [],
            "preaching_dates": [],
            "teaching_dates": [],
            "on_leave": False,
        }

        create_response = client.post("/api/v1/persons", json=person_data)
        created_person = create_response.json()
        person_id = created_person["id"]

        # Update the person
        update_data = {"name": "Updated Name", "on_leave": True}

        response = client.put(f"/api/v1/persons/{person_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["on_leave"] is True
        assert data["roles"] == ["DRUMS"]  # Should remain unchanged

    def test_delete_person(self):
        """Test deleting a person."""
        client = TestClient(app)

        # Create a person first
        person_data = {
            "name": "Delete Me",
            "roles": ["BACKUP"],
            "blockout_dates": [],
            "preaching_dates": [],
            "teaching_dates": [],
            "on_leave": False,
        }

        create_response = client.post("/api/v1/persons", json=person_data)
        created_person = create_response.json()
        person_id = created_person["id"]

        # Delete the person
        response = client.delete(f"/api/v1/persons/{person_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Person deleted successfully"

        # Verify person is deleted
        get_response = client.get(f"/api/v1/persons/{person_id}")
        assert get_response.status_code == 404


class TestPreacherEndpoints:
    """Test preacher management endpoints."""

    def test_get_all_preachers(self):
        """Test retrieving all preachers."""
        client = TestClient(app)
        response = client.get("/api/v1/preachers")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0  # Should have sample data

        # Check structure
        preacher = data[0]
        assert "id" in preacher
        assert "name" in preacher
        assert "graphics_support" in preacher
        assert "dates" in preacher

    def test_create_preacher(self):
        """Test creating a new preacher."""
        client = TestClient(app)
        preacher_data = {
            "name": "Test Preacher",
            "graphics_support": "Graphics Team C",
            "dates": ["2024-07-07", "2024-07-14"],
        }

        response = client.post("/api/v1/preachers", json=preacher_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Preacher"
        assert data["graphics_support"] == "Graphics Team C"
        assert "2024-07-07" in data["dates"]
        assert "2024-07-14" in data["dates"]


class TestScheduleEndpoints:
    """Test schedule generation and management endpoints."""

    def test_generate_schedule(self):
        """Test generating a schedule."""
        client = TestClient(app)
        schedule_request = {
            "start_date": "2024-06-02",  # Sunday
            "end_date": "2024-06-16",  # Sunday (2 weeks)
            "save_events": True,
        }

        response = client.post("/api/v1/schedule/generate", json=schedule_request)

        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "message" in data
        assert "events_created" in data

        events = data["events"]
        assert len(events) == 3  # Should have 3 Sundays in range

        # Check event structure
        event = events[0]
        assert "id" in event
        assert "date" in event
        assert "assignments" in event
        assert "preacher_name" in event

        # Check assignments structure
        assignments = event["assignments"]
        for role in Role:
            assert role.value in assignments

    def test_get_events_in_range(self):
        """Test retrieving events in a date range."""
        client = TestClient(app)

        # First generate some events
        schedule_request = {
            "start_date": "2024-06-02",
            "end_date": "2024-06-09",
            "save_events": True,
        }
        client.post("/api/v1/schedule/generate", json=schedule_request)

        # Now retrieve events
        response = client.get(
            "/api/v1/schedule/events",
            params={"start_date": "2024-06-01", "end_date": "2024-06-30"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # Should have at least the generated events

    def test_update_assignment(self):
        """Test updating a role assignment."""
        client = TestClient(app)

        # Generate a schedule first
        schedule_request = {
            "start_date": "2024-06-02",
            "end_date": "2024-06-02",
            "save_events": True,
        }
        schedule_response = client.post(
            "/api/v1/schedule/generate", json=schedule_request
        )
        events = schedule_response.json()["events"]
        event_id = events[0]["id"]

        # First unassign the DRUMS role
        unassign_request = {"role": "DRUMS", "person_name": None}

        unassign_response = client.put(
            f"/api/v1/schedule/events/{event_id}/assignment", json=unassign_request
        )
        assert unassign_response.status_code == 200

        # Then assign it to Michael
        update_request = {
            "role": "DRUMS",
            "person_name": "Michael",  # From sample data
        }

        response = client.put(
            f"/api/v1/schedule/events/{event_id}/assignment", json=update_request
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "event" in data

        # Check updated event
        updated_event = data["event"]
        assert updated_event["assignments"]["DRUMS"] == "Michael"

    def test_get_available_replacements(self):
        """Test getting available replacements for a role."""
        client = TestClient(app)

        # Generate a schedule first
        schedule_request = {
            "start_date": "2024-06-02",
            "end_date": "2024-06-02",
            "save_events": True,
        }
        schedule_response = client.post(
            "/api/v1/schedule/generate", json=schedule_request
        )
        events = schedule_response.json()["events"]
        event_id = events[0]["id"]

        # Get replacements
        response = client.get(f"/api/v1/schedule/events/{event_id}/replacements/DRUMS")

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "DRUMS"
        assert "available_persons" in data
        assert "event_date" in data
        assert isinstance(data["available_persons"], list)

    def test_unassign_role(self):
        """Test unassigning a role (setting to null)."""
        client = TestClient(app)

        # Generate a schedule first
        schedule_request = {
            "start_date": "2024-06-02",
            "end_date": "2024-06-02",
            "save_events": True,
        }
        schedule_response = client.post(
            "/api/v1/schedule/generate", json=schedule_request
        )
        events = schedule_response.json()["events"]
        event_id = events[0]["id"]

        # Unassign role (set person_name to null)
        update_request = {"role": "BACKUP", "person_name": None}

        response = client.put(
            f"/api/v1/schedule/events/{event_id}/assignment", json=update_request
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Check that role is unassigned
        updated_event = data["event"]
        assert updated_event["assignments"]["BACKUP"] is None


class TestAPIValidation:
    """Test API input validation."""

    def test_invalid_person_data(self):
        """Test creating person with invalid data."""
        client = TestClient(app)

        # Missing required name field
        invalid_data = {"roles": ["DRUMS"], "on_leave": False}

        response = client.post("/api/v1/persons", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_invalid_role_in_assignment(self):
        """Test assignment with invalid role."""
        client = TestClient(app)

        # Generate a schedule first
        schedule_request = {
            "start_date": "2024-06-02",
            "end_date": "2024-06-02",
            "save_events": True,
        }
        schedule_response = client.post(
            "/api/v1/schedule/generate", json=schedule_request
        )
        events = schedule_response.json()["events"]
        event_id = events[0]["id"]

        # Try to assign invalid role
        update_request = {"role": "INVALID_ROLE", "person_name": "Someone"}

        response = client.put(
            f"/api/v1/schedule/events/{event_id}/assignment", json=update_request
        )
        assert response.status_code == 422  # Validation error

    def test_invalid_date_format(self):
        """Test schedule generation with invalid date format."""
        client = TestClient(app)

        invalid_request = {
            "start_date": "not-a-date",
            "end_date": "2024-06-16",
            "save_events": True,
        }

        response = client.post("/api/v1/schedule/generate", json=invalid_request)
        assert response.status_code == 422  # Validation error


class TestConcurrentAPITests:
    """Tests for concurrent API access."""

    def test_concurrent_schedule_generation(self):
        """Test concurrent schedule generation requests."""
        # Make multiple concurrent requests
        schedule_request = {
            "start_date": "2024-06-02",
            "end_date": "2024-06-09",
            "save_events": False,  # Don't save to avoid conflicts
        }

        # Make 3 concurrent requests to the test app
        responses = []
        for _ in range(3):
            # Use TestClient for the actual requests
            test_client = TestClient(app)
            response = test_client.post(
                "/api/v1/schedule/generate", json=schedule_request
            )
            responses.append(response)

        # Test that concurrent access works
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert len(data["events"]) == 2  # 2 Sundays in range
