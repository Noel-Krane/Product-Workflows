"""
Cost tracking and budget management API routes.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db.models import db_manager, CostTracking, ResearchRun, CostTrackingResponse
from src.observability.tracker import CostTracker, BudgetStatus, BudgetConfig
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/costs", tags=["costs"])

# Request/Response models
class BudgetConfigRequest(BaseModel):
    monthly_hard_cap: Optional[float] = None
    monthly_soft_cap: Optional[float] = None
    per_run_soft_cap: Optional[float] = None
    per_run_hard_cap: Optional[float] = None
    daily_soft_cap: Optional[float] = None

class CostBreakdownResponse(BaseModel):
    summary: Dict[str, Any]
    by_model: List[Dict[str, Any]]
    by_call_type: List[Dict[str, Any]]
    daily_usage: List[Dict[str, Any]]

class BudgetStatusResponse(BaseModel):
    monthly_usage: float
    monthly_limit: float
    monthly_remaining: float
    monthly_percentage: float
    daily_usage: float
    daily_limit: float
    current_run_cost: float
    run_limit: float
    can_continue: bool
    warnings: List[str]
    recommendations: List[str]

# Dependency to get database session
def get_db():
    with db_manager.get_session() as session:
        yield session

# Global cost tracker instance
cost_tracker = CostTracker()

@router.get("/status", response_model=BudgetStatusResponse)
async def get_budget_status():
    """
    Get current budget status and usage statistics.
    """
    status = await cost_tracker.get_budget_status()
    
    return BudgetStatusResponse(
        monthly_usage=status.monthly_usage,
        monthly_limit=status.monthly_limit,
        monthly_remaining=status.monthly_remaining,
        monthly_percentage=status.monthly_percentage,
        daily_usage=status.daily_usage,
        daily_limit=status.daily_limit,
        current_run_cost=status.current_run_cost,
        run_limit=status.run_limit,
        can_continue=status.can_continue,
        warnings=status.warnings,
        recommendations=status.recommendations
    )

@router.get("/breakdown", response_model=CostBreakdownResponse)
async def get_cost_breakdown(days: int = Query(30, ge=1, le=365)):
    """
    Get detailed cost breakdown for analysis.
    
    Args:
        days: Number of days to include in breakdown (1-365)
    """
    breakdown = await cost_tracker.get_cost_breakdown(days=days)
    
    return CostBreakdownResponse(
        summary=breakdown["summary"],
        by_model=breakdown["by_model"],
        by_call_type=breakdown["by_call_type"],
        daily_usage=breakdown["daily_usage"]
    )

@router.get("/tracking", response_model=List[CostTrackingResponse])
async def get_cost_tracking(
    run_id: Optional[str] = None,
    model: Optional[str] = None,
    call_type: Optional[str] = None,
    days: int = Query(7, ge=1, le=365),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get detailed cost tracking entries with optional filtering.
    
    Args:
        run_id: Filter by specific run ID
        model: Filter by model name
        call_type: Filter by call type
        days: Number of days to look back
        limit: Maximum number of entries to return
    """
    # Calculate date threshold
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # Build query
    query = db.query(CostTracking).filter(CostTracking.timestamp >= since_date)
    
    if run_id:
        query = query.filter(CostTracking.run_id == run_id)
    
    if model:
        query = query.filter(CostTracking.model_name.ilike(f"%{model}%"))
    
    if call_type:
        query = query.filter(CostTracking.call_type == call_type)
    
    # Order by timestamp descending and limit
    cost_entries = query.order_by(CostTracking.timestamp.desc()).limit(limit).all()
    
    return [CostTrackingResponse.from_orm(entry) for entry in cost_entries]

