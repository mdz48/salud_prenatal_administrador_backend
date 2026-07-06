from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
from app.features.admin.infrastructure.models.user_model import Usuario

class ReportModel(Base):
    __tablename__ = "reports"

    report_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reporter_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    post_id = Column(Integer, nullable=True, index=True)
    comment_id = Column(Integer, nullable=True, index=True)
    reason = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
