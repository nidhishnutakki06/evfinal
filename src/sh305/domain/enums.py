from enum import Enum


class VehicleType(str, Enum):
    SUV = "SUV"
    SEDAN = "Sedan"
    HATCHBACK = "Hatchback"
    SCOOTER = "Scooter"
    BIKE = "Bike"


class StationStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    PAUSED = "PAUSED"
    COMPLETE = "COMPLETE"


class DeadlineStatus(str, Enum):
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK"
    UNABLE = "UNABLE"


class WeatherCondition(str, Enum):
    SUNNY = "SUNNY"
    CLOUDY = "CLOUDY"
    RAIN = "RAIN"


class TimeOfDay(str, Enum):
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    EVENING = "EVENING"
    NIGHT = "NIGHT"


class UserUrgency(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SafetyState(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class SimulationStatus(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
