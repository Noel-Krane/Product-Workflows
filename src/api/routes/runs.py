"""
Research run management API routes.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from src.db.models import (
    db_manager, ResearchRun, Agent, FrameworkResult, ActivityLog,
    ResearchRunResponse, FrameworkResultResponse, AgentResponse
)
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/runs", tags=["runs"])

# Response models
class RunStatisticsResponse(BaseModel):
    total_runs: int
    successful_runs: int
    failed_runs: int
    pending_runs: int
    running_runs: int
    avg_duration_minutes: float
    avg_cost_per_run: float
    total_cost: float
    success_rate: float

class RunDetailsResponse(BaseModel):
    run: ResearchRunResponse
    agent: AgentResponse
    frameworks: List[FrameworkResultResponse]
    activity_logs: List[Dict[str, Any]]
    cost_summary: Dict[str, Any]

class ActivityLogResponse(BaseModel):
    id: int
    run_id: Optional[str]
    level: str
    message: str
    component: Optional[str]
    action: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Dependency to get database session
def get_db():
    with db_manager.get_session() as session:
        yield session

@router.get("/statistics", response_model=RunStatisticsResponse)
async def get_run_statistics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get statistics about research runs over the specified time period.
    
    Args:
        days: Number of days to include in statistics (1-365)
    """
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # Basic counts
    total_runs = db.query(ResearchRun).filter(ResearchRun.created_at >= since_date).count()
    successful_runs = db.query(ResearchRun).filter(
        ResearchRun.created_at >= since_date,
        ResearchRun.status == "completed"
    ).count()
    failed_runs = db.query(ResearchRun).filter(
        ResearchRun.created_at >= since_date,
        ResearchRun.status == "failed"
    ).count()
    pending_runs = db.query(ResearchRun).filter(
        ResearchRun.created_at >= since_date,
        ResearchRun.status == "pending"
    ).count()
    running_runs = db.query(ResearchRun).filter(
        ResearchRun.created_at >= since_date,
        ResearchRun.status == "running"
    ).count()
    
    # Duration and cost statistics
    completed_runs = db.query(ResearchRun).filter(
        ResearchRun.created_at >= since_date,
        ResearchRun.status == "completed",
        ResearchRun.duration_seconds.isnot(None)
    ).all()
    
    avg_duration_minutes = 0.0
    avg_cost_per_run = 0.0
    total_cost = 0.0
    
    if completed_runs:
        total_duration = sum(run.duration_seconds or 0 for run in completed_runs)
        avg_duration_minutes = (total_duration / len(completed_runs)) / 60  # Convert to minutes
        
        total_cost = sum(run.total_cost or 0 for run in completed_runs)
        avg_cost_per_run = total_cost / len(completed_runs)
    
    success_rate = successful_runs / total_runs if total_runs > 0 else 0.0
    
    return RunStatisticsResponse(
        total_runs=total_runs,
        successful_runs=successful_runs,
        failed_runs=failed_runs,
        pending_runs=pending_runs,
        running_runs=running_runs,
        avg_duration_minutes=avg_duration_minutes,
        avg_cost_per_run=avg_cost_per_run,
        total_cost=total_cost,
        success_rate=success_rate
    )

@router.get("/{run_id}/details", response_model=RunDetailsResponse)
async def get_run_details(run_id: str, db: Session = Depends(get_db)):
    """
    Get comprehensive details for a specific research run.
    """
    # Get the run
    run = db.query(ResearchRun).filter_by(id=run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")
    
    # Get the agent
    agent = db.query(Agent).filter_by(id=run.agent_id).first()
    if not agent:
        raise HTTPException(status_code=500, detail="Associated agent not found")
    
    # Get framework results
    framework_results = db.query(FrameworkResult).filter_by(run_id=run_id).all()
    
    # Get activity logs
    activity_logs_raw = db.query(ActivityLog).filter_by(run_id=run_id).order_by(ActivityLog.timestamp).all()
    activity_logs = [
        {
            "id": log.id,
            "level": log.level,
            "message": log.message,
            "component": log.component,
            "action": log.action,
            "timestamp": log.timestamp,
            "details": log.details
        }
        for log in activity_logs_raw
    ]
    
    # Get cost summary from cost tracking
    from src.api.routes.costs import get_run_costs
    try:
        cost_summary = await get_run_costs(run_id, db)
    except:
        cost_summary = {"total_cost": run.total_cost or 0.0}
    
    return RunDetailsResponse(
        run=ResearchRunResponse.from_orm(run),
        agent=AgentResponse.from_orm(agent),
        frameworks=[FrameworkResultResponse.from_orm(result) for result in framework_results],
        activity_logs=activity_logs,
        cost_summary=cost_summary
    )

@router.get("/{run_id}/frameworks/{framework_type}")
async def get_framework_results(
    run_id: str, 
    framework_type: str, 
    db: Session = Depends(get_db)
):
    """
    Get detailed results for a specific framework analysis.
    
    Args:
        run_id: Research run ID
        framework_type: Framework type (porters, pestel, swot, ansoff, vpc)
    """
    # Validate framework type
    valid_frameworks = ["porters", "pestel", "swot", "ansoff", "vpc"]
    if framework_type not in valid_frameworks:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid framework type. Must be one of: {', '.join(valid_frameworks)}"
        )
    
    # Get framework results
    results = db.query(FrameworkResult).filter_by(
        run_id=run_id,
        framework_type=framework_type
    ).all()
    
    if not results:
        raise HTTPException(
            status_code=404, 
            detail=f"No {framework_type} results found for run {run_id}"
        )
    
    # Return detailed results
    return {
        "run_id": run_id,
        "framework_type": framework_type,
        "results_count": len(results),
        "results": [
            {
                "id": result.id,
                "component": result.component,
                "results": result.results,
                "confidence_score": result.confidence_score,
                "quality_score": result.quality_score,
                "citation_count": result.citation_count,
                "tokens_used": result.tokens_used,
                "cost": result.cost,
                "duration_seconds": result.duration_seconds,
                "created_at": result.created_at
            }
            for result in results
        ]
    }

