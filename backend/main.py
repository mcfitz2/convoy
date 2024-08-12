from typing import List
from utils import (
    custom_generate_unique_id,
    get_session,
    setup_engine,
)
from models import (
    APIResponse,
    Machine,
    MachineCreate,
    MachineDetailed,
    MeterReading,
    Status,
    Supply,
    SupplyDetailed,
    Task,
    TaskComplete,
    TaskDefinition,
    TaskDefinitionCreate,
    TaskDetailed,
    TaskSupply,
)
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


@app.get("/api/v1/machines", response_model=List[MachineDetailed])
def get_machines(*, session: Session = Depends(get_session)) -> List[MachineDetailed]:
    def enrich_machine(m: Machine) -> MachineDetailed:
        md = MachineDetailed.from_orm(m)
        return md

    machines = map(enrich_machine, session.exec(select(Machine)).all())

    return machines


@app.get("/api/v1/supplies", response_model=List[SupplyDetailed])
def get_supplies(*, session: Session = Depends(get_session)) -> List[SupplyDetailed]:
    return [SupplyDetailed.from_orm(s) for s in session.exec(select(Supply)).all()]


@app.post("/api/v1/supplies", response_model=SupplyDetailed)
def create_supply(supply: SupplyDetailed, *, session: Session = Depends(get_session)) -> SupplyDetailed:
    db_supply = Supply(**dict(supply))
    session.add(db_supply)

    for part in supply.parts:
        part.supply_id = db_supply.id
        session.add(part)

    session.commit()
    session.refresh(db_supply)
    return db_supply


@app.delete("/api/v1/supplies/{supply_id}", response_model=Supply)
def delete_supply(supply_id, *, session: Session = Depends(get_session)) -> Supply:
    supply = session.get(Supply, supply_id)
    session.delete(supply)
    session.commit()
    return supply


@app.post("/api/v1/machines/{machine_id}/task_definitions/{task_def_id}/supplies", response_model=APIResponse)
def assign_supplies(machine_id: str, task_def_id: str, supplies: List[TaskSupply], *, session: Session = Depends(get_session)) -> APIResponse:
    for task_supply in supplies:
        task_supply.task_definition_id = task_def_id
        session.add(task_supply)
    session.commit()
    return APIResponse(status=Status.SUCCESS, message="Supplies assigned")


@app.get("/api/v1/machines/{machine_id}", response_model=Machine)
def get_machine(machine_id: str, *, session: Session = Depends(get_session)) -> Machine:
    machines = session.exec(select(Machine).where(Machine.id == machine_id).options(selectinload("*"))).one()
    return machines


@app.get("/api/v1/machines/{machine_id}/readings", response_model=List[MeterReading])
def get_readings(machine_id: str, *, session: Session = Depends(get_session)) -> List[MeterReading]:
    readings = session.exec(select(MeterReading).where(MeterReading.machine_id == machine_id)).all()
    return readings


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


@app.get("/api/v1/machines/{machine_id}/tasks", response_model=List[TaskDetailed])
def get_tasks(machine_id: str, *, session: Session = Depends(get_session)) -> List[Task]:
    tasks = session.exec(select(Task).where(Task.machine_id == machine_id)).all()

    return [TaskDetailed(**dict(t)) for t in tasks]


@app.get("/api/v1/machines/{machine_id}/tasks/{task_id}", response_model=TaskDetailed)
def get_task(machine_id: str, task_id: str, *, session: Session = Depends(get_session)):
    task = session.exec(select(Task).where(Task.id == task_id and Task.machine_id == machine_id)).one()
    return TaskDetailed(**dict(task))


@app.get("/api/v1/machines/{machine_id}/task_definitions", response_model=List[TaskDefinition])
def get_task_definitions(machine_id: str, *, session: Session = Depends(get_session)) -> List[TaskDefinition]:
    task_defs = session.exec(select(TaskDefinition).where(TaskDefinition.machine_id == machine_id)).all()
    return task_defs


@app.post("/api/v1/machines/{machine_id}/task_definitions", response_model=TaskDefinition)
def create_task_definition(
    machine_id: str,
    task_definition_create: TaskDefinitionCreate,
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
    return task_definition


@app.post("/api/v1/machines")
def create_machine(machine: MachineCreate, *, session: Session = Depends(get_session)) -> Machine:
    values = dict(machine)

    m = Machine(**values)
    session.add(m)
    reading = MeterReading()
    reading.machine_id = m.id
    reading.timestamp = datetime.datetime.now()
    reading.value = 0
    session.add(reading)
    session.commit()
    session.refresh(m)
    return m


@app.get("/api/v1/machines/{machine_id}/task_definitions/{task_definition_id}", response_model=TaskDefinition)
def get_task_definition(machine_id: str, task_definition_id: str, *, session: Session = Depends(get_session)):
    task_def = session.exec(select(TaskDefinition).where(TaskDefinition.id == task_definition_id and TaskDefinition.machine_id == machine_id)).one()
    return task_def


@app.delete("/api/v1/tasks/{task_id}", response_model=Task)
def delete_task(
    task_id: str,
    *,
    session: Session = Depends(get_session),
):
    task = session.get(Task, task_id)
    session.delete(task)
    session.commit()
    return task


@app.delete("/api/v1/task_definitions/{task_id}", response_model=TaskDefinition)
def delete_task_definition(
    task_id: str,
    *,
    session: Session = Depends(get_session),
):
    task = session.get(TaskDefinition, task_id)
    session.delete(task)
    session.commit()
    return task


@app.delete("/api/v1/machines/{machine_id}", response_model=Machine)
def delete_machine(
    machine_id: str,
    *,
    session: Session = Depends(get_session),
):
    machine = session.get(Machine, machine_id)
    session.delete(machine)
    session.commit()
    return machine


@app.post("/api/v1/tasks/{task_id}/complete", response_model=Task)
def complete_task(
    task_request: TaskComplete,
    task_id: str,
    *,
    session: Session = Depends(get_session),
):
    task = session.exec(select(Task).where(Task.id == task_id)).one()
    task.completed = True
    task.sqlmodel_update(**dict(task_request))
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
    return task


@app.patch("/api/v1/supplies/{supply_id}", response_model=Supply)
def update_supply(supply_id: str, supply: Supply, *, session: Session = Depends(get_session)) -> Supply:
    db_supply = session.get(Supply, supply_id)
    supply_data = supply.model_dump(exclude_unset=True)
    db_supply.sqlmodel_update(supply_data)
    session.add(db_supply)
    session.commit()
    session.refresh(db_supply)
    return db_supply


@app.patch("/api/v1/machines/{machine_id}", response_model=Machine)
def update_machine(machine_id: str, machine: MachineCreate, *, session: Session = Depends(get_session)) -> Machine:
    db_machine = session.get(Machine, machine_id)
    machine_data = machine.model_dump(exclude_unset=True)
    db_machine.sqlmodel_update(machine_data)
    session.add(db_machine)
    session.commit()
    session.refresh(db_machine)
    return db_machine


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
