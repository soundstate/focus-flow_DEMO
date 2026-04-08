from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from game_engine.database.connection import Base


class XPHistory(Base):
    __tablename__ = "ge_xp_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    base_xp = Column(Integer, nullable=False)
    bonus_xp = Column(Integer, default=0)
    total_xp = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
