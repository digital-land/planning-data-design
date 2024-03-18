import datetime
import uuid
from enum import Enum
from typing import Optional

from sqlalchemy import UUID
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, JSONB
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
    name: Mapped[str] = mapped_column(db.Text)
    description: Mapped[Optional[str]] = mapped_column(db.Text)
    synonyms: Mapped[Optional[list[str]]] = mapped_column(ARRAY(db.Text))
    github_discssion_number: Mapped[Optional[int]] = mapped_column(db.Integer)
    stage: Mapped[Stage] = mapped_column(ENUM(Stage))
    public: Mapped[bool] = mapped_column(db.Boolean, default=True)

    expected_number_of_records: Mapped[Optional[int]] = mapped_column(db.Integer)
    frequency_of_updates: Mapped[Optional[FrequencyOfUpdates]] = mapped_column(
        ENUM(FrequencyOfUpdates)
    )
    prioritised: Mapped[bool] = mapped_column(db.Boolean, default=False)
    schemas: Mapped[Optional[list[str]]] = mapped_column(ARRAY(db.Text))
    specification_url: Mapped[Optional[str]] = mapped_column(db.Text)
    useful_links: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    legislation: Mapped[Optional[str]] = mapped_column(db.Text)

    def __repr__(self):
        return f"<Consideration {self.name}> <Description {self.description}> <Stage {self.stage}>"
