import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from utils import uuid_gen


class Part(SQLModel, table=True):
    id: str = Field(default_factory=uuid_gen, primary_key=True)
    name: str
    link: Optional[str] = None
    supply_id: str = Field(default=None, foreign_key="supply.id")
    supply: "Supply" = Relationship()


class Supply(SQLModel, table=True):
    id: str = Field(default_factory=uuid_gen, primary_key=True)
    name: str = Field(unique=True)
    unit: str
    quantity_on_hand: float = 0
    parts: List[Part] = Relationship(back_populates="supply", cascade_delete=True)
    machine_id: str | None = Field(default=None, foreign_key="machine.id")


class TaskSupply(SQLModel, table=True):
    id: str = Field(default_factory=uuid_gen, primary_key=True)
    quantity: float = 0
    task_definition_id: str | None = Field(default=None, foreign_key="taskdefinition.id")
    task_definition: "TaskDefinition" = Relationship(back_populates="supplies")
    supply_id: str | None = Field(default=None, foreign_key="supply.id")
    supply: "Supply" = Relationship()


class MeterReading(SQLModel, table=True):
    id: str = Field(default_factory=uuid_gen, primary_key=True)
    value: float
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now())
    machine_id: str | None = Field(default=None, foreign_key="machine.id")
    machine: "Machine" = Relationship(back_populates="meter_readings")


class TaskDefinition(SQLModel, table=True):
    id: str = Field(default_factory=uuid_gen, primary_key=True)
    description: str
    time_interval: int  # days
    meter_interval: float
    recurring: Optional[bool] = False
    notes: Optional[str] = None
    tasks: list["Task"] = Relationship(back_populates="task_definition", cascade_delete=True)
    machine_id: str | None = Field(default=None, foreign_key="machine.id")
    machine: "Machine" = Relationship(back_populates="task_definitions")
    supplies: list["TaskSupply"] = Relationship(back_populates="task_definition", cascade_delete=True)


class Task(SQLModel, table=True):
    id: str = Field(default_factory=uuid_gen, primary_key=True)
    completed: bool = False
    completed_date: Optional[datetime.date] = None
    completed_meter_reading: Optional[float] = None
    due_date: datetime.date
    due_meter_reading: float = None
    notes: Optional[str] = None
    task_definition_id: str | None = Field(default=None, foreign_key="taskdefinition.id")
    task_definition: TaskDefinition | None = Relationship(back_populates="tasks")
    machine_id: str | None = Field(default=None, foreign_key="machine.id")
    machine: "Machine" = Relationship(back_populates="tasks")


class Machine(SQLModel, table=True):
    id: str = Field(default_factory=uuid_gen, primary_key=True)
    meter_unit: str
    make: str
    model: str
    year: int
    image: str
    purchase_date: Optional[datetime.date] = None
    meter_readings: List["MeterReading"] = Relationship(back_populates="machine", cascade_delete=True)
    task_definitions: List["TaskDefinition"] = Relationship(back_populates="machine", cascade_delete=True)
    tasks: List["Task"] = Relationship(back_populates="machine", cascade_delete=True)
