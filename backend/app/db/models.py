"""
SQLAlchemy models for Project and Version persistence.
Compatible with SQLite and PostgreSQL.
"""

import json
from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(String(64), nullable=False)
    updated_at = Column(String(64), nullable=False)
    current_version_id = Column(String(64), nullable=True)

    versions = relationship(
        "VersionModel",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="VersionModel.created_at"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "current_version_id": self.current_version_id,
            "versions": [v.to_dict() for v in self.versions]
        }


class VersionModel(Base):
    __tablename__ = "versions"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(
        String(64),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    prompt = Column(Text, nullable=False)
    html_code = Column(Text, nullable=False)
    pages_json = Column(Text, nullable=True)
    is_multi_page = Column(Boolean, default=False)
    version_type = Column(String(32), default="generation")
    created_at = Column(String(64), nullable=False)

    project = relationship("ProjectModel", back_populates="versions")

    def to_dict(self) -> dict:
        pages_data = None
        if self.pages_json:
            try:
                pages_data = json.loads(self.pages_json)
            except Exception:
                pages_data = None

        return {
            "id": self.id,
            "prompt": self.prompt,
            "html_code": self.html_code,
            "pages": pages_data,
            "is_multi_page": bool(self.is_multi_page),
            "version_type": self.version_type or "generation",
            "created_at": self.created_at
        }
