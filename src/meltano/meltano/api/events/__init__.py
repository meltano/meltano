from __future__ import annotations

from meltano.core.project import Project

from .notification_events import NotificationEvents

notifications = NotificationEvents(Project.find())
