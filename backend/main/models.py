import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, computed_field, field_serializer, field_validator, Field
from .utils import parse_date, parse_timestamp, uuid_gen
from sqlalchemy import CheckConstraint, ForeignKey, Numeric
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from dateutil.parser import parse
from sqlalchemy.orm import validates
import validators

schema = "convoy"


class Base(DeclarativeBase):
    pass


class MeterReading(Base):
    __tablename__ = "meter_reading"
    id: Mapped[str] = mapped_column(primary_key=True, default=uuid_gen)
    value: Mapped[float] = mapped_column(Numeric())
    timestamp: Mapped[datetime.datetime] = mapped_column(default=lambda: datetime.datetime.now())
    machine_id: Mapped[str] = mapped_column(ForeignKey("machine.id"))
    machine: Mapped["Machine"] = relationship(back_populates="meter_readings", lazy="joined")

    __table_args__ = (CheckConstraint("value > 0", name="check_value_positive"), {})

    @classmethod
    def from_schema(cls, schema: "MeterReadingSchema"):
        return MeterReading(**schema.model_dump())


class Part(Base):
    __tablename__ = "part"

    id: Mapped[str] = mapped_column(primary_key=True, default=uuid_gen)
    name: Mapped[str] = mapped_column(String())
    link: Mapped[Optional[str]] = mapped_column(String(), nullable=True)
    supply_id: Mapped[str] = mapped_column(ForeignKey("supply.id"))
    supply: Mapped["Supply"] = relationship(back_populates="parts", lazy="joined")

    @validates("link")
    def validate_link(self, key, link):
        return validators.url(link)


class Supply(Base):
    __tablename__ = "supply"

    id: Mapped[str] = mapped_column(primary_key=True, default=uuid_gen)
    name: Mapped[str] = mapped_column(String())
    unit: Mapped[str] = mapped_column(String())
    quantity_on_hand: Mapped[float] = mapped_column(Numeric(), default=0)
    parts: Mapped[List[Part]] = relationship(back_populates="supply", lazy="joined", cascade="all, delete-orphan")
    machine_id: Mapped[Optional[str]] = mapped_column(ForeignKey("machine.id"))
    machine: Mapped["Machine"] = relationship(back_populates="supplies", lazy="joined")
    task_supplies: Mapped[List["TaskSupply"]] = relationship(back_populates="supply", lazy="joined", cascade="all, delete-orphan")
    __table_args__ = (CheckConstraint("quantity_on_hand >= 0", name="check_quantity_positive"), {})

    @classmethod
    def from_schema(cls, schema: "SupplySchema") -> "Supply":
        d = schema.model_dump()
        return Supply(**d)


class TaskSupply(Base):
    __tablename__ = "task_supply"

    id: Mapped[str] = mapped_column(primary_key=True, default=uuid_gen)
    quantity_required: Mapped[float] = mapped_column(Numeric(), default=0)
    supply_id: Mapped[str] = mapped_column(ForeignKey("supply.id"))
    supply: Mapped["Supply"] = relationship(back_populates="task_supplies", lazy="joined")
    task_id: Mapped[str] = mapped_column(ForeignKey("task.id"))
    task: Mapped["Task"] = relationship(back_populates="task_supplies", lazy="joined")
    machine_id: Mapped[Optional[str]] = mapped_column(ForeignKey("machine.id"))
    machine: Mapped["Machine"] = relationship(back_populates="task_supplies", lazy="joined")
    __table_args__ = (CheckConstraint("quantity_required > 0", name="check_quantity_positive"), {})


class Task(Base):
    __tablename__ = "task"

    id: Mapped[str] = mapped_column(primary_key=True, default=uuid_gen)
    description: Mapped[str]
    time_interval: Mapped[int]  # days
    meter_interval: Mapped[float]
    recurring: Mapped[bool] = mapped_column(default=False)
    notes: Mapped[Optional[str]] = mapped_column(String())
    task_supplies: Mapped[List["TaskSupply"]] = relationship(back_populates="task", lazy="joined", cascade="all, delete-orphan")
    completed: Mapped[bool] = mapped_column(default=False)
    completed_date: Mapped[Optional[datetime.date]] = None
    completed_meter_reading: Mapped[Optional[float]] = None
    due_date: Mapped[datetime.date]
    due_meter_reading: Mapped[float]
    todoist_task_id: Mapped[Optional[str]] = mapped_column(default=None)
    machine_id: Mapped[str] = mapped_column(ForeignKey("machine.id"))
    machine: Mapped["Machine"] = relationship(
        back_populates="tasks",
        lazy="joined",
    )
    task_supplies: Mapped[List["TaskSupply"]] = relationship(back_populates="task", lazy="joined", cascade="all, delete-orphan")
    __table_args__ = (
        CheckConstraint("time_interval > 0", name="check_time_positive"),
        CheckConstraint("meter_interval > 0", name="check_meter_positive"),
        {},
    )

    @classmethod
    def from_schema(cls, schema: BaseModel) -> "Task":
        d = schema.model_dump(exclude=["supplies", "initial_due_meter", "initial_due_date"])
        return Task(**d)


