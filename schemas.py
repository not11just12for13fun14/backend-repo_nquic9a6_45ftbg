from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

# NOTE: Each model corresponds to a MongoDB collection named by its lowercase class name
# Example: class Provider -> collection "provider"

class Category(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None

class Service(BaseModel):
    title: str
    category: str
    price: Optional[float] = None
    description: Optional[str] = None
    provider_id: Optional[str] = None
    popularity: int = 0

class Provider(BaseModel):
    name: str
    category: str
    city: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    rating: float = 4.5
    services: Optional[List[Service]] = None

class ServiceRequest(BaseModel):
    customer_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: str
    description: str
    category: str
    provider_id: Optional[str] = None
    preferred_date: Optional[str] = None

class Review(BaseModel):
    provider_id: str
    customer_name: str
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
