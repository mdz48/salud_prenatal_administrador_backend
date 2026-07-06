from app.features.admin.infrastructure.repositories.report_repository import ReportRepository

class GetAllReportsUseCase:
    def __init__(self, report_repository: ReportRepository):
        self.report_repository = report_repository

    def execute(self):
        return self.report_repository.get_all_reports()
