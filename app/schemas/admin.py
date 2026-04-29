from pydantic import BaseModel


class AdminUserStatusUpdate(BaseModel):
    is_active: bool


class DashboardSummaryResponse(BaseModel):
    total_docs: int
    total_chunks: int
    questions_asked_today: int
    most_searched_topics: list[str]
    active_users: int