@router.get("/{run_id}/logs", response_model=List[ActivityLogResponse])
async def get_run_logs(
    run_id: str,
    level: Optional[str] = Query(None, description="Filter by log level"),
    component: Optional[str] = Query(None, description="Filter by component"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs"),
    db: Session = Depends(get_db)
):
    """
    Get activity logs for a specific research run.
    
    Args:
        run_id: Research run ID
        level: Filter by log level (info, warning, error, debug)
        component: Filter by component name
        limit: Maximum number of logs to return
    """
    # Check if run exists
    run = db.query(ResearchRun).filter_by(id=run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")
    
    # Build query
    query = db.query(ActivityLog).filter_by(run_id=run_id)
    
    if level:
        query = query.filter(ActivityLog.level == level)
    
    if component:
        query = query.filter(ActivityLog.component.ilike(f"%{component}%"))
    
    # Order by timestamp descending and limit
    logs = query.order_by(desc(ActivityLog.timestamp)).limit(limit).all()
    
    return [ActivityLogResponse.from_orm(log) for log in logs]

@router.post("/{run_id}/retry")
async def retry_failed_run(run_id: str, db: Session = Depends(get_db)):
    """
    Retry a failed research run by creating a new run with the same parameters.
    """
    # Get the original run
    original_run = db.query(ResearchRun).filter_by(id=run_id).first()
    if not original_run:
        raise HTTPException(status_code=404, detail="Research run not found")
    
    if original_run.status != "failed":
        raise HTTPException(status_code=400, detail="Can only retry failed runs")
    
    # Create new run with same parameters
    import uuid
    from src.api.routes.research import StartResearchRequest, start_research_run
    from fastapi import BackgroundTasks
    
    new_run_id = str(uuid.uuid4())
    
    # Extract original parameters
    input_data = original_run.input_data or {}
    retry_request = StartResearchRequest(
        name=f"Retry of {original_run.name}",
        components=input_data.get("components", []),
        positioning_doc=input_data.get("positioning_doc"),
        config=input_data.get("config")
    )
    
    # Start new run
    background_tasks = BackgroundTasks()
    response = await start_research_run(retry_request, background_tasks, db)
    
    logger.info("Retrying failed run", 
               original_run_id=run_id, 
               new_run_id=response.run_id)
    
    return {
        "message": "Retry initiated",
        "original_run_id": run_id,
        "new_run_id": response.run_id,
        "status": response.status
    }

@router.get("/agents", response_model=List[AgentResponse])
async def list_agents(db: Session = Depends(get_db)):
    """
    List all available agents in the system.
    """
    agents = db.query(Agent).order_by(Agent.created_at.desc()).all()
    return [AgentResponse.from_orm(agent) for agent in agents]

@router.get("/recent")
async def get_recent_activity(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back (1-168)"),
    db: Session = Depends(get_db)
):
    """
    Get recent activity summary across all runs.
    
    Args:
        hours: Number of hours to look back (1-168, max 1 week)
    """
    since_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Get recent runs
    recent_runs = db.query(ResearchRun).filter(
        ResearchRun.created_at >= since_time
    ).order_by(desc(ResearchRun.created_at)).limit(20).all()
    
    # Get recent logs
    recent_logs = db.query(ActivityLog).filter(
        ActivityLog.timestamp >= since_time
    ).order_by(desc(ActivityLog.timestamp)).limit(50).all()
    
    # Summary statistics
    runs_by_status = {}
    for run in recent_runs:
        status = run.status
        runs_by_status[status] = runs_by_status.get(status, 0) + 1
    
    logs_by_level = {}
    for log in recent_logs:
        level = log.level
        logs_by_level[level] = logs_by_level.get(level, 0) + 1
    
    return {
        "period_hours": hours,
        "recent_runs": [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "created_at": run.created_at,
                "total_cost": run.total_cost
            }
            for run in recent_runs
        ],
        "recent_logs": [
            {
                "id": log.id,
                "run_id": log.run_id,
                "level": log.level,
                "message": log.message,
                "component": log.component,
                "timestamp": log.timestamp
            }
            for log in recent_logs
        ],
        "summary": {
            "total_runs": len(recent_runs),
            "runs_by_status": runs_by_status,
            "total_logs": len(recent_logs),
            "logs_by_level": logs_by_level
        }
    }