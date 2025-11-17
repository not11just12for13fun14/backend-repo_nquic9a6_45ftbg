from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from database import db, create_document, get_documents
from schemas import Category, Provider, ServiceRequest, Review, Service
import os

app = FastAPI(title="Home Services API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Home Services API is running"}

@app.get("/test")
async def test():
    try:
        # Try a simple list_collections call to validate connection
        collections = await db.list_collection_names()
        return {
            "backend": "ok",
            "database": "ok",
            "database_url": os.getenv("DATABASE_URL", "mongodb://unknown"),
            "database_name": os.getenv("DATABASE_NAME", "unknown"),
            "connection_status": "connected",
            "collections": collections,
        }
    except Exception as e:
        return {
            "backend": "ok",
            "database": "error",
            "error": str(e),
        }

# Seed sample data
@app.post("/seed")
async def seed():
    sample_categories = [
        Category(name="Plumbing", description="Fix leaks, install fixtures", icon="🚰"),
        Category(name="Electrical", description="Wiring, lighting, panels", icon="💡"),
        Category(name="Cleaning", description="Home & office cleaning", icon="🧼"),
        Category(name="Painting", description="Interior & exterior", icon="🎨"),
        Category(name="Moving", description="Pack & move", icon="📦"),
    ]

    sample_providers = [
        Provider(name="Spark Electric Co.", category="Electrical", city="Seattle", bio="Certified electricians for residential & commercial.", rating=4.8),
        Provider(name="BlueWave Plumbing", category="Plumbing", city="Portland", bio="24/7 emergency plumbing services.", rating=4.7),
        Provider(name="ProClean Team", category="Cleaning", city="San Francisco", bio="Eco-friendly cleaning solutions.", rating=4.6),
        Provider(name="ColorCraft Painters", category="Painting", city="Austin", bio="Quality finishes that last.", rating=4.9),
        Provider(name="Swift Movers", category="Moving", city="Denver", bio="Stress-free moves, local & long distance.", rating=4.5),
    ]

    for c in sample_categories:
        await create_document("category", c.model_dump())

    for p in sample_providers:
        await create_document("provider", p.model_dump())

    # Add example services for top-selling section
    services = [
        Service(title="Outlet Installation", category="Electrical", price=120, description="Install a new outlet", popularity=42),
        Service(title="Faucet Replacement", category="Plumbing", price=90, description="Replace a faucet", popularity=55),
        Service(title="Deep Cleaning", category="Cleaning", price=200, description="Whole-home deep clean", popularity=68),
        Service(title="Room Painting", category="Painting", price=350, description="Paint a standard room", popularity=40),
    ]
    for s in services:
        await create_document("service", s.model_dump())

    return {"status": "seeded"}

@app.get("/categories")
async def list_categories():
    return await get_documents("category", {}, limit=100)

@app.get("/providers")
async def list_providers(category: Optional[str] = Query(None), top: Optional[int] = Query(None)):
    filt = {"category": category} if category else {}
    providers = await get_documents("provider", filt, limit=100)
    if top:
        # sort by rating desc
        providers = sorted(providers, key=lambda x: x.get("rating", 0), reverse=True)[:top]
    return providers

@app.get("/services")
async def list_services(category: Optional[str] = Query(None), top: Optional[int] = Query(None)):
    filt = {"category": category} if category else {}
    items = await get_documents("service", filt, limit=100)
    if top:
        items = sorted(items, key=lambda x: x.get("popularity", 0), reverse=True)[:top]
    return items

class RequestResponse(BaseModel):
    id: str
    status: str

@app.post("/request", response_model=RequestResponse)
async def create_request(req: ServiceRequest):
    doc = await create_document("servicerequest", req.model_dump())
    return {"id": str(doc.get("_id")), "status": "received"}

@app.get("/provider/{provider_id}")
async def provider_detail(provider_id: str):
    # naive lookup by name or id
    results = await get_documents("provider", {"$or": [{"_id": provider_id}, {"name": provider_id}]}, limit=1)
    if not results:
        # fallback: try name equality
        results = await get_documents("provider", {"name": provider_id}, limit=1)
    if not results:
        raise HTTPException(status_code=404, detail="Provider not found")

    provider = results[0]
    reviews = await get_documents("review", {"provider_id": str(provider.get("_id", provider.get("name")))}, limit=50)
    services = await get_documents("service", {"provider_id": str(provider.get("_id", provider.get("name")))}, limit=100)
    provider["reviews"] = reviews
    provider["services"] = services
    return provider

@app.post("/review")
async def add_review(review: Review):
    return await create_document("review", review.model_dump())
