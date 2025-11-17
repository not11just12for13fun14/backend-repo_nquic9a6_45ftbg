"""
Database Schemas for Home Services Platform

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercase of the class name (e.g., ServiceRequest -> "servicerequest").
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List


class Category(BaseModel):
    name: str = Field(..., description="Category name, e.g., Plumbing")
    icon: Optional[str] = Field(None, description="Optional icon name for UI")
    description: Optional[str] = Field(None, description="Short description")


class Provider(BaseModel):
    name: str = Field(..., description="Provider or company name")
    category: str = Field(..., description="Category this provider serves")
    city: Optional[str] = Field(None, description="City of operation")
    rating: float = Field(4.8, ge=0, le=5, description="Average rating out of 5")
    jobs_completed: int = Field(0, ge=0, description="Number of completed jobs")
    phone: Optional[str] = Field(None, description="Contact phone")
    bio: Optional[str] = Field(None, description="Short bio or specialties")


class ServiceRequest(BaseModel):
    customer_name: str = Field(..., description="Your full name")
    email: EmailStr = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    address: str = Field(..., description="Service address")
    category: str = Field(..., description="Requested service category")
    provider_id: Optional[str] = Field(None, description="Chosen provider id (optional)")
    description: str = Field(..., description="Describe what you need")
    preferred_date: Optional[str] = Field(None, description="Preferred date (YYYY-MM-DD)")
    status: str = Field("pending", description="Request status: pending|scheduled|completed|cancelled")


# Example additional models (not used directly in the MVP but useful for future):
class Review(BaseModel):
    provider_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    customer_name: Optional[str] = None
