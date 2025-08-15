from sqlmodel import SQLModel


class TargetUrl(SQLModel):
    target_url: str


class ShortenedUrl(SQLModel):
    shortened_url: str
    target_url: str


class UrlStats(SQLModel):
    short_url: str
    target_url: str
    visits_count: int
    created_at: str
