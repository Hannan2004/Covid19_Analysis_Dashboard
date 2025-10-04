from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CountryData(BaseModel):
    """Model for COVID-19 country data"""
    country: str
    cases: int
    deaths: int
    recovered: int
    active: Optional[int] = None
    critical: Optional[int] = None
    population: Optional[int] = None
    timestamp: Optional[datetime] = None

class CountryResponse(BaseModel):
    """Response model for country data"""
    country: str
    confirmed: int
    deaths: int
    recovered: int
    last_updated: Optional[str] = None

class HealthCheck(BaseModel):
    """Health check response model"""
    status: str
    message: str
    timestamp: datetime

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime