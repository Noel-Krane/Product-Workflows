"""
Cost tracking and budget management for AI research platform.
Provides real-time cost monitoring with soft/hard caps and alerts.
"""

import asyncio
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pydantic import BaseModel
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class BudgetConfig:
    """Budget configuration with multiple limits"""
    monthly_hard_cap: float = 20.00
    monthly_soft_cap: float = 15.00
    per_run_soft_cap: float = 1.50
    per_run_hard_cap: float = 3.00
    daily_soft_cap: float = 2.00

class CostEntry(BaseModel):
    """Individual cost tracking entry"""
    id: Optional[int] = None
    run_id: Optional[str] = None
    model_name: str
    input_tokens: int
    output_tokens: int
    cost: float
    call_type: str
    duration_seconds: float
    timestamp: datetime
    metadata: Dict[str, Any] = {}

class BudgetStatus(BaseModel):
    """Current budget status and usage"""
    monthly_usage: float
    monthly_limit: float
    monthly_remaining: float
    monthly_percentage: float
    daily_usage: float
    daily_limit: float
    current_run_cost: float
    run_limit: float
    can_continue: bool
    warnings: List[str] = []
    recommendations: List[str] = []

class CostTracker:
    """
    Comprehensive cost tracking with budget enforcement and alerting
    """
    
    def __init__(self, budget_config: Optional[BudgetConfig] = None, db_path: str = "ai_research_platform.db"):
        self.budget = budget_config or BudgetConfig()
        self.db_path = db_path
        self.current_run_id: Optional[str] = None
        self.current_run_cost: float = 0.0
        self._init_database()
    
    def _init_database(self):
        """Initialize cost tracking tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if cost_tracking table exists, if not create it
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cost_tracking (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        run_id TEXT,
                        model_name TEXT NOT NULL,
                        input_tokens INTEGER NOT NULL,
                        output_tokens INTEGER NOT NULL,
                        cost REAL NOT NULL,
                        call_type TEXT NOT NULL,
                        duration_seconds REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                """)
                
                # Create index for faster queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_cost_tracking_timestamp 
                    ON cost_tracking(timestamp)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_cost_tracking_run_id 
                    ON cost_tracking(run_id)
                """)
                conn.commit()
                logger.info("Cost tracking database initialized")
        except Exception as e:
            logger.error("Failed to initialize cost tracking database", error=str(e))
            raise
    
    async def start_run(self, run_id: str) -> bool:
        """
        Start tracking costs for a new run
        
        Args:
            run_id: Unique identifier for the run
            
        Returns:
            True if run can start, False if budget constraints prevent it
        """
        # Check if we can start a new run
        status = await self.get_budget_status()
        
        if not status.can_continue:
            logger.warning("Cannot start run due to budget constraints", 
                          run_id=run_id,
                          warnings=status.warnings)
            return False
        
        # Check if estimated run cost would exceed limits
        estimated_run_cost = self.budget.per_run_soft_cap
        if status.monthly_remaining < estimated_run_cost:
            logger.warning("Cannot start run - insufficient monthly budget remaining",
                          run_id=run_id,
                          estimated_cost=estimated_run_cost,
                          remaining=status.monthly_remaining)
            return False
        
        self.current_run_id = run_id
        self.current_run_cost = 0.0
        
        logger.info("Started cost tracking for run", 
                   run_id=run_id,
                   monthly_usage=status.monthly_usage,
                   monthly_remaining=status.monthly_remaining)
        
        return True
    
    async def track_api_call(self,
                           model: str,
                           input_tokens: int,
                           output_tokens: int,
                           cost: float,
                           call_type: str,
                           duration: float = 0.0,
                           call_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Track an individual API call with cost and usage
        
        Returns:
            Dictionary with cost tracking information and budget status
        """
        entry = CostEntry(
            run_id=self.current_run_id,
            model_name=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            call_type=call_type,
            duration_seconds=duration,
            timestamp=datetime.utcnow(),
            metadata=call_metadata or {}
        )
        
        # Store in database
        await self._store_cost_entry(entry)
        
        # Update current run cost
        self.current_run_cost += cost
        
        # Check budget constraints
        status = await self.get_budget_status()
        
        # Log the API call
        logger.info("API call tracked",
                   model=model,
                   cost=cost,
                   run_cost=self.current_run_cost,
                   monthly_usage=status.monthly_usage,
                   call_type=call_type)
        
        # Check for warnings
        if status.warnings:
            logger.warning("Budget warnings triggered", warnings=status.warnings)
        
        return {
            "cost": cost,
            "run_cost": self.current_run_cost,
            "monthly_usage": status.monthly_usage,
            "budget_remaining": status.monthly_remaining,
            "can_continue": status.can_continue,
            "warnings": status.warnings,
            "tokens_used": input_tokens + output_tokens
        }
    
    async def _store_cost_entry(self, entry: CostEntry):
        """Store cost entry in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO cost_tracking 
                    (run_id, model_name, input_tokens, output_tokens, cost, 
                     call_type, duration_seconds, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.run_id,
                    entry.model_name,
                    entry.input_tokens,
                    entry.output_tokens,
                    entry.cost,
                    entry.call_type,
                    entry.duration_seconds,
                    entry.timestamp.isoformat(),
                    str(entry.metadata) if entry.metadata else None
                ))
                conn.commit()
        except Exception as e:
            logger.error("Failed to store cost entry", error=str(e), entry=entry)
            raise
    
    async def can_make_call(self, estimated_cost: float) -> bool:
        """
        Check if an API call can be made given current budget status
        
        Args:
            estimated_cost: Estimated cost of the upcoming call
            
        Returns:
            True if call can be made, False otherwise
        """
        status = await self.get_budget_status()
        
        # Check hard caps first
        if status.monthly_usage + estimated_cost > self.budget.monthly_hard_cap:
            return False
        
        if self.current_run_cost + estimated_cost > self.budget.per_run_hard_cap:
            return False
        
        # Check daily cap
        if status.daily_usage + estimated_cost > self.budget.daily_soft_cap * 1.5:  # 50% buffer on daily
            return False
        
        return True
    
    async def get_budget_status(self) -> BudgetStatus:
        """Get current budget status with usage statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get monthly usage
                month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                cursor.execute("""
                    SELECT COALESCE(SUM(cost), 0) 
                    FROM cost_tracking 
                    WHERE timestamp >= ?
                """, (month_start.isoformat(),))
                monthly_usage = cursor.fetchone()[0]
                
                # Get daily usage
                day_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                cursor.execute("""
                    SELECT COALESCE(SUM(cost), 0) 
                    FROM cost_tracking 
                    WHERE timestamp >= ?
                """, (day_start.isoformat(),))
                daily_usage = cursor.fetchone()[0]
                
        except Exception as e:
            logger.error("Failed to get budget status", error=str(e))
            monthly_usage = 0.0
            daily_usage = 0.0
        
        monthly_remaining = self.budget.monthly_hard_cap - monthly_usage
        monthly_percentage = (monthly_usage / self.budget.monthly_hard_cap) * 100
        
        # Determine if we can continue
        can_continue = (
            monthly_usage < self.budget.monthly_hard_cap and
            self.current_run_cost < self.budget.per_run_hard_cap and
            daily_usage < self.budget.daily_soft_cap * 1.5
        )
        
        # Generate warnings
        warnings = []
        recommendations = []
        
        if monthly_usage > self.budget.monthly_soft_cap:
            warnings.append(f"Monthly soft cap exceeded: ${monthly_usage:.2f} / ${self.budget.monthly_soft_cap:.2f}")
        
        if monthly_percentage > 80:
            warnings.append(f"Monthly budget at {monthly_percentage:.1f}% capacity")
            recommendations.append("Consider reducing API usage or increasing budget")
        
        if self.current_run_cost > self.budget.per_run_soft_cap:
            warnings.append(f"Current run cost exceeds soft cap: ${self.current_run_cost:.2f} / ${self.budget.per_run_soft_cap:.2f}")
        
        if daily_usage > self.budget.daily_soft_cap:
            warnings.append(f"Daily usage exceeded: ${daily_usage:.2f} / ${self.budget.daily_soft_cap:.2f}")
            recommendations.append("Consider running fewer research sessions today")
        
        if monthly_remaining < self.budget.per_run_soft_cap:
            warnings.append("Insufficient budget remaining for another full run")
            recommendations.append("Wait until next month or increase budget")
        
        return BudgetStatus(
            monthly_usage=monthly_usage,
            monthly_limit=self.budget.monthly_hard_cap,
            monthly_remaining=monthly_remaining,
            monthly_percentage=monthly_percentage,
            daily_usage=daily_usage,
            daily_limit=self.budget.daily_soft_cap,
            current_run_cost=self.current_run_cost,
            run_limit=self.budget.per_run_hard_cap,
            can_continue=can_continue,
            warnings=warnings,
            recommendations=recommendations
        )
    
    async def get_cost_breakdown(self, days: int = 30) -> Dict[str, Any]:
        """
        Get detailed cost breakdown for analysis
        
        Args:
            days: Number of days to include in breakdown
            
        Returns:
            Dictionary with cost breakdown by model, call type, etc.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                since_date = datetime.now() - timedelta(days=days)
                
                # Cost by model
                cursor.execute("""
                    SELECT model_name, 
                           COUNT(*) as calls, 
                           SUM(cost) as total_cost,
                           SUM(input_tokens) as input_tokens,
                           SUM(output_tokens) as output_tokens
                    FROM cost_tracking 
                    WHERE timestamp >= ?
                    GROUP BY model_name
                    ORDER BY total_cost DESC
                """, (since_date.isoformat(),))
                
                by_model = [
                    {
                        "model": row[0],
                        "calls": row[1],
                        "cost": row[2],
                        "input_tokens": row[3],
                        "output_tokens": row[4],
                        "avg_cost_per_call": row[2] / row[1] if row[1] > 0 else 0
                    }
                    for row in cursor.fetchall()
                ]
                
                # Cost by call type
                cursor.execute("""
                    SELECT call_type, 
                           COUNT(*) as calls,
                           SUM(cost) as total_cost,
                           AVG(cost) as avg_cost
                    FROM cost_tracking 
                    WHERE timestamp >= ?
                    GROUP BY call_type
                    ORDER BY total_cost DESC
                """, (since_date.isoformat(),))
                
                by_call_type = [
                    {
                        "call_type": row[0],
                        "calls": row[1],
                        "cost": row[2],
                        "avg_cost": row[3]
                    }
                    for row in cursor.fetchall()
                ]
                
                # Daily usage
                cursor.execute("""
                    SELECT DATE(timestamp) as date,
                           SUM(cost) as daily_cost,
                           COUNT(*) as daily_calls
                    FROM cost_tracking 
                    WHERE timestamp >= ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                """, (since_date.isoformat(),))
                
                daily_usage = [
                    {
                        "date": row[0],
                        "cost": row[1],
                        "calls": row[2]
                    }
                    for row in cursor.fetchall()
                ]
                
                # Total statistics
                cursor.execute("""
                    SELECT COUNT(*) as total_calls,
                           SUM(cost) as total_cost,
                           AVG(cost) as avg_cost,
                           MIN(timestamp) as first_call,
                           MAX(timestamp) as last_call
                    FROM cost_tracking 
                    WHERE timestamp >= ?
                """, (since_date.isoformat(),))
                
                stats = cursor.fetchone()
                summary = {
                    "total_calls": stats[0],
                    "total_cost": stats[1] or 0.0,
                    "avg_cost_per_call": stats[2] or 0.0,
                    "first_call": stats[3],
                    "last_call": stats[4],
                    "period_days": days
                }
                
                return {
                    "summary": summary,
                    "by_model": by_model,
                    "by_call_type": by_call_type,
                    "daily_usage": daily_usage
                }
                
        except Exception as e:
            logger.error("Failed to get cost breakdown", error=str(e))
            return {
                "summary": {"total_calls": 0, "total_cost": 0.0},
                "by_model": [],
                "by_call_type": [],
                "daily_usage": []
            }
    
    async def end_run(self) -> Dict[str, Any]:
        """End the current run and return summary"""
        if not self.current_run_id:
            return {"error": "No active run"}
        
        run_summary = {
            "run_id": self.current_run_id,
            "total_cost": self.current_run_cost,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Get budget status
        status = await self.get_budget_status()
        run_summary.update({
            "monthly_usage": status.monthly_usage,
            "monthly_remaining": status.monthly_remaining,
            "warnings": status.warnings
        })
        
        logger.info("Run completed", **run_summary)
        
        # Reset run tracking
        self.current_run_id = None
        self.current_run_cost = 0.0
        
        return run_summary
    
    async def update_budget(self, new_budget: BudgetConfig):
        """Update budget configuration"""
        old_budget = self.budget
        self.budget = new_budget
        
        logger.info("Budget configuration updated",
                   old_monthly_cap=old_budget.monthly_hard_cap,
                   new_monthly_cap=new_budget.monthly_hard_cap,
                   old_run_cap=old_budget.per_run_hard_cap,
                   new_run_cap=new_budget.per_run_hard_cap)