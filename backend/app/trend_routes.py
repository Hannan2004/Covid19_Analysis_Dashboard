from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from .trend_analyzer import get_trend_analyzer

router = APIRouter(prefix="/trends", tags=["Trend Analysis"])

class TrendAnalysisResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    timestamp: str

@router.get("/global", response_model=TrendAnalysisResponse)
async def get_global_trends():
    """Get global COVID-19 trend analysis"""
    try:
        analyzer = get_trend_analyzer()
        result = analyzer.get_global_trends()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return TrendAnalysisResponse(
            status="success",
            data=result,
            timestamp=result["timestamp"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis error: {str(e)}")

@router.get("/country/{country_name}", response_model=TrendAnalysisResponse)
async def get_country_trends(country_name: str):
    """Get trend analysis for specific country"""
    try:
        analyzer = get_trend_analyzer()
        result = analyzer.analyze_country_trends(country_name)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return TrendAnalysisResponse(
            status="success",
            data=result,
            timestamp=result["timestamp"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Country trend analysis error: {str(e)}")

@router.get("/risk-assessment", response_model=TrendAnalysisResponse)
async def get_risk_assessment():
    """Get risk assessment for all countries"""
    try:
        analyzer = get_trend_analyzer()
        result = analyzer.get_risk_assessment()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return TrendAnalysisResponse(
            status="success",
            data=result,
            timestamp=result["timestamp"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk assessment error: {str(e)}")

@router.get("/health")
async def trend_health():
    """Check if trend analysis service is healthy"""
    try:
        analyzer = get_trend_analyzer()
        return {
            "status": "healthy",
            "message": "Trend analysis service is operational",
            "groq_status": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Trend service error: {str(e)}"
        }