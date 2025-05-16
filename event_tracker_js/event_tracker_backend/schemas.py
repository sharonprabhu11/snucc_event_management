from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AttendeeBase(BaseModel):
    name: str
    email: str
    phone: str
    role: str
    

class AttendeeCreate(AttendeeBase):
    pass

class AttendeeResponse(AttendeeBase):
    id: int
    identifier: str
    registered: bool
    lunch_collected: bool
    kit_collected: bool
    registration_time: Optional[datetime] = None

    class Config:
        orm_mode = True

class AttendeeUpdate(BaseModel):
    registered: Optional[bool] = None
    lunch_collected: Optional[bool] = None
    kit_collected: Optional[bool] = None

class AttendeeList(BaseModel):
    attendees: List[AttendeeResponse]

class StatsResponse(BaseModel):
    total: int
    registered: int
    lunch_collected: int
    kit_collected: int