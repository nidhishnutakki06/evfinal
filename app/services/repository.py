from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models.sqlalchemy_db import EVDefinition, StationDefinition, ScenarioProfile

class PersistenceRepository:
    """
    A clean persistence interface/service for SQLite data operations.
    Exposes failures clearly; does not silently mutate runtime state.
    """
    def __init__(self, db: Session):
        self.db = db
        
    def create_ev_definition(self, ev_data: dict) -> EVDefinition:
        ev = EVDefinition(**ev_data)
        self.db.add(ev)
        self.db.commit()
        self.db.refresh(ev)
        return ev
        
    def get_ev_definition(self, ev_id: str) -> Optional[EVDefinition]:
        return self.db.query(EVDefinition).filter(EVDefinition.id == ev_id).first()
        
    def get_all_ev_definitions(self) -> List[EVDefinition]:
        return self.db.query(EVDefinition).all()
        
    def update_ev_definition(self, ev_id: str, ev_data: dict) -> Optional[EVDefinition]:
        ev = self.get_ev_definition(ev_id)
        if ev:
            for key, value in ev_data.items():
                setattr(ev, key, value)
            self.db.commit()
            self.db.refresh(ev)
        return ev
        
    def create_station_definition(self, station_data: dict) -> StationDefinition:
        station = StationDefinition(**station_data)
        self.db.add(station)
        self.db.commit()
        self.db.refresh(station)
        return station
        
    def get_station_definition(self, station_id: str) -> Optional[StationDefinition]:
        return self.db.query(StationDefinition).filter(StationDefinition.station_id == station_id).first()
        
    def get_all_station_definitions(self) -> List[StationDefinition]:
        return self.db.query(StationDefinition).all()
        
    def create_scenario_profile(self, profile_data: dict) -> ScenarioProfile:
        profile = ScenarioProfile(**profile_data)
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
        
    def get_scenario_profile(self, profile_id: str) -> Optional[ScenarioProfile]:
        return self.db.query(ScenarioProfile).filter(ScenarioProfile.id == profile_id).first()
        
    def get_all_scenario_profiles(self) -> List[ScenarioProfile]:
        return self.db.query(ScenarioProfile).all()
