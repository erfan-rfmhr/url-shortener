from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

__all__ = ["Link", "Visit"]


class Link(SQLModel, table=True):
    """Link model representing shortened URLs."""

    id: int = Field(primary_key=True)
    target: str = Field(..., description="The target URL to redirect to")
    code: str = Field(
        ..., unique=True, index=True, description="Short code for the URL"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="When the link was created",
    )

    # Relationship to visits
    visits: list["Visit"] = Relationship(back_populates="link")


class Visit(SQLModel, table=True):
    """Visit model tracking link visits."""

    id: int = Field(primary_key=True)
    link_id: int = Field(
        ..., foreign_key="link.id", description="Foreign key to the link"
    )
    utm: str | None = Field(default=None, description="UTM parameters for tracking")
    visited_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="When the visit occurred",
    )

    # Relationship to link
    link: Link = Relationship(back_populates="visits")
