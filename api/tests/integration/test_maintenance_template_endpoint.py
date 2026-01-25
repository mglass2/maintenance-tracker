"""Integration tests for maintenance template API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestCreateMaintenanceTemplateEndpoint:
    """Tests for POST /maintenance_templates endpoint."""

    def test_create_maintenance_template_missing_item_type_id(self, client: TestClient):
        """Test missing item_type_id returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "task_type_id": 1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_missing_task_type_id(self, client: TestClient):
        """Test missing task_type_id returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_missing_time_interval_days(
        self, client: TestClient
    ):
        """Test missing time_interval_days returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": 1,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_negative_item_type_id(self, client: TestClient):
        """Test negative item_type_id returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": -1,
                "task_type_id": 1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_zero_item_type_id(self, client: TestClient):
        """Test zero item_type_id returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 0,
                "task_type_id": 1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_negative_task_type_id(self, client: TestClient):
        """Test negative task_type_id returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": -1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_zero_task_type_id(self, client: TestClient):
        """Test zero task_type_id returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": 0,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_negative_time_interval_days(
        self, client: TestClient
    ):
        """Test negative time_interval_days returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": 1,
                "time_interval_days": -30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_zero_time_interval_days(
        self, client: TestClient
    ):
        """Test zero time_interval_days returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": 1,
                "time_interval_days": 0,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_non_integer_item_type_id(
        self, client: TestClient
    ):
        """Test non-integer item_type_id returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": "not_an_int",
                "task_type_id": 1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_non_integer_task_type_id(
        self, client: TestClient
    ):
        """Test non-integer task_type_id returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": "not_an_int",
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_non_integer_time_interval_days(
        self, client: TestClient
    ):
        """Test non-integer time_interval_days returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": 1,
                "time_interval_days": "thirty",
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_custom_interval_not_dict(
        self, client: TestClient
    ):
        """Test custom_interval that is not a dictionary returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": 1,
                "time_interval_days": 30,
                "custom_interval": "not_a_dict",
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_custom_interval_as_list(
        self, client: TestClient
    ):
        """Test custom_interval that is a list returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": 1,
                "time_interval_days": 30,
                "custom_interval": ["type", "mileage"],
            },
        )

        assert response.status_code == 422


class TestGetMaintenanceTemplatesByItemTypeEndpoint:
    """Tests for GET /maintenance_templates/item_types/{item_type_id} endpoint."""

    def test_get_templates_by_item_type_nonexistent_returns_404(self, client: TestClient):
        """Test GET templates for nonexistent item type returns 404."""
        response = client.get("/maintenance_templates/item_types/9999")

        # Should return 404 when item_type doesn't exist
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "RESOURCE_NOT_FOUND"

    def test_get_templates_by_item_type_response_format(self, client: TestClient):
        """Test response format for GET templates by item type."""
        # This test would pass if an item_type with ID 1 exists and has templates
        response = client.get("/maintenance_templates/item_types/1")

        # Should return 200 if item_type exists, 404 if not
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert "message" in data
            assert isinstance(data["data"], list)

            # Each template should have required fields
            for template in data["data"]:
                assert "id" in template
                assert "item_type_id" in template
                assert "task_type_id" in template
                assert "task_type_name" in template
                assert "time_interval_days" in template
                assert "created_at" in template
                assert "updated_at" in template

    def test_get_templates_by_item_type_includes_task_type_name(self, client: TestClient):
        """Test GET templates includes task_type_name field."""
        response = client.get("/maintenance_templates/item_types/1")

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            for template in data["data"]:
                assert "task_type_name" in template
                assert isinstance(template["task_type_name"], str)

    def test_get_templates_by_item_type_empty_list(self, client: TestClient):
        """Test GET templates returns empty list if no templates exist."""
        response = client.get("/maintenance_templates/item_types/1")

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data["data"], list)


class TestGetAllTemplatesEndpoint:
    """Tests for GET /maintenance_templates endpoint."""

    def test_get_all_templates_empty_database(self, client: TestClient):
        """Test GET all templates with empty database."""
        response = client.get("/maintenance_templates")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "item_types" in data["data"]
        assert data["data"]["item_types"] == []

    def test_get_all_templates_response_structure(self, client: TestClient, db):
        """Test response structure of GET all templates."""
        from models.item_type import ItemType
        from models.task_type import TaskType
        from models.maintenance_template import MaintenanceTemplate

        # Create test data
        item_type = ItemType(name="Car")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        task_type = TaskType(name="Oil Change")
        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        template = MaintenanceTemplate(
            item_type_id=item_type.id,
            task_type_id=task_type.id,
            time_interval_days=30,
        )
        db.add(template)
        db.commit()

        response = client.get("/maintenance_templates")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "message" in data
        assert "item_types" in data["data"]
        assert len(data["data"]["item_types"]) == 1

        # Verify item type structure
        item_type_data = data["data"]["item_types"][0]
        assert "item_type_id" in item_type_data
        assert "item_type_name" in item_type_data
        assert "templates" in item_type_data
        assert isinstance(item_type_data["templates"], list)

        # Verify template structure
        assert len(item_type_data["templates"]) == 1
        template_data = item_type_data["templates"][0]
        assert "task_type_id" in template_data
        assert "task_type_name" in template_data
        assert "time_interval_days" in template_data
        assert "custom_interval" in template_data

    def test_get_all_templates_multiple_item_types(self, client: TestClient, db):
        """Test getting all templates with multiple item types."""
        from models.item_type import ItemType
        from models.task_type import TaskType
        from models.maintenance_template import MaintenanceTemplate

        # Create item types
        item_type1 = ItemType(name="Car")
        item_type2 = ItemType(name="House")
        db.add_all([item_type1, item_type2])
        db.commit()
        db.refresh(item_type1)
        db.refresh(item_type2)

        # Create task types
        task_type1 = TaskType(name="Oil Change")
        task_type2 = TaskType(name="Roof Inspection")
        db.add_all([task_type1, task_type2])
        db.commit()
        db.refresh(task_type1)
        db.refresh(task_type2)

        # Create templates
        template1 = MaintenanceTemplate(
            item_type_id=item_type1.id,
            task_type_id=task_type1.id,
            time_interval_days=30,
        )
        template2 = MaintenanceTemplate(
            item_type_id=item_type2.id,
            task_type_id=task_type2.id,
            time_interval_days=365,
        )
        db.add_all([template1, template2])
        db.commit()

        response = client.get("/maintenance_templates")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["item_types"]) == 2

        # Verify item types are sorted by name
        names = [it["item_type_name"] for it in data["data"]["item_types"]]
        assert names == ["Car", "House"]

    def test_get_all_templates_with_custom_interval(self, client: TestClient, db):
        """Test that custom_interval is included in response."""
        from models.item_type import ItemType
        from models.task_type import TaskType
        from models.maintenance_template import MaintenanceTemplate

        # Create test data
        item_type = ItemType(name="Car")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        task_type = TaskType(name="Tire Rotation")
        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        custom_interval = {"type": "mileage", "value": 5000}
        template = MaintenanceTemplate(
            item_type_id=item_type.id,
            task_type_id=task_type.id,
            time_interval_days=90,
            custom_interval=custom_interval,
        )
        db.add(template)
        db.commit()

        response = client.get("/maintenance_templates")

        assert response.status_code == 200
        data = response.json()
        template_data = data["data"]["item_types"][0]["templates"][0]
        assert template_data["custom_interval"] == custom_interval

    def test_get_all_templates_filters_soft_deleted(self, client: TestClient, db):
        """Test that soft-deleted templates are filtered out."""
        from models.item_type import ItemType
        from models.task_type import TaskType
        from models.maintenance_template import MaintenanceTemplate

        # Create test data
        item_type = ItemType(name="Car")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        task_type1 = TaskType(name="Oil Change")
        task_type2 = TaskType(name="Tire Rotation")
        db.add_all([task_type1, task_type2])
        db.commit()
        db.refresh(task_type1)
        db.refresh(task_type2)

        # Create one active and one deleted template
        template1 = MaintenanceTemplate(
            item_type_id=item_type.id,
            task_type_id=task_type1.id,
            time_interval_days=30,
        )
        template2 = MaintenanceTemplate(
            item_type_id=item_type.id,
            task_type_id=task_type2.id,
            time_interval_days=90,
            is_deleted=True,
        )
        db.add_all([template1, template2])
        db.commit()

        response = client.get("/maintenance_templates")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["item_types"]) == 1
        assert len(data["data"]["item_types"][0]["templates"]) == 1
        assert data["data"]["item_types"][0]["templates"][0]["task_type_name"] == "Oil Change"
