import os
import sys

# Add the root project directory to the python path so it can be run standalone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.session import engine, Base, SessionLocal
from app.models.sqlalchemy_db import EVDefinition, StationDefinition, ScenarioProfile
from app.core.config import settings

def init_db():
    print(f"Initializing database at: {settings.sqlite_url}")
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    
def seed_data():
    db = SessionLocal()
    try:
        # Seed EVs
        if not db.query(EVDefinition).first():
            ev1 = EVDefinition(
                id="EV-100", vehicle_type="Car", battery_capacity=50.0, 
                range=300.0, minimum_charging_rate=0.0, maximum_charging_rate=11.0
            )
            ev2 = EVDefinition(
                id="EV-101", vehicle_type="Van", battery_capacity=80.0, 
                range=400.0, minimum_charging_rate=0.0, maximum_charging_rate=22.0
            )
            db.add_all([ev1, ev2])
            
        # Seed Stations
        if not db.query(StationDefinition).first():
            st1 = StationDefinition(
                station_id="ST-1", capacity=22.0, 
                minimum_charging_rate=0.0, maximum_charging_rate=22.0
            )
            st2 = StationDefinition(
                station_id="ST-2", capacity=11.0, 
                minimum_charging_rate=0.0, maximum_charging_rate=11.0
            )
            db.add_all([st1, st2])
            
        # Seed Scenario
        if not db.query(ScenarioProfile).first():
            scenario = ScenarioProfile(
                id="SC-1", name="Baseline Scenario", description="A simple baseline scenario",
                scenario_data={
                    "building": {"total_demand_curve": [10.0, 12.0, 15.0]},
                    "weather": {"conditions": ["Sunny", "Cloudy", "Rainy"]}
                }
            )
            db.add(scenario)
            
        db.commit()
        print("Seed data inserted successfully.")
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    seed_data()
