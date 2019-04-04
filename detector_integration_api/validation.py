from enum import Enum


class IntegrationStatus(Enum):
    READY = "ready",
    RUNNING = "running",
    ERROR = "error",
    COMPONENT_NOT_RESPONDING = "component_not_responding"
