from app.features.admin.infrastructure.repositories.report_repository import ReportRepository

class GetUserReportsUseCase:
    def __init__(self, report_repository: ReportRepository):
        self.report_repository = report_repository

    def execute(self, user_id: int):
        return self.report_repository.get_reports_by_user_id(user_id)
