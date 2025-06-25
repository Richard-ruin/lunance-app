from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from app.models.base import PyObjectId


class DailyLog(BaseModel):
    date: datetime
    amount_saved: float
    notes: Optional[str] = None


class Participant(BaseModel):
    student_id: PyObjectId
    joined_date: datetime
    current_progress: float = 0.0
    status: str = "active"  # active, completed, failed
    daily_log: List[DailyLog] = Field(default_factory=list)


class Rewards(BaseModel):
    completion_points: int = 0
    badges: List[str] = Field(default_factory=list)
    leaderboard_recognition: bool = False


class SavingsChallenge(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    # Challenge Info
    name: str
    description: str
    type: str  # daily_save, expense_reduction, goal_based
    
    # Challenge Parameters
    duration_days: int
    target_amount: float
    daily_target: float
    
    # Participation
    participants: List[Participant] = Field(default_factory=list)
    
    # Challenge Settings
    is_public: bool = True
    max_participants: Optional[int] = None
    start_date: datetime
    end_date: datetime
    
    # Rewards
    rewards: Rewards = Field(default_factory=Rewards)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: PyObjectId


class SavingsChallengeInDB(SavingsChallenge):
    pass


class SavingsChallengeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[float] = None
    daily_target: Optional[float] = None
    is_public: Optional[bool] = None
    max_participants: Optional[int] = None


class JoinChallengeRequest(BaseModel):
    student_id: PyObjectId


class LogProgressRequest(BaseModel):
    challenge_id: PyObjectId
    amount_saved: float
    notes: Optional[str] = None