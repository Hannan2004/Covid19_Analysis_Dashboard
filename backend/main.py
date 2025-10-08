from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import time
import os

# Import your modules - Updated paths for backend/ location
try:
    from app.kafka_consumer import start_consumer_thread
    from app.neo4j_client import driver
    from app.models import CountryResponse, HealthCheck, ErrorResponse
    from app.trend_routes import router as trend_router
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback for direct execution
    from app.kafka_consumer import start_consumer_thread
    from app.neo4j_client import driver
    from app.models import CountryResponse, HealthCheck, ErrorResponse
    from app.trend_routes import router as trend_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Waiting for Neo4j to be ready...")
    max_retries = 12
    retry_count = 0

    while retry_count < max_retries:
        try:
            if driver:
                with driver.session() as session:
                    result = session.run("RETURN 1 as test")
                    test_result = result.single()
                    if test_result:
                        print("✅ Neo4j connection verified")
                        break
        except Exception as e:
            print(f"🔄 Neo4j not ready yet (attempt {retry_count + 1}/{max_retries}): {e}")
            time.sleep(10)
            retry_count += 1
    
    if retry_count >= max_retries:
        print("❌ Neo4j failed to start after 2 minutes.")
        
    try:
        start_consumer_thread()
        print("✅ Consumer thread started successfully")
    except Exception as e:
        print(f"❌ Failed to start consumer thread: {e}")
    
    yield
    
    # Shutdown
    print("🛑 Application shutting down")

app = FastAPI(
    title="COVID-19 Analytics API", 
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trend_router)

@app.get("/")
def read_root():
    return {"message": "COVID-19 Analytics API is running.", "status": "healthy"}

@app.get("/health")
def health_check():
    try:
        # Test Neo4j connection
        neo4j_status = "disconnected"
        if driver:
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_result = result.single()
                if test_result:
                    neo4j_status = "connected"
        
        response_data = {
            "status": "healthy",
            "message": "COVID-19 Analytics API is running",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "neo4j": neo4j_status,
                "api": "running"
            }
        }
        
        return JSONResponse(content=response_data, status_code=200)
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return JSONResponse(
            content={
                "status": "error",
                "message": f"Health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "neo4j": "error",
                    "api": "running"  
                }
            },
            status_code=500
        )

@app.get("/countries")
def get_countries():
    try:
        if not driver:
            raise HTTPException(status_code=500, detail="Neo4j connection not available")
            
        with driver.session() as session:
            result = session.run("MATCH (c:Country) RETURN c.name AS country, c.confirmed AS confirmed, c.deaths AS deaths, c.recovered AS recovered ORDER BY c.confirmed DESC")
            return [r.data() for r in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/countries/{country_name}")
def get_country(country_name: str):
    try:
        if not driver:
            raise HTTPException(status_code=500, detail="Neo4j connection not available")
            
        with driver.session() as session:
            result = session.run(
                "MATCH (c:Country {name: $name}) RETURN c.name AS country, c.confirmed AS confirmed, c.deaths AS deaths, c.recovered AS recovered, c.last_updated AS last_updated",
                name=country_name
            )
            record = result.single()
            if not record:
                raise HTTPException(status_code=404, detail="Country not found")
            return record.data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats/global")
def get_global_stats():
    try:
        if not driver:
            raise HTTPException(status_code=500, detail="Neo4j connection not available")
            
        with driver.session() as session:
            result = session.run(
                "MATCH (c:Country) RETURN sum(c.confirmed) AS total_confirmed, sum(c.deaths) AS total_deaths, sum(c.recovered) AS total_recovered, count(c) AS total_countries"
            )
            data = result.single().data()
            return {
                "total_confirmed": data["total_confirmed"] or 0,
                "total_deaths": data["total_deaths"] or 0,
                "total_recovered": data["total_recovered"] or 0,
                "total_countries": data["total_countries"] or 0,
                "active_cases": (data["total_confirmed"] or 0) - (data["total_deaths"] or 0) - (data["total_recovered"] or 0)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats/top/{limit}")
def get_top_countries(limit: int = 10):
    try:
        if not driver:
            raise HTTPException(status_code=500, detail="Neo4j connection not available")
            
        with driver.session() as session:
            result = session.run(
                "MATCH (c:Country) RETURN c.name AS country, c.confirmed AS confirmed, c.deaths AS deaths, c.recovered AS recovered ORDER BY c.confirmed DESC LIMIT $limit",
                limit=limit
            )
            return [r.data() for r in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))