@router.get("/run/{run_id}")
async def get_run_costs(run_id: str, db: Session = Depends(get_db)):
    """
    Get cost breakdown for a specific research run.
    """
    # Check if run exists
    run = db.query(ResearchRun).filter_by(id=run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")
    
    # Get cost entries for this run
    cost_entries = db.query(CostTracking).filter_by(run_id=run_id).all()
    
    if not cost_entries:
        return {
            "run_id": run_id,
            "total_cost": 0.0,
            "total_tokens": 0,
            "api_calls": 0,
            "by_model": [],
            "by_call_type": [],
            "timeline": []
        }
    
    # Calculate totals
    total_cost = sum(entry.cost for entry in cost_entries)
    total_tokens = sum(entry.total_tokens for entry in cost_entries)
    api_calls = len(cost_entries)
    
    # Group by model
    by_model = {}
    for entry in cost_entries:
        model = entry.model_name
        if model not in by_model:
            by_model[model] = {
                "model": model,
                "cost": 0.0,
                "tokens": 0,
                "calls": 0
            }
        by_model[model]["cost"] += entry.cost
        by_model[model]["tokens"] += entry.total_tokens
        by_model[model]["calls"] += 1
    
    # Group by call type
    by_call_type = {}
    for entry in cost_entries:
        call_type = entry.call_type
        if call_type not in by_call_type:
            by_call_type[call_type] = {
                "call_type": call_type,
                "cost": 0.0,
                "tokens": 0,
                "calls": 0
            }
        by_call_type[call_type]["cost"] += entry.cost
        by_call_type[call_type]["tokens"] += entry.total_tokens
        by_call_type[call_type]["calls"] += 1
    
    # Create timeline
    timeline = [
        {
            "timestamp": entry.timestamp.isoformat(),
            "cost": entry.cost,
            "model": entry.model_name,
            "call_type": entry.call_type,
            "tokens": entry.total_tokens
        }
        for entry in sorted(cost_entries, key=lambda x: x.timestamp)
    ]
    
    return {
        "run_id": run_id,
        "total_cost": total_cost,
        "total_tokens": total_tokens,
        "api_calls": api_calls,
        "by_model": list(by_model.values()),
        "by_call_type": list(by_call_type.values()),
        "timeline": timeline
    }

@router.post("/budget")
async def update_budget_config(config: BudgetConfigRequest):
    """
    Update budget configuration limits.
    """
    try:
        # Get current budget
        current_budget = cost_tracker.budget
        
        # Update only provided fields
        new_budget = BudgetConfig(
            monthly_hard_cap=config.monthly_hard_cap or current_budget.monthly_hard_cap,
            monthly_soft_cap=config.monthly_soft_cap or current_budget.monthly_soft_cap,
            per_run_soft_cap=config.per_run_soft_cap or current_budget.per_run_soft_cap,
            per_run_hard_cap=config.per_run_hard_cap or current_budget.per_run_hard_cap,
            daily_soft_cap=config.daily_soft_cap or current_budget.daily_soft_cap
        )
        
        # Validate budget configuration
        if new_budget.monthly_soft_cap > new_budget.monthly_hard_cap:
            raise HTTPException(
                status_code=400,
                detail="Monthly soft cap cannot exceed hard cap"
            )
        
        if new_budget.per_run_soft_cap > new_budget.per_run_hard_cap:
            raise HTTPException(
                status_code=400,
                detail="Per-run soft cap cannot exceed hard cap"
            )
        
        # Update budget
        await cost_tracker.update_budget(new_budget)
        
        logger.info("Budget configuration updated", 
                   monthly_hard_cap=new_budget.monthly_hard_cap,
                   per_run_hard_cap=new_budget.per_run_hard_cap)
        
        return {
            "message": "Budget configuration updated successfully",
            "budget": {
                "monthly_hard_cap": new_budget.monthly_hard_cap,
                "monthly_soft_cap": new_budget.monthly_soft_cap,
                "per_run_soft_cap": new_budget.per_run_soft_cap,
                "per_run_hard_cap": new_budget.per_run_hard_cap,
                "daily_soft_cap": new_budget.daily_soft_cap
            }
        }
        
    except Exception as e:
        logger.error("Failed to update budget configuration", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_model_costs():
    """
    Get current model pricing information.
    """
    from src.api.openrouter_client import OpenRouterClient
    
    pricing = OpenRouterClient.MODEL_PRICING
    models = OpenRouterClient.MODELS
    
    model_info = []
    for model_key, model_name in models.items():
        price_info = pricing.get(model_name, {"input": 0.0, "output": 0.0})
        model_info.append({
            "model_key": model_key,
            "model_name": model_name,
            "input_cost_per_1m_tokens": price_info["input"],
            "output_cost_per_1m_tokens": price_info["output"],
            "description": {
                "primary": "High-quality analysis and reasoning",
                "fallback": "Cost-effective backup option",
                "web_search": "Online research and fact-checking",
                "cost_effective": "Budget-friendly for simple tasks",
                "free": "No-cost option for testing"
            }.get(model_key, "General purpose model")
        })
    
    return {
        "models": model_info,
        "pricing_note": "Costs are per 1 million tokens. Actual costs depend on prompt and response length."
    }

@router.get("/alerts")
async def get_budget_alerts():
    """
    Get current budget alerts and recommendations.
    """
    status = await cost_tracker.get_budget_status()
    
    alerts = []
    
    # Generate alerts based on usage thresholds
    if status.monthly_percentage > 90:
        alerts.append({
            "type": "critical",
            "message": f"Monthly budget at {status.monthly_percentage:.1f}% capacity",
            "action": "Stop research runs until next month"
        })
    elif status.monthly_percentage > 75:
        alerts.append({
            "type": "warning", 
            "message": f"Monthly budget at {status.monthly_percentage:.1f}% capacity",
            "action": "Monitor usage carefully"
        })
    
    if status.current_run_cost > status.run_limit * 0.8:
        alerts.append({
            "type": "warning",
            "message": f"Current run approaching cost limit: ${status.current_run_cost:.2f}",
            "action": "Consider stopping current run"
        })
    
    if status.daily_usage > status.daily_limit:
        alerts.append({
            "type": "info",
            "message": f"Daily usage exceeded: ${status.daily_usage:.2f}",
            "action": "Consider reducing research activity today"
        })
    
    return {
        "alerts": alerts,
        "warnings": status.warnings,
        "recommendations": status.recommendations,
        "can_continue": status.can_continue
    }