import datetime
import uuid
from enum import Enum
from typing import Optional

from slugify import slugify
from sqlalchemy import UUID
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column

from application.extensions import db


class Stage(Enum):
    BACKLOG = "Backlog"
    SCREEN = "Screen"
    RESEARCH = "Research"
    CO_DESIGN = "Co-design"
    TEST_AND_ITERATE = "Test and iterate"
    READY_FOR_GO_NO_GO = "Ready for go/no-go"
    PREPARED_FOR_PLATFORM = "Prepared for platform"
    ON_THE_PLATFORM = "On the platform"
    ARCHIVED = "Archived"


class FrequencyOfUpdates(Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    ANNUALLY = "Annually"
    AD_HOC = "Ad hoc"


class DateModel(db.Model):
    __abstract__ = True

    created: Mapped[datetime.date] = mapped_column(
        db.Date, default=datetime.datetime.today
    )
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(
        db.DateTime, onupdate=datetime.datetime.now
    )


class Consideration(DateModel):
    id: Mapped[uuid.uuid4] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(db.Text, unique=True)
    description: Mapped[Optional[str]] = mapped_column(db.Text)
    synonyms: Mapped[Optional[list[str]]] = mapped_column(ARRAY(db.Text))
    github_discussion_number: Mapped[Optional[int]] = mapped_column(db.Integer)
    stage: Mapped[Stage] = mapped_column(ENUM(Stage))
    public: Mapped[bool] = mapped_column(db.Boolean, default=True)

    expected_number_of_records: Mapped[Optional[int]] = mapped_column(db.Integer)
    frequency_of_updates: Mapped[Optional[FrequencyOfUpdates]] = mapped_column(
        ENUM(FrequencyOfUpdates)
    )
    prioritised: Mapped[bool] = mapped_column(db.Boolean, default=False)
    schemas: Mapped[Optional[list]] = mapped_column(MutableList.as_mutable(JSONB))
    specification_url: Mapped[Optional[dict]] = mapped_column(
        MutableDict.as_mutable(JSONB)
    )
    useful_links: Mapped[Optional[list]] = mapped_column(MutableList.as_mutable(JSONB))
    legislation: Mapped[Optional[dict]] = mapped_column(MutableDict.as_mutable(JSONB))
    slug: Mapped[Optional[str]] = mapped_column(db.Text)

    def set_slug(self):
        if self.name is not None:
            name_part = self.name.split("(")[0]
            slug = slugify(name_part)
            self.slug = slug

    def __repr__(self):
        return f"<Consideration {self.name}> <Description {self.description}> <Stage {self.stage}>"
