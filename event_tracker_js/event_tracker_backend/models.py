from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Attendee(Base):
    __tablename__ = "attendees"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    identifier = Column(String, unique=True, index=True)
    registered = Column(Boolean, default=False)
    lunch_collected = Column(Boolean, default=False)
    kit_collected = Column(Boolean, default=False)
    registration_time = Column(DateTime, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "identifier": self.identifier,
            "registered": self.registered,
            "lunch_collected": self.lunch_collected,
            "kit_collected": self.kit_collected,
            "registration_time": self.registration_time.isoformat() if self.registration_time else None
        }