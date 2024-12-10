import datetime
import uuid
from enum import Enum
from typing import List, Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field, field_serializer
from slugify import slugify
from sqlalchemy import UUID, Boolean, Date, DateTime, ForeignKey, Integer, Text
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
    FORTNIGHTLY = "Fortnightly"
    MONTHLY = "Monthly"
    EVERY_6_WEEKS = "Every 6 weeks"
    QUARTERLY = "Quarterly"
    EVERY_6_MONTHS = "Every 6 months"
    ANNUALLY = "Annually"
    EVERY_2_YEARS = "Every 2 years"
    AD_HOC = "Ad hoc"
    UNKNOWN = "Unknown"


class QuestionType(Enum):
    TEXTAREA = "textarea"
    CHOOSE_ONE_FROM_LIST = "choose-one-from-list"
    CHOOSE_ONE_FROM_LIST_OTHER = "choose-one-from-list-other"
    INPUT = "input"
    ADD_TO_A_LIST = "add-to-a-list"
    CHOOSE_MULTIPLE_FROM_LIST = "choose-one-or-more"


class OSDeclarationStatus(Enum):
    UNKNOWN = "Unknown"
    CHECKING_WITH_OS = "Checking with OS"
    FREE_TO_USE = "Free to use"
    PRESUMPTION_TO_PUBLISH = "Presumption to publish"
    EXEMPTION = "Exemption"
    OTHER_LICENCE_NEEDED = "Other licence needed"


consideration_tags = db.Table(
    "consideration_tags",
    db.Column("consideration_id", UUID(as_uuid=True), ForeignKey("consideration.id")),
    db.Column("tag_id", UUID(as_uuid=True), ForeignKey("tag.id")),
)


class DateModel(db.Model):
    __abstract__ = True

    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now
    )
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, onupdate=datetime.datetime.now
    )
    deleted_date: Mapped[Optional[datetime.date]] = mapped_column(Date)


class Consideration(db.Model):
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
    datasets: Mapped[Optional[list]] = mapped_column(MutableList.as_mutable(JSONB))
    specification: Mapped[Optional[dict]] = mapped_column(MutableDict.as_mutable(JSONB))
    useful_links: Mapped[Optional[list]] = mapped_column(MutableList.as_mutable(JSONB))
    legislation: Mapped[Optional[dict]] = mapped_column(MutableDict.as_mutable(JSONB))
    slug: Mapped[Optional[str]] = mapped_column(Text)
    blocked_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    os_declaration: Mapped[Optional[dict]] = mapped_column(
        MutableDict.as_mutable(JSONB)
    )

    answers: Mapped[List["Answer"]] = relationship(back_populates="consideration")
    change_log: Mapped[List["ChangeLog"]] = relationship(
        back_populates="consideration", order_by="asc(ChangeLog.created)"
    )

    is_local_land_charge: Mapped[bool] = mapped_column(Boolean, default=False)
    is_local_plan_data: Mapped[bool] = mapped_column(Boolean, default=False)

    tags: Mapped[List["Tag"]] = relationship(
        secondary="consideration_tags", back_populates="considerations"
    )

    notes: Mapped[List["Note"]] = relationship(
        back_populates="consideration", order_by="asc(Note.created)"
    )

    created: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today)
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, onupdate=datetime.datetime.now
    )
    deleted_date: Mapped[Optional[datetime.date]] = mapped_column(Date)

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
        if isinstance(question, str):
            question = Question.query.filter(Question.slug == question).first()
        answer = next(
            (a for a in self.answers if a.question_slug == question.slug),
            None,
        )
        return answer

    def get_column_type(self, field_name):
        return self.__table__.columns[field_name].type

    def __repr__(self):
        return f"<Consideration {self.name}> <Description {self.description}> <Stage {self.stage}>"


class ChangeLog(db.Model):
    id: Mapped[uuid.uuid4] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    field: Mapped[str] = mapped_column(Text, nullable=False)
    change: Mapped[dict] = mapped_column(JSONB, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    consideration_id: Mapped[uuid.uuid4] = mapped_column(
        UUID(as_uuid=True), ForeignKey("consideration.id")
    )
    consideration: Mapped[Consideration] = relationship(back_populates="change_log")
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now
    )
    user: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self):
        return f"<ChangeLog {self.field}> <from: {self.from_value}> <to: {self.to_value}> <created: {self.created}>"


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


class Performance(db.Model):
    id: Mapped[uuid.uuid4] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    considerations: Mapped[int] = mapped_column(Integer)
    backlog: Mapped[int] = mapped_column(Integer)
    screen: Mapped[int] = mapped_column(Integer)
    research: Mapped[int] = mapped_column(Integer)
    co_design: Mapped[int] = mapped_column(Integer)
    test_and_iterate: Mapped[int] = mapped_column(Integer)
    ready_for_go_no_go: Mapped[int] = mapped_column(Integer)
    prepared_for_platform: Mapped[int] = mapped_column(Integer)
    on_the_platform: Mapped[int] = mapped_column(Integer)
    archived: Mapped[int] = mapped_column(Integer)
    blocked: Mapped[int] = mapped_column(Integer)
    date: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today)

    def indicators(self):
        excluded_fields = ["id", "date"]
        return [
            field
            for field in self.__table__.columns.keys()
            if field not in excluded_fields
        ]


class Tag(db.Model):
    id: Mapped[uuid.uuid4] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(Text, unique=True)
    considerations: Mapped[List[Consideration]] = relationship(
        secondary="consideration_tags", back_populates="tags"
    )


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

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=lambda x: x.replace("_", "-"),
        populate_by_name=True,
    )

    name: str
    description: Optional[str]
    synonyms: Optional[List[str]]
    github_discussion_number: Optional[int] = Field(
        default=None, alias="github-discussion-number"
    )
    stage: Optional[StageModel]
    public: Optional[bool]
    expected_number_of_records: Optional[int] = Field(
        default=None, alias="expected-number-of-records"
    )
    frequency_of_updates: Optional[FrequencyOfUpdatesModel] = Field(
        default=None, alias="frequency-of-updates"
    )
    prioritised: Optional[bool]
    datasets: Optional[list]
    specification_url: Optional[dict] = Field(default=None, alias="specification")
    useful_links: Optional[list] = Field(default=None, alias="useful-links")
    legislation: Optional[dict]
    slug: Optional[str]
    blocked_reason: Optional[str]
    os_declaration: Optional[dict]

    @field_serializer("frequency_of_updates", "stage")
    def serialize_enum(self, field: Enum):
        if field is not None:
            return field.value

    @field_serializer("datasets")
    def serialze_datasets(self, data):
        if data is not None:
            urls = []
            for d in data:
                urls.append(d["schema_url"])
            return ";".join(urls)
        return None

    @field_serializer("legislation", "specification_url")
    def serialize_links(self, data):
        if isinstance(data, dict):
            return data["link_url"]
        if isinstance(data, list):
            urls = []
            for d in data:
                urls.append(d["link_url"])
            return ";".join(urls)
        return None

    @field_serializer("synonyms")
    def serialize_synonyms(self, data):
        if data is not None:
            return ";".join(data)
        return None


class AnswerModel(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    text: str
    consideration_id: UUID4 = Field(exclude=True)
    question_slug: str


class PerformanceModel(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    considerations: int
    backlog: int
    screen: int
    research: int
    co_design: int
    test_and_iterate: int
    ready_for_go_no_go: int
    prepared_for_platform: int
    on_the_platform: int
    archived: int
    blocked: int
    date: datetime.datetime

    @field_serializer("date")
    def serialize_date(self, value):
        return value.strftime("%Y-%m-%d")
