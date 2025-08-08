"""
Database models for AI research platform using SQLAlchemy ORM.
Provides structured access to research data with relationships.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy import create_engine
from pydantic import BaseModel
import json

Base = declarative_base()

class Agent(Base):
    """Agent registry table"""
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    type = Column(String, nullable=False)  # 'researcher', 'analyst', etc.
    version = Column(String, default='1.0.0')
    config = Column(JSON)  # Agent-specific configuration
    status = Column(String, default='active')  # 'active', 'inactive', 'maintenance'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    runs = relationship("ResearchRun", back_populates="agent")

class ResearchRun(Base):
    """Research runs table"""
    __tablename__ = "research_runs"
    
    id = Column(String, primary_key=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default='pending')  # 'pending', 'running', 'completed', 'failed', 'cancelled'
    input_data = Column(JSON)  # Research parameters and input
    output_data = Column(JSON)  # Final research results
    run_metadata = Column(JSON)  # Additional run metadata
    error_message = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_seconds = Column(Float)
    total_cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="runs")
    framework_results = relationship("FrameworkResult", back_populates="run")
    cost_entries = relationship("CostTracking", back_populates="run")
    activity_logs = relationship("ActivityLog", back_populates="run")

class FrameworkResult(Base):
    """Framework analysis results"""
    __tablename__ = "framework_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("research_runs.id"), nullable=False)
    framework_type = Column(String, nullable=False)  # 'porters', 'pestel', 'swot', 'ansoff', 'vpc'
    component = Column(String)  # Crane component analyzed
    results = Column(JSON, nullable=False)  # Framework results
    confidence_score = Column(Float)
    quality_score = Column(Float)
    citation_count = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    api_calls_count = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    duration_seconds = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    run = relationship("ResearchRun", back_populates="framework_results")

class CostTracking(Base):
    """Individual API call cost tracking"""
    __tablename__ = "cost_tracking"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("research_runs.id"))
    model_name = Column(String, nullable=False)
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    call_type = Column(String, nullable=False)  # 'competitor_research', 'framework_analysis', etc.
    duration_seconds = Column(Float)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    call_metadata = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    run = relationship("ResearchRun", back_populates="cost_entries")

class CompetitorProfile(Base):
    """Discovered competitor profiles"""
    __tablename__ = "competitor_profiles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("research_runs.id"))
    company_name = Column(String, nullable=False)
    component = Column(String)  # Crane component they compete with
    competitor_type = Column(String)  # 'direct', 'partial'
    url = Column(String)
    description = Column(Text)
    analysis_data = Column(JSON)  # Detailed competitor analysis
    funding_info = Column(JSON)
    company_size = Column(String)
    target_market = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class ActivityLog(Base):
    """Activity logging for observability"""
    __tablename__ = "activity_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("research_runs.id"))
    agent_id = Column(String, ForeignKey("agents.id"))
    level = Column(String, nullable=False)  # 'info', 'warning', 'error', 'debug'
    message = Column(Text, nullable=False)
    component = Column(String)  # Which part of system generated log
    action = Column(String)  # What action was being performed
    details = Column(JSON)  # Additional details
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    run = relationship("ResearchRun", back_populates="activity_logs")

class UserSettings(Base):
    """User configuration and preferences"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    setting_key = Column(String, nullable=False, unique=True)
    setting_value = Column(JSON, nullable=False)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WatchlistSource(Base):
    """Trusted sources for research"""
    __tablename__ = "watchlist_sources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String)
    source_type = Column(String, nullable=False)  # 'academic', 'industry', 'influencer', 'primary'
    category = Column(String)  # 'construction_tech', 'ai_trends', etc.
    weight = Column(Float, default=1.0)  # Source credibility weight
    active = Column(Boolean, default=True)
    last_checked = Column(DateTime)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models for API serialization
class AgentCreate(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    type: str
    config: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    type: str
    version: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ResearchRunCreate(BaseModel):
    name: str
    agent_id: str
    input_data: Dict[str, Any]
    run_metadata: Optional[Dict[str, Any]] = None

class ResearchRunResponse(BaseModel):
    id: str
    agent_id: str
    name: str
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    total_cost: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class FrameworkResultResponse(BaseModel):
    id: int
    run_id: str
    framework_type: str
    component: Optional[str]
    confidence_score: Optional[float]
    quality_score: Optional[float]
    citation_count: int
    cost: float
    duration_seconds: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

class CostTrackingResponse(BaseModel):
    id: int
    run_id: Optional[str]
    model_name: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float
    call_type: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Database utility functions
class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self, database_url: str = "sqlite:///ai_research_platform.db"):
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self._create_tables()
        self._initialize_default_data()
    
    def _create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
    
    def _initialize_default_data(self):
        """Initialize default data if tables are empty"""
        with Session(self.engine) as session:
            # Check if we have any agents
            if session.query(Agent).count() == 0:
                # Create default research agent
                default_agent = Agent(
                    id="research-agent-v1",
                    name="Strategic Research Agent",
                    description="Multi-framework business analysis agent using Porter's Five Forces, PESTEL, SWOT, Ansoff Matrix, and Value Proposition Canvas",
                    type="researcher",
                    version="1.0.0",
                    config={
                        "frameworks": ["porters", "pestel", "swot", "ansoff", "vpc"],
                        "max_cost_per_run": 3.00,
                        "default_model": "anthropic/claude-3.5-sonnet"
                    },
                    status="active"
                )
                session.add(default_agent)
            
            # Initialize default user settings
            default_settings = [
                ("monthly_budget", 20.00, "Monthly budget limit in USD"),
                ("per_run_budget", 1.50, "Per-run budget soft cap in USD"),
                ("default_model", "anthropic/claude-3.5-sonnet", "Default LLM model"),
                ("research_depth", "standard", "Research depth: quick, standard, comprehensive"),
                ("auto_citations", True, "Automatically require citations in research"),
                ("framework_weights", {
                    "porters": 0.35,
                    "pestel": 0.25, 
                    "swot": 0.25,
                    "ansoff": 0.15
                }, "Framework analysis time allocation weights")
            ]
            
            for key, value, desc in default_settings:
                existing = session.query(UserSettings).filter_by(setting_key=key).first()
                if not existing:
                    setting = UserSettings(
                        setting_key=key,
                        setting_value=value,
                        description=desc
                    )
                    session.add(setting)
            
            session.commit()
    
    def get_session(self) -> Session:
        """Get database session"""
        return Session(self.engine)
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()

# Global database manager instance
db_manager = DatabaseManager()