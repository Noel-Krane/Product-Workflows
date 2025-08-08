"""
LangSmith integration for comprehensive observability and tracing.
Provides real-time monitoring of AI research workflows.
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from functools import wraps
from contextlib import asynccontextmanager

try:
    from langsmith import Client, traceable, trace
    from langsmith.run_helpers import get_current_run_tree
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    # Create dummy decorators if langsmith not available
    def traceable(name: str = None, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def trace(name: str = None, **kwargs):
        @asynccontextmanager
        async def dummy_trace(**trace_kwargs):
            yield type('DummyRun', (), {'id': 'dummy'})()
        return dummy_trace(**kwargs)

import structlog
from src.config import get_settings

logger = structlog.get_logger(__name__)

class LangSmithTracker:
    """
    LangSmith integration for comprehensive workflow observability
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.project_name = self.settings.langchain_project or "ai-research-platform"
        self.enabled = LANGSMITH_AVAILABLE and bool(self.settings.langchain_api_key)
        
        if self.enabled:
            self._initialize_client()
        else:
            logger.warning("LangSmith not available or not configured")
    
    def _initialize_client(self):
        """Initialize LangSmith client"""
        try:
            # Set environment variables for LangSmith
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
            os.environ["LANGCHAIN_API_KEY"] = self.settings.langchain_api_key
            os.environ["LANGCHAIN_PROJECT"] = self.project_name
            
            self.client = Client()
            logger.info("LangSmith client initialized", project=self.project_name)
        except Exception as e:
            logger.error("Failed to initialize LangSmith client", error=str(e))
            self.enabled = False
    
    def research_workflow(self, name: str = "research_workflow"):
        """Decorator for tracking research workflows"""
        if not self.enabled:
            def dummy_decorator(func):
                return func
            return dummy_decorator
        
        return traceable(name=name, project_name=self.project_name)
    
    def framework_analysis(self, framework_name: str):
        """Decorator for tracking framework analysis (Porter's, PESTEL, etc.)"""
        if not self.enabled:
            def dummy_decorator(func):
                return func
            return dummy_decorator
        
        return traceable(name=f"{framework_name}_analysis", project_name=self.project_name)
    
    def research_phase(self, phase_name: str):
        """Decorator for tracking research phases"""
        if not self.enabled:
            def dummy_decorator(func):
                return func
            return dummy_decorator
        
        return traceable(name=f"phase_{phase_name}", project_name=self.project_name)
    
    def api_call_tracker(self, call_type: str):
        """Decorator for tracking API calls"""
        if not self.enabled:
            def dummy_decorator(func):
                return func
            return dummy_decorator
        
        return traceable(name=f"api_call_{call_type}", project_name=self.project_name)
    
    @asynccontextmanager
    async def trace_research_run(self, run_id: str, config: Dict[str, Any]):
        """Context manager for tracing entire research runs"""
        if not self.enabled:
            yield type('DummyRun', (), {'id': run_id})()
            return
        
        async with trace(
            name="research_run",
            inputs={
                "run_id": run_id,
                "config": config,
                "timestamp": datetime.utcnow().isoformat()
            },
            project_name=self.project_name
        ) as run:
            try:
                yield run
            except Exception as e:
                if hasattr(run, 'update'):
                    run.update(
                        outputs={"error": str(e)},
                        extra={"status": "failed", "error_type": type(e).__name__}
                    )
                raise
            else:
                if hasattr(run, 'update'):
                    run.update(
                        extra={"status": "completed", "completed_at": datetime.utcnow().isoformat()}
                    )
    
    @asynccontextmanager 
    async def trace_competitor_discovery(self, component: str, expected_count: int = 3):
        """Context manager for tracing competitor discovery"""
        if not self.enabled:
            yield type('DummyRun', (), {'id': 'dummy'})()
            return
        
        async with trace(
            name="competitor_discovery",
            inputs={
                "component": component,
                "expected_competitors": expected_count,
                "timestamp": datetime.utcnow().isoformat()
            },
            project_name=self.project_name
        ) as run:
            yield run
    
    @asynccontextmanager
    async def trace_framework_execution(self, framework: str, components: List[str]):
        """Context manager for tracing framework analysis execution"""
        if not self.enabled:
            yield type('DummyRun', (), {'id': 'dummy'})()
            return
        
        async with trace(
            name=f"{framework}_framework",
            inputs={
                "framework": framework,
                "components": components,
                "timestamp": datetime.utcnow().isoformat()
            },
            project_name=self.project_name
        ) as run:
            yield run
    
    async def log_cost_metrics(self, run_id: str, cost_data: Dict[str, Any]):
        """Log cost metrics to LangSmith"""
        if not self.enabled:
            return
        
        try:
            # Get current run if available
            current_run = get_current_run_tree()
            if current_run:
                current_run.update(
                    extra={
                        "cost_tracking": cost_data,
                        "run_id": run_id,
                        "cost_timestamp": datetime.utcnow().isoformat()
                    }
                )
        except Exception as e:
            logger.error("Failed to log cost metrics to LangSmith", error=str(e))
    
    async def log_research_quality(self, 
                                  framework: str, 
                                  quality_score: float,
                                  citations_count: int,
                                  confidence_score: float):
        """Log research quality metrics"""
        if not self.enabled:
            return
        
        try:
            current_run = get_current_run_tree()
            if current_run:
                current_run.update(
                    extra={
                        "quality_metrics": {
                            "framework": framework,
                            "quality_score": quality_score,
                            "citations_count": citations_count,
                            "confidence_score": confidence_score,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }
                )
        except Exception as e:
            logger.error("Failed to log quality metrics", error=str(e))
    
    async def log_performance_metrics(self, 
                                    phase: str,
                                    duration_seconds: float,
                                    tokens_used: int,
                                    api_calls_count: int):
        """Log performance metrics for analysis phases"""
        if not self.enabled:
            return
        
        try:
            current_run = get_current_run_tree()
            if current_run:
                current_run.update(
                    extra={
                        "performance_metrics": {
                            "phase": phase,
                            "duration_seconds": duration_seconds,
                            "tokens_used": tokens_used,
                            "api_calls_count": api_calls_count,
                            "tokens_per_second": tokens_used / duration_seconds if duration_seconds > 0 else 0,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }
                )
        except Exception as e:
            logger.error("Failed to log performance metrics", error=str(e))
    
    async def log_framework_results(self, 
                                  framework: str,
                                  results: Dict[str, Any],
                                  component: Optional[str] = None):
        """Log framework analysis results"""
        if not self.enabled:
            return
        
        try:
            current_run = get_current_run_tree()
            if current_run:
                # Extract key metrics for logging (avoid logging full results due to size)
                result_summary = {
                    "framework": framework,
                    "component": component,
                    "result_keys": list(results.keys()) if isinstance(results, dict) else [],
                    "result_size": len(str(results)),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Add framework-specific metrics
                if framework == "porters":
                    if "forces" in results:
                        result_summary["forces_analyzed"] = len(results["forces"])
                elif framework == "pestel":
                    if "factors" in results:
                        result_summary["factors_analyzed"] = len(results["factors"])
                elif framework == "swot":
                    swot_counts = {}
                    for category in ["strengths", "weaknesses", "opportunities", "threats"]:
                        if category in results:
                            swot_counts[f"{category}_count"] = len(results[category]) if isinstance(results[category], list) else 1
                    result_summary.update(swot_counts)
                
                current_run.update(
                    outputs={"framework_results": result_summary}
                )
        except Exception as e:
            logger.error("Failed to log framework results", error=str(e))
    
    async def create_custom_metric(self, 
                                 metric_name: str, 
                                 value: Any,
                                 langsmith_metadata: Optional[Dict[str, Any]] = None):
        """Create custom metric in current trace"""
        if not self.enabled:
            return
        
        try:
            current_run = get_current_run_tree()
            if current_run:
                custom_metrics = current_run.extra.get("custom_metrics", {})
                custom_metrics[metric_name] = {
                    "value": value,
                    "metadata": langsmith_metadata or {},
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                current_run.update(
                    extra={
                        **current_run.extra,
                        "custom_metrics": custom_metrics
                    }
                )
        except Exception as e:
            logger.error("Failed to create custom metric", error=str(e))
    
    async def get_run_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get statistics from LangSmith for the past N days"""
        if not self.enabled or not self.client:
            return {"error": "LangSmith not available"}
        
        try:
            # Get runs from the past N days
            from datetime import datetime, timedelta
            since = datetime.now() - timedelta(days=days)
            
            runs = list(self.client.list_runs(
                project_name=self.project_name,
                start_time=since
            ))
            
            # Analyze runs
            total_runs = len(runs)
            successful_runs = sum(1 for run in runs if run.status == "success")
            failed_runs = sum(1 for run in runs if run.status == "error")
            
            # Calculate average duration
            durations = [
                (run.end_time - run.start_time).total_seconds() 
                for run in runs 
                if run.end_time and run.start_time
            ]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            return {
                "period_days": days,
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "failed_runs": failed_runs,
                "success_rate": successful_runs / total_runs if total_runs > 0 else 0,
                "average_duration_seconds": avg_duration,
                "project_name": self.project_name
            }
        except Exception as e:
            logger.error("Failed to get run statistics", error=str(e))
            return {"error": str(e)}
    
    async def health_check(self) -> bool:
        """Check if LangSmith is properly configured and accessible"""
        if not self.enabled:
            return False
        
        try:
            # Try to access the project
            if self.client:
                # Simple test to verify connection
                list(self.client.list_runs(project_name=self.project_name, limit=1))
                return True
        except Exception as e:
            logger.error("LangSmith health check failed", error=str(e))
        
        return False

# Global instance
langsmith_tracker = LangSmithTracker()

# Convenience decorators using the global instance
def trace_research_workflow(name: str = "research_workflow"):
    """Convenience decorator for research workflows"""
    return langsmith_tracker.research_workflow(name)

def trace_framework_analysis(framework_name: str):
    """Convenience decorator for framework analysis"""
    return langsmith_tracker.framework_analysis(framework_name)

def trace_research_phase(phase_name: str):
    """Convenience decorator for research phases"""
    return langsmith_tracker.research_phase(phase_name)

def trace_api_call(call_type: str):
    """Convenience decorator for API calls"""
    return langsmith_tracker.api_call_tracker(call_type)