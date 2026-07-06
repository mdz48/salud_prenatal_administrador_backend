from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.features.admin.infrastructure.models.report_model import ReportModel
from app.features.admin.infrastructure.models.user_model import Usuario

class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_reports(self) -> List[Dict[str, Any]]:
        results = self.db.query(ReportModel, Usuario).join(
            Usuario, ReportModel.reporter_id == Usuario.user_id
        ).all()
        
        return self._format_results(results)

    def get_reports_by_user_id(self, user_id: int) -> List[Dict[str, Any]]:
        results = self.db.query(ReportModel, Usuario).join(
            Usuario, ReportModel.reporter_id == Usuario.user_id
        ).filter(ReportModel.reporter_id == user_id).all()
        
        return self._format_results(results)

    def _format_results(self, results) -> List[Dict[str, Any]]:
        formatted_reports = []
        for report, user in results:
            formatted_reports.append({
                "report_id": report.report_id,
                "post_id": report.post_id,
                "comment_id": report.comment_id,
                "reason": report.reason,
                "created_at": report.created_at,
                "reporter": {
                    "id": user.user_id,
                    "nombre_completo": f"{user.name} {user.last_name}",
                    "rol": user.role.value if hasattr(user.role, 'value') else str(user.role),
                    "correo": user.email
                }
            })
        return formatted_reports
