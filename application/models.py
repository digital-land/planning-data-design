import datetime
import uuid
from enum import Enum
from typing import List, Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field
from slugify import slugify
from sqlalchemy import UUID, Boolean, Date, DateTime, ForeignKey, Integer, Text, event
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, attributes, mapped_column, relationship

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
    ADD_TO_A_LIST = "add-to-a-list"
    CHOOSE_MULTIPLE_FROM_LIST = "choose-one-or-more"


class DateModel(db.Model):
    __abstract__ = True

    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now
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

    is_local_land_charge: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[List["Note"]] = relationship(
        back_populates="consideration", order_by="asc(Note.created)"
    )

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
            None,
        )
        return answer

    def get_column_type(self, field_name):
        return self.__table__.columns[field_name].type

    def __repr__(self):
        return f"<Consideration {self.name}> <Description {self.description}> <Stage {self.stage}>"


@event.listens_for(Consideration, "before_update")
def receive_before_update(mapper, connection, target):
    from flask import session

    from application.extensions import db

    attr_to_model = {
        "stage": StageModel,
        "answers": AnswerModel,
        "frequency_of_updates": FrequencyOfUpdatesModel,
    }

    try:
        state = db.inspect(target)
        for attr in state.attrs:
            if attr.key not in ["id", "changes", "udpated", "deleted_date", "notes"]:
                history = attr.load_history()
                if history.has_changes():
                    log = {
                        "field": attr.key,
                        "added": history.added[0] if history.added else "",
                        "deleted": history.deleted[0] if history.deleted else "",
                        "user": session.get("username"),
                        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    }
                    if attr.key in attr_to_model.keys():
                        log["added"] = attr_to_model[attr.key](
                            value=log["added"]
                        ).dict()
                        log["deleted"] = attr_to_model[attr.key](
                            value=log["deleted"]
                        ).dict()
                    if target.changes is None:
                        target.changes = []
                    target.changes.append(log)
    except Exception as e:
        print(e)
        print("Error logging changes")


class Answer(DateModel):
    id: Mapped[uuid.uuid4] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    answer: Mapped[Optional[dict]] = mapped_column(MutableDict.as_mutable(JSONB))
    answer_list: Mapped[Optional[list]] = mapped_column(MutableList.as_mutable(JSONB))
    consideration_id: Mapped[uuid.uuid4] = mapped_column(
        UUID(as_uuid=True), ForeignKey("consideration.id")
    )
    consideration: Mapped[Consideration] = relationship(back_populates="answers")
    question_slug: Mapped[str] = mapped_column(Text, ForeignKey("question.slug"))
    question: Mapped["Question"] = relationship(lazy=True)

    def add_to_list(self, data):
        if self.answer_list is None:
            self.answer_list = []
        position = int(data.get("position", 0))
        if position < len(self.answer_list):
            d = self.answer_list[position]
            for key, value in data.items():
                d[key] = value
        else:
            self.answer_list.append(data)

    def update_list(self, position, data):
        for key, value in data.items():
            self.answer_list[position][key] = value
        attributes.flag_modified(self, "answer_list")

    def __repr__(self):
        return f"<Answer {self.answer}>"


class Question(DateModel):
    slug: Mapped[str] = mapped_column(Text, primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    stage: Mapped[Stage] = mapped_column(ENUM(Stage))
    question_type: Mapped[QuestionType] = mapped_column(ENUM(QuestionType))
    hint: Mapped[Optional[str]] = mapped_column(Text)
    python_form: Mapped[Optional[str]] = mapped_column(Text)

    next: Mapped[Optional[str]] = mapped_column(MutableDict.as_mutable(JSONB))
    previous: Mapped[Optional[str]] = mapped_column(Text)

    choices: Mapped[Optional[list[str]]] = mapped_column(
        MutableList.as_mutable(ARRAY(Text))
    )
    order: Mapped[Optional[int]] = mapped_column(Integer)

    def format(self, consideration_name):
        if "{name}" in self.text:
            return self.text.format(name=consideration_name)
        return self.text

    def __repr__(self):
        return f"<Question {self.text}> <Stage {self.stage}>"


class Note(DateModel):

    id: Mapped[uuid.uuid4] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    text: Mapped[str] = mapped_column(Text)
    consideration_id: Mapped[uuid.uuid4] = mapped_column(
        UUID(as_uuid=True), ForeignKey("consideration.id")
    )
    consideration: Mapped[Consideration] = relationship(back_populates="notes")
    author: Mapped[str] = mapped_column(Text)

    def __repr__(self):
        return f"<Note {self.text}>"


# pydantic models


class StageModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    value: str


class FrequencyOfUpdatesModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    value: str


class ConsiderationModel(BaseModel):

    model_config = ConfigDict(from_attributes=True)

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


class AnswerModel(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    text: str
    consideration_id: UUID4 = Field(exclude=True)
    question_slug: str