class Machine(Base):
    __tablename__ = "machine"
    id: Mapped[str] = mapped_column(primary_key=True, default=uuid_gen)
    vin: Mapped[Optional[str]] = None
    meter_unit: Mapped[str]
    make: Mapped[str]
    model: Mapped[str]
    year: Mapped[int]
    image: Mapped[Optional[str]] = None
    purchase_date: Mapped[Optional[datetime.date]] = None
    meter_readings: Mapped[List[MeterReading]] = relationship(back_populates="machine", lazy="joined", cascade="all, delete-orphan")
    tasks: Mapped[List["Task"]] = relationship(back_populates="machine", lazy="joined", cascade="all, delete-orphan")
    task_supplies: Mapped[List["TaskSupply"]] = relationship(back_populates="machine", lazy="joined", cascade="all, delete-orphan")
    supplies: Mapped[List["Supply"]] = relationship(back_populates="machine", lazy="joined", cascade="all, delete-orphan")

    @classmethod
    def from_schema(cls, schema: "MachineSchema") -> "Machine":
        d = schema.model_dump(exclude=["current_meter_reading", "name"])
        d["purchase_date"] = parse(d["purchase_date"]).date()
        return Machine(**d)


class MeterReadingSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    value: float = Field()
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now())
    machine_id: Optional[str] = None
    normalize_date = field_validator("timestamp", mode="before")(parse_timestamp)


class PartSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=uuid_gen)
    name: str = Field()
    link: Optional[str] = Field()
    supply_id: Optional[str] = None
    supply: Optional["SupplySchema"] = None


class SupplySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=uuid_gen)
    name: str = Field()
    unit: str = Field()
    quantity_on_hand: float = Field()
    parts: List[PartSchema] = []
    machine_id: Optional[str] = None
    task_supplies: List["TaskSupplySchema"] = Field(default=[])


class SupplyUpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: Optional[str] = Field(default=None)
    unit: Optional[str] = Field(default=None)
    quantity_on_hand: Optional[float] = Field()
    parts: Optional[List[PartSchema]] = Field(default=[])
    machine_id: Optional[str] = Field(default=None)
    task_supplies: List["TaskSupplySchema"] = Field(default=[])


class TaskSupplySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=uuid_gen)
    quantity_required: float = Field()
    supply_id: str = Field()
    supply: "SupplySchema"
    task_id: str = Field()
    task: "TaskSchema"


class TaskSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=uuid_gen)

    description: str
    time_interval: int  # days
    meter_interval: float
    recurring: bool = Field(default=False)
    notes: Optional[str] = Field()
    completed: bool = Field(default=False)
    completed_date: Optional[datetime.date] = Field(default=None)
    completed_meter_reading: Optional[float] = Field(default=None)
    due_date: datetime.date
    due_meter_reading: float
    normalize_date = field_validator("completed_date", mode="before")(parse_date)
    normalize_date2 = field_validator("due_date", mode="before")(parse_date)
    todoist_task_id: Optional[str] = Field(default=None)
    machine_id: str = Field()
    task_supplies: List["TaskSupplySchema"] = []

    @field_serializer("due_date")
    def serialize_dt(self, dt: datetime.date, _info):
        if dt:
            return dt.strftime("%m/%d/%Y")

    @field_serializer("completed_date")
    def serialize_dt2(self, dt: datetime.date, _info):
        if dt:
            return dt.strftime("%m/%d/%Y")
        else:
            return None

    # @computed_field
    # @property
    # def due_meter_ago(self) -> float:
    #     return self.machine.current_meter_reading - self.due_meter_reading

    @computed_field
    @property
    def due_days_ago(self) -> int:
        return (datetime.date.today() - self.due_date).days or 0


class TaskCompleteSchema(BaseModel):
    notes: Optional[str] = None
    completed_date: datetime.date
    completed_meter_reading: float
    normalize_date = field_validator("completed_date", mode="before")(parse_date)

    @field_serializer("completed_date")
    def serialize_dt2(self, dt: datetime.date, _info):
        if dt:
            return dt.strftime("%m/%d/%Y")


class TaskCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    supplies: List[str] = []
    normalize_date = field_validator("due_date", mode="before")(parse_date)
    description: str
    time_interval: int  # days
    meter_interval: float
    recurring: bool
    notes: Optional[str] = None
    due_date: Optional[datetime.date]
    due_meter_reading: Optional[float]


class MachineSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=uuid_gen)
    vin: Optional[str] = None
    meter_unit: str
    make: str
    model: str
    year: int
    image: Optional[str] = None
    purchase_date: Optional[datetime.date] = None
    meter_readings: Optional[List[MeterReadingSchema]] = []
    tasks: Optional[List["TaskSchema"]] = []

    normalize_date = field_validator("purchase_date", mode="before")(parse_date)

    @field_serializer("purchase_date")
    def serialize_dt(self, dt: datetime.date, _info):
        if dt:
            return dt.strftime("%m/%d/%Y")

    @computed_field
    @property
    def current_meter_reading(self) -> float:
        if len(self.meter_readings) > 0:
            return sorted(self.meter_readings, key=lambda x: x.timestamp)[0].value
        else:
            return 0

    @computed_field
    @property
    def name(self) -> str:
        return f"{self.year} {self.make} {self.model}"


class MachineUpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    vin: Optional[str] = None
    meter_unit: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    image: Optional[str] = None
    purchase_date: Optional[datetime.date] = None
    normalize_date = field_validator("purchase_date", mode="before")(parse_date)
