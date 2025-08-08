"""
Research API routes for managing research runs and workflows.
"""

import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db.models import (
    db_manager, ResearchRun, Agent, FrameworkResult,
    ResearchRunCreate, ResearchRunResponse, FrameworkResultResponse
)
from src.observability.tracker import CostTracker, BudgetStatus
from src.observability.langsmith_integration import langsmith_tracker
from src.api.openrouter_client import OpenRouterClient
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/research", tags=["research"])

# Request/Response models
class StartResearchRequest(BaseModel):
    name: str
    components: List[str]
    positioning_doc: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None

class ResearchStatusResponse(BaseModel):
    run_id: str
    status: str
    progress: Optional[Dict[str, Any]] = None
    current_step: Optional[str] = None
    estimated_completion: Optional[str] = None
    cost_info: Optional[Dict[str, Any]] = None
    errors: List[str] = []

class ResearchResultsResponse(BaseModel):
    run_id: str
    status: str
    frameworks: List[FrameworkResultResponse]
    total_cost: float
    duration_seconds: Optional[float]
    summary: Optional[Dict[str, Any]] = None

# Dependency to get database session
def get_db():
    with db_manager.get_session() as session:
        yield session

# Global instances
cost_tracker = CostTracker()
openrouter_client = OpenRouterClient(cost_tracker)

