"""Routes module for API endpoints."""

from . import users
from . import items
from . import tasks
from . import item_types
from . import task_types
from . import maintenance_templates
from . import item_maintenance_plans

__all__ = ["users", "items", "tasks", "item_types", "task_types", "maintenance_templates", "item_maintenance_plans"]
