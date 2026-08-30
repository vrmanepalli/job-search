from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    Text,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)

    job_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255))

    job_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="saved",
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    applied_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(255)
    )

    resume_text: Mapped[str] = mapped_column(
        Text
    )

    is_master: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

class ResumeOptimization(Base):
    __tablename__ = "resume_optimizations"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    job_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    company: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    original_resume: Mapped[str] = mapped_column(
        Text
    )

    job_description: Mapped[str] = mapped_column(
        Text
    )

    optimized_resume: Mapped[str] = mapped_column(
        Text
    )

    match_score: Mapped[int] = mapped_column(
        Integer
    )

    # NEW
    validation_passed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # NEW
    validation_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # NEW
    validation_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # NEW
    validation_issues_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)

    external_job_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    company: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    job_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        default="linkedin",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )