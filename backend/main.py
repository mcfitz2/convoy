from typing import List
from schemas import (
    APIResponse,
    AssignedTaskSupplySchema,
    CreateMachineSchema,
    MachineSchema,
    MeterReadingSchema,
    Status,
    SupplySchema,
    CompleteTaskSchema,
    CreateTaskDefinitionSchema,
    TaskDefinitionSchema,
    TaskSchema,
    TaskSupplySchema,
)
from utils import (
    custom_generate_unique_id,
    get_session,
    setup_engine,
)
from models import Machine, MeterReading, Supply, Task, TaskDefinition, TaskSupply
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import datetime
from sqlmodel import Session, SQLModel, select
from sqlalchemy.orm import selectinload


engine = setup_engine()
app = FastAPI(generate_unique_id_function=custom_generate_unique_id)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.get("/api/v1/machines", response_model=List[MachineSchema])
def get_machines(*, session: Session = Depends(get_session)) -> List[MachineSchema]:
    return [MachineSchema.model_validate(m) for m in session.exec(select(Machine)).all()]


@app.get("/api/v1/supplies", response_model=List[SupplySchema])
def get_supplies(*, session: Session = Depends(get_session)) -> List[SupplySchema]:
    return [SupplySchema.model_validate(s) for s in session.exec(select(Supply)).all()]


@app.post("/api/v1/supplies", response_model=SupplySchema)
def create_supply(supply: SupplySchema, *, session: Session = Depends(get_session)) -> SupplySchema:
    db_supply = Supply(**dict(supply))
    session.add(db_supply)

    for part in supply.parts:
        part.supply_id = db_supply.id
        session.add(part)

    session.commit()
    session.refresh(db_supply)
    return SupplySchema.model_validate(db_supply)


@app.delete("/api/v1/supplies/{supply_id}", response_model=SupplySchema)
def delete_supply(supply_id, *, session: Session = Depends(get_session)) -> Supply:
    supply = session.get(Supply, supply_id)
    session.delete(supply)
    session.commit()
    return SupplySchema.model_validate(supply)


@app.post("/api/v1/machines/{machine_id}/task_definitions/{task_def_id}/supplies", response_model=APIResponse)
def assign_supplies(
    machine_id: str, task_def_id: str, supplies: List[AssignedTaskSupplySchema], *, session: Session = Depends(get_session)
) -> APIResponse:
    for task_supply in supplies:
        ts = TaskSupply.model_validate(task_supply)
        ts.task_definition_id = task_def_id
        session.add(ts)
    session.commit()
    return APIResponse(status=Status.SUCCESS, message="Supplies assigned")


@app.get("/api/v1/machines/{machine_id}", response_model=MachineSchema)
def get_machine(machine_id: str, *, session: Session = Depends(get_session)) -> MachineSchema:
    machine = session.exec(select(Machine).where(Machine.id == machine_id).options(selectinload("*"))).one()
    return MachineSchema.model_validate(machine)


@app.get("/api/v1/machines/{machine_id}/readings", response_model=List[MeterReadingSchema])
def get_readings(machine_id: str, *, session: Session = Depends(get_session)) -> List[MeterReadingSchema]:
    readings = session.exec(select(MeterReading).where(MeterReading.machine_id == machine_id)).all()
    return [MeterReadingSchema.model_validate(reading) for reading in readings]


@app.post("/api/v1/machines/{machine_id}/readings", response_model=MeterReading)
def create_reading(machine_id: str, reading: MeterReading, *, session: Session = Depends(get_session)) -> MeterReading:
    reading.machine_id = machine_id
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading


@app.get("/api/v1/machines/{machine_id}/readings/{reading_id}", response_model=MeterReading)
def get_reading(machine_id: str, reading_id: str, *, session: Session = Depends(get_session)):
    reading = session.exec(select(MeterReading).where(MeterReading.id == reading_id)).one()
    return reading


@app.get("/api/v1/machines/{machine_id}/tasks", response_model=List[TaskSchema])
def get_tasks(machine_id: str, *, session: Session = Depends(get_session)) -> List[Task]:
    tasks = session.exec(select(Task).where(Task.machine_id == machine_id)).all()

    return [TaskSchema.model_validate(t) for t in tasks]


@app.get("/api/v1/machines/{machine_id}/tasks/{task_id}", response_model=TaskSchema)
def get_task(machine_id: str, task_id: str, *, session: Session = Depends(get_session)):
    task = session.exec(select(Task).where(Task.id == task_id and Task.machine_id == machine_id)).one()
    return TaskSchema.model_validate(task)


@app.get("/api/v1/machines/{machine_id}/task_definitions", response_model=List[TaskDefinitionSchema])
def get_task_definitions(machine_id: str, *, session: Session = Depends(get_session)) -> List[TaskDefinitionSchema]:
    task_defs = session.exec(select(TaskDefinition).where(TaskDefinition.machine_id == machine_id)).all()
    return [TaskDefinitionSchema.model_validate(t) for t in task_defs]


@app.post("/api/v1/machines/{machine_id}/task_definitions", response_model=TaskDefinition)
def create_task_definition(
    machine_id: str,
    task_definition_create: CreateTaskDefinitionSchema,
    *,
    session: Session = Depends(get_session),
) -> TaskDefinition:

    task_definition = TaskDefinition(**dict(task_definition_create))
    task_definition.machine_id = machine_id
    session.add(task_definition)

    meter_reading = session.exec(select(MeterReading).where(MeterReading.machine_id == machine_id).order_by(MeterReading.timestamp.desc())).first()
    if task_definition_create.initial_due_meter:
        due_meter = task_definition_create.initial_due_meter
    elif meter_reading:
        due_meter = meter_reading.value
    else:
        due_meter = 0
    due_date = task_definition_create.initial_due_date if task_definition_create.initial_due_date else datetime.datetime.today()
    new_task = Task(
        due_date=due_date,
        due_meter_reading=due_meter,
        machine_id=machine_id,
        task_definition_id=task_definition.id,
    )
    session.add(new_task)
    session.commit()
    session.refresh(task_definition)
    return TaskDefinitionSchema.model_validate(task_definition)


@app.post("/api/v1/machines", response_model=MachineSchema)
def create_machine(machine: CreateMachineSchema, *, session: Session = Depends(get_session)) -> MachineSchema:
    m = Machine.model_validate(machine)
    session.add(m)
    reading = MeterReading()
    reading.machine_id = m.id
    reading.timestamp = datetime.datetime.now()
    reading.value = 0
    session.add(reading)
    session.commit()
    session.refresh(m)
    return MachineSchema.model_validate(m)


@app.get("/api/v1/machines/{machine_id}/task_definitions/{task_definition_id}", response_model=TaskDefinitionSchema)
def get_task_definition(machine_id: str, task_definition_id: str, *, session: Session = Depends(get_session)):
    task_def = session.exec(select(TaskDefinition).where(TaskDefinition.id == task_definition_id and TaskDefinition.machine_id == machine_id)).one()
    return TaskDefinitionSchema.model_validate(task_def)


@app.delete("/api/v1/tasks/{task_id}", response_model=TaskSchema)
def delete_task(
    task_id: str,
    *,
    session: Session = Depends(get_session),
) -> TaskSchema:
    task = session.get(Task, task_id)
    session.delete(task)
    session.commit()
    return TaskSchema.model_validate(task)


@app.delete("/api/v1/task_definitions/{task_id}", response_model=TaskDefinitionSchema)
def delete_task_definition(
    task_id: str,
    *,
    session: Session = Depends(get_session),
) -> TaskDefinitionSchema:
    task = session.get(TaskDefinition, task_id)
    session.delete(task)
    session.commit()
    
    return TaskDefinitionSchema.model_validate(task)


@app.delete("/api/v1/machines/{machine_id}", response_model=MachineSchema)
def delete_machine(
    machine_id: str,
    *,
    session: Session = Depends(get_session),
) -> MachineSchema:
    machine = session.get(Machine, machine_id)
    session.delete(machine)
    session.commit()
    return MachineSchema.model_validate(machine)


@app.post("/api/v1/tasks/{task_id}/complete", response_model=TaskSchema)
def complete_task(
    task_request: CompleteTaskSchema,
    task_id: str,
    *,
    session: Session = Depends(get_session),
) -> TaskSchema:
    task = session.exec(select(Task).where(Task.id == task_id)).one()
    task.completed = True
    task.sqlmodel_update(task_request)
    session.add(
        MeterReading(
            machine_id=task.machine_id,
            value=task_request.completed_meter_reading,
            timestamp=task_request.completed_date,
        )
    )
    session.add(task)
    if task.task_definition.recurring:
        new_task = Task(
            due_date=datetime.date.today() + datetime.timedelta(days=task.task_definition.time_interval),
            due_meter_reading=task.task_definition.meter_interval + task.completed_meter_reading,
            machine_id=task.machine_id,
            task_definition_id=task.task_definition_id,
        )
        session.add(new_task)
    session.commit()
    return TaskSchema.model_validate(task)


@app.patch("/api/v1/supplies/{supply_id}", response_model=SupplySchema)
def update_supply(supply_id: str, supply: SupplySchema, *, session: Session = Depends(get_session)) -> SupplySchema:
    db_supply = session.get(Supply, supply_id)
    supply_data = supply.model_dump(exclude_unset=True)
    db_supply.sqlmodel_update(supply_data)
    session.add(db_supply)
    session.commit()
    session.refresh(db_supply)
    return SupplySchema.model_validate(db_supply)


@app.patch("/api/v1/machines/{machine_id}", response_model=MachineSchema)
def update_machine(machine_id: str, machine: CreateMachineSchema, *, session: Session = Depends(get_session)) -> MachineSchema:
    db_machine = session.get(Machine, machine_id)
    machine_data = machine.model_dump(exclude_unset=True)
    db_machine.sqlmodel_update(machine_data)
    session.add(db_machine)
    session.commit()
    session.refresh(db_machine)
    return MachineSchema.model_validate(db_machine)


@app.middleware("http")
async def add_custom_header(request, call_next):
    response = await call_next(request)
    if response.status_code == 404:
        return FileResponse("static/index.html")
    return response


@app.exception_handler(404)
def not_found(request, exc):
    return FileResponse("static/index.html")


app.mount("/ui", StaticFiles(directory="static"), name="static")
