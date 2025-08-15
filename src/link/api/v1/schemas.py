from sqlmodel import SQLModel


class TargetUrl(SQLModel):
    target_url: str


class ShortenedUrl(SQLModel):
    shortened_url: str
    target_url: str


class UrlStats(SQLModel):
    short_code: str
    target_url: str
    visit_count: int
    created_at: str
