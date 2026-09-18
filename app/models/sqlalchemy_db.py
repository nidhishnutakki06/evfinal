from sqlalchemy import Column, String, Float, CheckConstraint, JSON
from app.db.session import Base

class EVDefinition(Base):
    """
    Persisted configuration for reusable EV profiles.
    Does NOT store live runtime state like current SoC, current rate, etc.
    """
    __tablename__ = "ev_definitions"
    
    id = Column(String, primary_key=True, index=True)
    vehicle_type = Column(String, nullable=False)
    battery_capacity = Column(Float, nullable=False)
    range = Column(Float, nullable=False, default=0.0)
    minimum_charging_rate = Column(Float, nullable=False, default=0.0)
    maximum_charging_rate = Column(Float, nullable=False)
    
    __table_args__ = (
        CheckConstraint('battery_capacity > 0', name='check_battery_capacity_positive'),
        CheckConstraint('range >= 0', name='check_range_non_negative'),
        CheckConstraint('minimum_charging_rate >= 0', name='check_min_rate_non_negative'),
        CheckConstraint('maximum_charging_rate >= minimum_charging_rate', name='check_max_ge_min_rate'),
    )

class StationDefinition(Base):
    """
    Persisted configuration for physical charging stations.
    Does NOT store runtime state like occupancy or connected EV.
    """
    __tablename__ = "station_definitions"
    
    station_id = Column(String, primary_key=True, index=True)
    capacity = Column(Float, nullable=False)
    minimum_charging_rate = Column(Float, nullable=False, default=0.0)
    maximum_charging_rate = Column(Float, nullable=False)
    
    __table_args__ = (
        CheckConstraint('capacity > 0', name='check_station_capacity_positive'),
        CheckConstraint('minimum_charging_rate >= 0', name='check_station_min_rate_non_negative'),
        CheckConstraint('maximum_charging_rate >= minimum_charging_rate', name='check_station_max_ge_min_rate'),
    )

class ScenarioProfile(Base):
    """
    Persisted configuration for reusable scenario data.
    JSON 'scenario_data' structure should contain building and weather profiles:
    {
       "building_profile": {"ac": [...], "lights": [...], ...},
       "weather_profile": {"conditions": [...], ...}
    }
    """
    __tablename__ = "scenario_profiles"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    scenario_data = Column(JSON, nullable=False)