@router.post("/run", response_model=ResearchStatusResponse)
async def start_research_run(
    request: StartResearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start a new research run with specified components and configuration.
    """
    # Validate components
    if not request.components:
        raise HTTPException(status_code=400, detail="At least one component must be specified")
    
    # Check budget before starting
    budget_status = await cost_tracker.get_budget_status()
    if not budget_status.can_continue:
        raise HTTPException(
            status_code=402, 
            detail=f"Budget constraints prevent starting new run: {', '.join(budget_status.warnings)}"
        )
    
    # Generate run ID
    run_id = str(uuid.uuid4())
    
    # Check if we can start this run
    if not await cost_tracker.start_run(run_id):
        raise HTTPException(
            status_code=402,
            detail="Cannot start run due to budget constraints"
        )
    
    # Get research agent
    agent = db.query(Agent).filter_by(type="researcher", status="active").first()
    if not agent:
        raise HTTPException(status_code=500, detail="No active research agent found")
    
    # Create research run record
    run = ResearchRun(
        id=run_id,
        agent_id=agent.id,
        name=request.name,
        status="pending",
        input_data={
            "components": request.components,
            "positioning_doc": request.positioning_doc,
            "config": request.config
        },
        run_metadata={
            "budget_at_start": budget_status.monthly_usage,
            "estimated_cost": budget_status.run_limit
        },
        start_time=datetime.utcnow()
    )
    
    db.add(run)
    db.commit()
    db.refresh(run)
    
    logger.info("Research run created", 
               run_id=run_id, 
               components=request.components,
               budget_remaining=budget_status.monthly_remaining)
    
    # Start research workflow in background
    background_tasks.add_task(execute_research_workflow, run_id, request, db_manager)
    
    return ResearchStatusResponse(
        run_id=run_id,
        status="pending",
        current_step="initialization",
        cost_info={
            "monthly_usage": budget_status.monthly_usage,
            "monthly_remaining": budget_status.monthly_remaining,
            "estimated_run_cost": budget_status.run_limit
        }
    )

@router.get("/run/{run_id}", response_model=ResearchStatusResponse)
async def get_research_status(run_id: str, db: Session = Depends(get_db)):
    """
    Get the current status of a research run.
    """
    run = db.query(ResearchRun).filter_by(id=run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")
    
    # Get current budget status
    budget_status = await cost_tracker.get_budget_status()
    
    # Calculate progress based on completed frameworks
    completed_frameworks = db.query(FrameworkResult).filter_by(run_id=run_id).count()
    total_frameworks = 5  # Porter's, PESTEL, SWOT, Ansoff, VPC
    progress_percentage = (completed_frameworks / total_frameworks) * 100 if completed_frameworks > 0 else 0
    
    progress = {
        "completed_frameworks": completed_frameworks,
        "total_frameworks": total_frameworks,
        "percentage": progress_percentage
    }
    
    # Determine current step
    current_step = "unknown"
    if run.status == "pending":
        current_step = "initialization"
    elif run.status == "running":
        if completed_frameworks == 0:
            current_step = "competitor_discovery"
        elif completed_frameworks == 1:
            current_step = "pestel_analysis"
        elif completed_frameworks == 2:
            current_step = "swot_analysis"
        elif completed_frameworks == 3:
            current_step = "ansoff_analysis"
        elif completed_frameworks == 4:
            current_step = "vpc_analysis"
        else:
            current_step = "generating_reports"
    
    return ResearchStatusResponse(
        run_id=run_id,
        status=run.status,
        progress=progress,
        current_step=current_step,
        cost_info={
            "run_cost": run.total_cost or 0.0,
            "monthly_usage": budget_status.monthly_usage,
            "monthly_remaining": budget_status.monthly_remaining
        },
        errors=[run.error_message] if run.error_message else []
    )

@router.get("/run/{run_id}/results", response_model=ResearchResultsResponse)
async def get_research_results(run_id: str, db: Session = Depends(get_db)):
    """
    Get the results of a completed research run.
    """
    run = db.query(ResearchRun).filter_by(id=run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")
    
    if run.status not in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Research run not yet completed")
    
    # Get framework results
    framework_results = db.query(FrameworkResult).filter_by(run_id=run_id).all()
    framework_responses = [
        FrameworkResultResponse.from_orm(result) for result in framework_results
    ]
    
    # Generate summary
    summary = None
    if run.status == "completed" and framework_results:
        summary = {
            "total_frameworks": len(framework_results),
            "avg_confidence": sum(r.confidence_score or 0 for r in framework_results) / len(framework_results),
            "total_citations": sum(r.citation_count for r in framework_results),
            "components_analyzed": list(set(r.component for r in framework_results if r.component))
        }
    
    return ResearchResultsResponse(
        run_id=run_id,
        status=run.status,
        frameworks=framework_responses,
        total_cost=run.total_cost or 0.0,
        duration_seconds=run.duration_seconds,
        summary=summary
    )

@router.get("/runs", response_model=List[ResearchRunResponse])
async def list_research_runs(
    limit: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List recent research runs with optional status filtering.
    """
    query = db.query(ResearchRun).order_by(ResearchRun.created_at.desc())
    
    if status:
        query = query.filter(ResearchRun.status == status)
    
    runs = query.limit(limit).all()
    return [ResearchRunResponse.from_orm(run) for run in runs]

@router.delete("/run/{run_id}")
async def cancel_research_run(run_id: str, db: Session = Depends(get_db)):
    """
    Cancel a running research run.
    """
    run = db.query(ResearchRun).filter_by(id=run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")
    
    if run.status not in ["pending", "running"]:
        raise HTTPException(status_code=400, detail="Can only cancel pending or running runs")
    
    # Update run status
    run.status = "cancelled"
    run.end_time = datetime.utcnow()
    if run.start_time:
        run.duration_seconds = (run.end_time - run.start_time).total_seconds()
    
    db.commit()
    
    logger.info("Research run cancelled", run_id=run_id)
    
    return {"message": "Research run cancelled", "run_id": run_id}

@router.get("/frameworks")
async def list_available_frameworks():
    """
    List available research frameworks and their descriptions.
    """
    frameworks = [
        {
            "name": "porters",
            "title": "Porter's Five Forces",
            "description": "Competitive analysis framework examining industry rivalry, threats, and market dynamics",
            "weight": 0.35,
            "estimated_duration_minutes": 8
        },
        {
            "name": "pestel",
            "title": "PESTEL Analysis", 
            "description": "Macro-environment analysis covering Political, Economic, Social, Technological, Environmental, and Legal factors",
            "weight": 0.25,
            "estimated_duration_minutes": 6
        },
        {
            "name": "swot",
            "title": "SWOT Analysis",
            "description": "Strategic positioning analysis of Strengths, Weaknesses, Opportunities, and Threats",
            "weight": 0.25,
            "estimated_duration_minutes": 5
        },
        {
            "name": "ansoff",
            "title": "Ansoff Matrix",
            "description": "Growth opportunity analysis focusing on market penetration and product development",
            "weight": 0.15,
            "estimated_duration_minutes": 4
        },
        {
            "name": "vpc",
            "title": "Value Proposition Canvas",
            "description": "Customer needs analysis mapping jobs, pains, and gains to product features",
            "weight": 0.10,
            "estimated_duration_minutes": 3
        }
    ]
    
    return {"frameworks": frameworks}

# Background task for executing research workflow
async def execute_research_workflow(run_id: str, request: StartResearchRequest, db_manager):
    """
    Execute the research workflow in the background.
    This is a simplified version - Phase 2 will implement the full workflow.
    """
    logger.info("Starting research workflow execution", run_id=run_id)
    
    with db_manager.get_session() as db:
        run = db.query(ResearchRun).filter_by(id=run_id).first()
        if not run:
            logger.error("Run not found", run_id=run_id)
            return
        
        try:
            # Update status to running
            run.status = "running"
            db.commit()
            
            # Simulate research workflow execution
            # This will be replaced with actual workflow in Phase 2
            logger.info("Simulating research workflow", run_id=run_id)
            
            # Simulate competitor discovery
            await asyncio.sleep(2)
            logger.info("Competitor discovery completed", run_id=run_id)
            
            # Simulate framework analyses
            frameworks = ["porters", "pestel", "swot", "ansoff", "vpc"]
            for i, framework in enumerate(frameworks):
                await asyncio.sleep(3)  # Simulate analysis time
                
                # Create mock framework result
                result = FrameworkResult(
                    run_id=run_id,
                    framework_type=framework,
                    component=request.components[0] if request.components else "general",
                    results={"mock": f"results for {framework}"},
                    confidence_score=0.8,
                    quality_score=0.85,
                    citation_count=5,
                    tokens_used=1000,
                    api_calls_count=3,
                    cost=0.15,
                    duration_seconds=3.0
                )
                db.add(result)
                
                # Update run cost
                run.total_cost = (run.total_cost or 0.0) + 0.15
                
                logger.info("Framework analysis completed", 
                           framework=framework, 
                           run_id=run_id,
                           progress=f"{i+1}/{len(frameworks)}")
            
            # Complete the run
            run.status = "completed"
            run.end_time = datetime.utcnow()
            if run.start_time:
                run.duration_seconds = (run.end_time - run.start_time).total_seconds()
            
            db.commit()
            
            # End cost tracking
            cost_summary = await cost_tracker.end_run()
            logger.info("Research workflow completed", 
                       run_id=run_id,
                       cost_summary=cost_summary)
            
        except Exception as e:
            logger.error("Research workflow failed", run_id=run_id, error=str(e))
            
            # Update run with error
            run.status = "failed"
            run.error_message = str(e)
            run.end_time = datetime.utcnow()
            if run.start_time:
                run.duration_seconds = (run.end_time - run.start_time).total_seconds()
            
            db.commit()
            
            # End cost tracking
            await cost_tracker.end_run()