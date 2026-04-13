from datetime import datetime

from pydantic import BaseModel, Field


class ResearchDocument(BaseModel):
    """
    Represents raw, ingested research material.
    """

    source_url: str
    title: str
    raw_content: str
    ingested_at: datetime = Field(default_factory=datetime.now)


class WikiArticle(BaseModel):
    """
    Represents a synthesized, structured concept article maintained by the LLM.
    """

    title: str
    summary: str
    content: str
    sources: list[str] = Field(default_factory=list)
    backlinks: list[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)


class WikiIndex(BaseModel):
    """
    The central navigation file for the LLM.
    """

    entities: list[str] = Field(default_factory=list)
    last_linted: datetime | None = None
