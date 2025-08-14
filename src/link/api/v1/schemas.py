from sqlmodel import SQLModel


class TargetUrl(SQLModel):
    target_url: str


class ShortenedUrl(SQLModel):
    shortened_url: str
    target_url: str
