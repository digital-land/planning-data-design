import datetime
import uuid
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel
from slugify import slugify
from sqlalchemy import UUID, Boolean, Date, DateTime, ForeignKey, Integer, Text, event
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

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


class QuestionType(Enum):
    TEXTAREA = "textarea"
    CHOOSE_ONE_FROM_LIST = "choose-one-from-list"
    CHOOSE_ONE_FROM_LIST_OTHER = "choose-one-from-list-other"
    INPUT = "input"


class DateModel(db.Model):
    __abstract__ = True

    created: Mapped[datetime.date] = mapped_column(
        Date, default=datetime.datetime.today
    )
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, onupdate=datetime.datetime.now
    )
    deleted_date: Mapped[Optional[datetime.date]] = mapped_column(Date)


class Consideration(DateModel):
    id: Mapped[uuid.uuid4] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(Text, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    synonyms: Mapped[Optional[list[str]]] = mapped_column(
        MutableList.as_mutable(ARRAY(Text))
    )
    github_discussion_number: Mapped[Optional[int]] = mapped_column(Integer)
    stage: Mapped[Stage] = mapped_column(ENUM(Stage))
    public: Mapped[bool] = mapped_column(Boolean, default=True)

    expected_number_of_records: Mapped[Optional[int]] = mapped_column(Integer)
    frequency_of_updates: Mapped[Optional[FrequencyOfUpdates]] = mapped_column(
        ENUM(FrequencyOfUpdates)
    )
    prioritised: Mapped[bool] = mapped_column(Boolean, default=False)
    schemas: Mapped[Optional[list]] = mapped_column(MutableList.as_mutable(JSONB))
    specification: Mapped[Optional[dict]] = mapped_column(MutableDict.as_mutable(JSONB))
    useful_links: Mapped[Optional[list]] = mapped_column(MutableList.as_mutable(JSONB))
    legislation: Mapped[Optional[dict]] = mapped_column(MutableDict.as_mutable(JSONB))
    slug: Mapped[Optional[str]] = mapped_column(Text)

    answers: Mapped[List["Answer"]] = relationship(back_populates="consideration")

    changes: Mapped[Optional[list]] = mapped_column(MutableList.as_mutable(JSONB))

    def delete(self):
        self.deleted_date = datetime.date.today()
        db.session.add(self)
        db.session.commit()

    def set_slug(self):
        if self.name is not None:
            name_part = self.name.split("(")[0]
            slug = slugify(name_part)
            self.slug = slug

    def get_answer(self, question):
        answer = next(
            (a for a in self.answers if a.question_slug == question.slug),
            "Not anwsered yet",
        )
        return answer

    def __repr__(self):
        return f"<Consideration {self.name}> <Description {self.description}> <Stage {self.stage}>"


# @event.listens_for(Consideration, "before_update")
# def receive_before_update(mapper, connection, target):
#     from flask import session

#     from application.extensions import db

#     modifications = {}
#     state = db.inspect(target)
#     for attr in state.attrs:
#         if attr.key not in ["stage", "changes"]:
#             history = attr.load_history()
#             if history.has_changes():
#                 c = {}
#                 if history.added:
#                     c["added"] = history.added
#                 if history.deleted:
#                     c["deleted"] = history.deleted
#                 modifications[attr.key] = c

#     if modifications:
#         if target.changes is None:
#             target.changes = []

#         user_name = session.get("user", {}).get("name", None)
#         log = {
#             "user": user_name,
#             "date": datetime.datetime.today().strftime("%Y-%m-%d"),
#             "changes": modifications,
#         }
#         target.changes.append(log)


@event.listens_for(Consideration, "before_insert")
def receive_before_insert(mapper, connection, target):
    print("before_insert")


class Answer(DateModel):
    id: Mapped[uuid.uuid4] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    text: Mapped[str] = mapped_column(Text)

    consideration_id: Mapped[uuid.uuid4] = mapped_column(
        UUID(as_uuid=True), ForeignKey("consideration.id")
    )
    consideration: Mapped[Consideration] = relationship(back_populates="answers")

    question_slug: Mapped[str] = mapped_column(Text, ForeignKey("question.slug"))

    question: Mapped["Question"] = relationship(lazy=True)

    def __repr__(self):
        return f"<Answer {self.text}>"


class Question(DateModel):
    slug: Mapped[str] = mapped_column(Text, primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    stage: Mapped[Stage] = mapped_column(ENUM(Stage))
    question_type: Mapped[QuestionType] = mapped_column(ENUM(QuestionType))
    hint: Mapped[Optional[str]] = mapped_column(Text)

    # could make this self referential keys
    next: Mapped[Optional[str]] = mapped_column(Text)
    previous: Mapped[Optional[str]] = mapped_column(Text)

    choices: Mapped[Optional[list[str]]] = mapped_column(
        MutableList.as_mutable(ARRAY(Text))
    )

    def format(self, consideration_name):
        if "{name}" in self.text:
            return self.text.format(name=consideration_name)
        return self.text

    def __repr__(self):
        return f"<Question {self.text}> <Stage {self.stage}>"


# pydantic models


class StageModel(BaseModel):
    name: str
    value: str

    class Config:
        from_attributes = True


class FrequencyOfUpdatesModel(BaseModel):
    name: str
    value: str

    class Config:
        from_attributes = True


class ConsiderationModel(BaseModel):
    name: str
    description: Optional[str]
    synonyms: Optional[List[str]]
    github_discussion_number: Optional[int]
    stage: StageModel
    public: bool
    expected_number_of_records: Optional[int]
    frequency_of_updates: Optional[FrequencyOfUpdatesModel]
    prioritised: bool
    schemas: Optional[list]
    specification_url: Optional[dict]
    useful_links: Optional[list]
    legislation: Optional[dict]
    slug: Optional[str]

    class Config:
        from_attributes = True
