import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import db, create_document, get_documents
from schemas import Category, Provider, ServiceRequest

app = FastAPI(title="Home Services Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Home Services Platform Backend Running"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# Seed minimal data if empty (categories, providers)
@app.post("/seed")
def seed_data():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    categories = [
        {"name": "Plumbing", "icon": "Wrench", "description": "Fix leaks, pipes, and fixtures"},
        {"name": "Electrical", "icon": "Zap", "description": "Wiring, fixtures, and repairs"},
        {"name": "Cleaning", "icon": "Broom", "description": "Home and office cleaning"},
        {"name": "Handyman", "icon": "Hammer", "description": "General repairs and tasks"},
        {"name": "HVAC", "icon": "Thermometer", "description": "Heating and AC services"},
    ]

    providers = [
        {"name": "AquaPro Plumbing", "category": "Plumbing", "city": "San Francisco", "rating": 4.9, "jobs_completed": 320, "phone": "(415) 555-0123", "bio": "24/7 emergency plumbing"},
        {"name": "Spark Electric Co.", "category": "Electrical", "city": "San Francisco", "rating": 4.7, "jobs_completed": 210, "phone": "(415) 555-0456", "bio": "Licensed electricians"},
        {"name": "Shine & Sparkle", "category": "Cleaning", "city": "Oakland", "rating": 4.8, "jobs_completed": 540, "phone": "(510) 555-0987", "bio": "Eco-friendly cleaning"},
        {"name": "Fix-It Handyman", "category": "Handyman", "city": "San Jose", "rating": 4.6, "jobs_completed": 150, "phone": "(408) 555-0234", "bio": "Small jobs, big quality"},
    ]

    col_c = db["category"]
    col_p = db["provider"]

    if col_c.count_documents({}) == 0:
        col_c.insert_many(categories)
    if col_p.count_documents({}) == 0:
        col_p.insert_many(providers)

    return {"status": "ok"}


@app.get("/categories", response_model=List[Category])
def list_categories():
    docs = get_documents("category")
    return [Category(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]


@app.get("/providers", response_model=List[Provider])
def list_providers(category: Optional[str] = None):
    flt = {"category": category} if category else {}
    docs = get_documents("provider", flt)
    return [Provider(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]


@app.post("/request", status_code=201)
def create_service_request(payload: ServiceRequest):
    req_id = create_document("servicerequest", payload)
    return {"id": req_id, "status": "created"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
