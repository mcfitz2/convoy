import enum
from pydantic import BaseModel, ConfigDict, Field, computed_field, validator
from dateutil.parser import parse

import datetime
from typing import Optional, List
from sqlmodel import select

from models import Machine, MeterReading, Part, Supply, TaskDefinition
from utils import get_session, uuid_gen


class MeterReadingSchema(BaseModel):
    id: str = Field(default_factory=uuid_gen, primary_key=True)
    value: float
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now())
    machine_id: str | None
    machine: "Machine"


class SupplySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str = Field(default_factory=uuid_gen, primary_key=True)
    name: str
    unit: str
    quantity_on_hand: float = 0
    parts: List[Part] = []
    machine_id: str | None = None


class TaskSupplySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    quantity: float = 0
    supply_id: str
    supply: "Supply"


class AssignedTaskSupplySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    quantity: float = 0
    supply_id: str


class TaskDefinitionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    description: str
    time_interval: int  # days
    meter_interval: float
    recurring: Optional[bool] = False
    notes: Optional[str] = None
    machine_id: str | None
    supplies: list["TaskSupplySchema"]


class CreateTaskDefinitionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    description: str
    time_interval: int  # days
    meter_interval: float
    recurring: Optional[bool] = False
    notes: Optional[str] = None
    machine_id: str | None
    initial_due_meter: Optional[float] = None
    initial_due_date: Optional[datetime.date] = None

    @validator("initial_due_date", pre=True)
    def parse_date(cls, value):
        if not value:
            return value
        if isinstance(value, datetime.datetime):
            return value.date()
        elif isinstance(value, datetime.date):
            return value
        else:
            return parse(value)


class TaskSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=uuid_gen, primary_key=True)
    completed: bool = False
    completed_date: Optional[datetime.date] = None

    completed_meter_reading: Optional[float] = None
    due_date: datetime.date
    due_meter_reading: float = None
    notes: Optional[str] = None
    task_definition_id: str | None
    task_definition: TaskDefinitionSchema | None
    machine_id: str | None
    machine: "Machine"

    @validator("completed_date", pre=True)
    def parse_date(cls, value):
        if not value:
            return value
        if isinstance(value, datetime.date):
            return value
        elif isinstance(value, datetime.datetime):
            return value.date()
        else:
            return parse(value)

    @computed_field
    @property
    def due_meter_ago(self) -> float:
        try:
            if self.completed:
                return self.completed_meter_reading - self.due_meter_reading
            else:
                session = get_session()
                meter_reading = session.exec(
                    select(MeterReading).where(MeterReading.machine_id == self.machine_id).order_by(MeterReading.timestamp.desc())
                ).first()
                return meter_reading.value - self.due_meter_reading
        except AttributeError:
            return 0

    @computed_field
    @property
    def due_days_ago(self) -> float:
        return (datetime.date.today() - self.due_date).days or 0

    @computed_field
    @property
    def overdue_reason(self) -> str:
        time_bool = self.due_days_ago >= 0
        meter_bool = self.due_meter_ago >= 0
        if time_bool and meter_bool:
            return "BOTH"
        elif time_bool:
            return "TIME"
        elif meter_bool:
            return "METER"
        else:
            return None


class CompleteTaskSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    completed: bool = True
    completed_date: datetime.date
    completed_meter_reading: float
    notes: Optional[str] = None

    @validator("completed_date", pre=True)
    def parse_date(cls, value):
        if not value:
            return value
        if isinstance(value, datetime.datetime):
            return value.date()
        elif isinstance(value, datetime.date):
            return value
        else:
            return parse(value)


class CreateMachineSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    make: str
    model: str
    year: int
    image: Optional[str] = None
    meter_unit: str


class MachineSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    make: str
    model: str
    year: int
    image: Optional[str] = None
    meter_unit: str
    meter_readings: List["MeterReading"]
    task_definitions: List["TaskDefinition"]
    tasks: List["TaskSchema"]

    @computed_field
    @property
    def current_meter_reading(self) -> Optional[float]:
        try:
            session = get_session()
            meter_reading = session.exec(
                select(MeterReading).where(MeterReading.machine_id == self.id).order_by(MeterReading.timestamp.desc())
            ).first()
            return meter_reading.value
        except AttributeError:
            return 0

    @computed_field
    @property
    def name(self) -> int:
        return f"{self.year} {self.make} {self.model}"


class Status(str, enum.Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class APIResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    message: str
    status: Status
