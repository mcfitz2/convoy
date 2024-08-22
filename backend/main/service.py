import datetime
import os
from typing import List, Tuple

import requests
from requests import HTTPError
from requests import Session as RequestsSession
from requests.adapters import HTTPAdapter
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from todoist_api_python.api_async import TodoistAPIAsync
from todoist_api_python.endpoints import BASE_URL
from todoist_api_python.models import Task as TDTask

from .exceptions import MachineNotFound, SupplyNotFound, TaskNotFound
from .models import (
    Base,
    DueReason,
    Machine,
    MachineSchema,
    MeterReading,
    Supply,
    Task,
    TaskDetailedState,
    TaskDueState,
    TasksByStateSchema,
    TaskSchema,
)
from .utils import LogRetry, setup_logger

logger = setup_logger("ConvoyService")
enable_todoist = True


class ConvoyService:
    async def init_models(self, drop=True):
        async with self.engine.begin() as conn:
            if drop:
                await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    def __init__(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///convoy.db")
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        self.token = os.environ.get("TODOIST_TOKEN", "")
        self.project = os.environ.get("TODOIST_PROJECT_ID", "2338186081")
        s = RequestsSession()
        s.mount(
            BASE_URL,
            HTTPAdapter(
                max_retries=LogRetry(
                    total=10, backoff_factor=1, status_forcelist=[500, 502, 503, 504]
                )
            ),
        )
        self.todoist: TodoistAPIAsync = TodoistAPIAsync(self.token, session=s)

    async def machine_to_schema(self, machine: Machine) -> MachineSchema:
        machine = MachineSchema(
            id=machine.id,
            vin=machine.vin,
            meter_unit=machine.meter_unit,
            make=machine.make,
            model=machine.model,
            year=machine.year,
            image=machine.image,
            purchase_date=machine.purchase_date,
            meter_readings=machine.meter_readings,
            tasks=machine.tasks,
            current_meter_reading=await self.get_current_meter_reading(machine.id)
        )
        return MachineSchema.model_validate(machine)

    async def task_to_schema(self, task: Task) -> TaskSchema:
        task = TaskSchema(
            id=task.id,
            description=task.description,
            time_interval=task.time_interval,
            meter_interval=task.meter_interval,
            recurring=task.recurring,
            notes=task.notes,
            completed=task.completed,
            completed_date=task.completed_date,
            completed_meter_reading=task.completed_meter_reading,
            due_date=task.due_date,
            due_meter_reading=task.due_meter_reading,
            todoist_task_id=task.todoist_task_id,
            machine_id=task.machine_id,
            task_supplies=task.task_supplies,
            detailed_state=await self.determine_task_state(task.machine_id, task.id)
        )
        return TaskSchema.model_validate(task)

    async def create_machine(self, machine: Machine) -> MachineSchema:
        async with self.async_session() as session:
            session.add(machine)
            await session.commit()
            await session.refresh(machine)
            for meter_reading in machine.meter_readings:
                meter_reading.machine_id = machine.id
                session.add(meter_reading)

            for task in machine.tasks:
                task.machine_id = machine.id
                session.add(task)

            await session.commit()
            await session.refresh(machine)
            if len(machine.meter_readings) == 0:
                session.add(
                    MeterReading(
                        timestamp=datetime.datetime.now(),
                        value=0,
                        machine_id=machine.id,
                    )
                )
                await session.commit()
                await session.refresh(machine)
        return machine

    async def get_machine(self, machine_id) -> Machine:
        async with self.async_session() as session:
            machine = (
                (await session.execute(select(Machine).where(Machine.id == machine_id)))
                .unique()
                .scalars()
                .first()
            )
        if not machine:
            raise MachineNotFound(machine_id)
        else:
            return machine

    async def update_machine(self, machine_id: str, new_machine: dict) -> Machine:
        machine = await self.get_machine(machine_id)
        async with self.async_session() as session:
            await session.execute(
                update(Machine).where(Machine.id == machine_id).values(**new_machine)
            )
            session.add(machine)
            await session.commit()
            await session.refresh(machine)
        return machine

    async def delete_machine(self, machine_id: str) -> Machine:
        async with self.async_session() as session:
            machine = (
                (await session.execute(select(Machine).where(Machine.id == machine_id)))
                .unique()
                .scalars()
                .first()
            )
            await session.delete(machine)
            await session.commit()
            await self.reconcile_tasks(machine)
        return machine

    async def get_machines(self) -> List[Machine]:
        async with self.async_session() as session:
            return (await session.execute(select(Machine))).unique().scalars().all()

    async def get_current_meter_reading(self, machine_id: str) -> float:
        async with self.async_session() as session:
            reading = (
                (
                    await session.execute(
                        select(MeterReading)
                        .where(MeterReading.machine_id == machine_id)
                        .order_by(MeterReading.timestamp)
                        .limit(1)
                    )
                )
                .scalars()
                .first()
            )
            if reading:
                return float(reading.value)
            else:
                return 0

    async def record_reading(
        self, machine_id: str, reading: MeterReading
    ) -> MeterReading:
        machine = await self.get_machine(machine_id)
        async with self.async_session() as session:
            session.add(reading)
            await session.commit()
            await session.refresh(reading)
            await self.reconcile_tasks(machine)
        return reading

    async def create_task(self, machine_id: str, task: Task) -> Task:
        machine = await self.get_machine(machine_id)

        task.due_meter_reading = (
            task.due_meter_reading
            if task.due_meter_reading
            else await self.get_current_meter_reading(machine.id)
        )
        task.due_date = task.due_date if task.due_date else datetime.date.today()
        task.machine_id = machine_id
        async with self.async_session() as session:
            session.add(task)
            await session.commit()
            await session.refresh(task)
            try:
                task, td_task = await self.reconcile_task(machine, task)
            except HTTPError:
                pass
            return task

    async def complete_task(
        self,
        machine_id: str,
        task_id: str,
        completed_date: datetime.date,
        completed_meter_reading: float,
        notes: str,
    ) -> Task:
        machine = await self.get_machine(machine_id)
        task = await self.get_task(machine_id, task_id)
        task.completed = True
        task.completed_date = completed_date
        task.completed_meter_reading = completed_meter_reading
        if notes:
            task.notes = notes
        async with self.async_session() as session:
            session.add(task)
            await session.commit()
            if task.recurring:
                logger.warning(
                    f"Completed task [{task_id}] was recurring task. Creating new task"
                )
                new_task = Task(
                    description=task.description,
                    time_interval=task.time_interval,
                    meter_interval=task.meter_interval,
                    due_date=task.completed_date
                    + datetime.timedelta(days=task.time_interval),
                    due_meter_reading=task.completed_meter_reading
                    + task.meter_interval,
                    completed=False,
                    completed_meter_reading=None,
                    completed_date=None,
                    notes=task.notes,
                    todoist_task_id=None,
                    machine_id=machine_id,
                    task_supplies=task.task_supplies,
                )
                session.add(new_task)
                await session.commit()
                await self.reconcile_task(machine.id, new_task)

            await self.reconcile_task(machine.id, task)
        return task

    async def set_todoist_task_id(
        self, machine_id: str, task_id: str, todoist_task_id: str
    ):
        logger.info(f"Setting todoist_task_id={todoist_task_id} on task {task_id}")
        async with self.async_session() as session:
            await session.execute(
                update(Task)
                .where(Task.id == task_id)
                .values({"todoist_task_id": todoist_task_id})
            )
            await session.commit()
        task = await self.get_task(machine_id, task_id)
        return task

    async def delete_task(self, machine_id: str, task_id: str) -> Task:
        task = await self.get_task(machine_id, task_id)
        async with self.async_session() as session:
            await session.delete(task)
            await session.commit()
        task, td_task = await self.reconcile_task(machine_id, task, deleted=True)
        return task

    async def get_task(self, machine_id: str, task_id: str) -> Task:
        async with self.async_session() as session:
            task = (
                (await session.execute(select(Task).where(Task.id == task_id)))
                .unique()
                .scalars()
                .first()
            )
        if not task:
            raise TaskNotFound(machine_id, task_id)
        return task

    async def get_tasks(self, machine_id: str) -> List[Task]:
        await self.get_machine(machine_id)
        async with self.async_session() as session:
            tasks = (
                (
                    await session.execute(
                        select(Task).where(Task.machine_id == machine_id)
                    )
                )
                .unique()
                .scalars()
                .all()
            )
        return tasks

    async def get_all_tasks(self) -> List[Task]:
        async with self.async_session() as session:
            tasks = (await session.execute(select(Task))).unique().scalars().all()
        return tasks

    async def determine_task_state(
        self, machine_id: str, task_id: str
    ) -> TaskDetailedState:
        task = await self.get_task(machine_id, task_id)
        current_meter: float = await self.get_current_meter_reading(machine_id)

        if task.completed:
            return TaskDetailedState(
                state=TaskDueState.COMPLETED,
                due_reason=DueReason.NOT_DUE,
                due_days_ago=(task.due_date - datetime.date.today()).days,
                due_meter_ago=task.due_meter_reading - current_meter,
            )
        else:
            if (
                task.due_meter_reading < current_meter
                and task.due_date < datetime.date.today()
            ):
                return TaskDetailedState(
                    state=TaskDueState.OVERDUE,
                    due_reason=DueReason.BOTH,
                    due_days_ago=(task.due_date - datetime.date.today()).days,
                    due_meter_ago=task.due_meter_reading - current_meter,
                )
            if (
                task.due_meter_reading < current_meter
                and task.due_date >= datetime.date.today()
            ):
                return TaskDetailedState(
                    state=TaskDueState.OVERDUE,
                    due_reason=DueReason.METER,
                    due_days_ago=(task.due_date - datetime.date.today()).days,
                    due_meter_ago=task.due_meter_reading - current_meter,
                )
            if (
                task.due_meter_reading > current_meter
                and task.due_date < datetime.date.today()
            ):
                return TaskDetailedState(
                    state=TaskDueState.OVERDUE,
                    due_reason=DueReason.TIME,
                    due_days_ago=(task.due_date - datetime.date.today()).days,
                    due_meter_ago=task.due_meter_reading - current_meter,
                )

            if (
                task.due_meter_reading == current_meter
                and task.due_date == datetime.date.today()
            ):
                return TaskDetailedState(
                    state=TaskDueState.DUE,
                    due_reason=DueReason.BOTH,
                    due_days_ago=(task.due_date - datetime.date.today()).days,
                    due_meter_ago=task.due_meter_reading - current_meter,
                )
            if (
                task.due_meter_reading == current_meter
                and task.due_date > datetime.date.today()
            ):
                return TaskDetailedState(
                    state=TaskDueState.DUE,
                    due_reason=DueReason.METER,
                    due_days_ago=(task.due_date - datetime.date.today()).days,
                    due_meter_ago=task.due_meter_reading - current_meter,
                )
            if (
                task.due_meter_reading > current_meter
                and task.due_date == datetime.date.today()
            ):
                return TaskDetailedState(
                    state=TaskDueState.DUE,
                    due_reason=DueReason.TIME,
                    due_days_ago=(task.due_date - datetime.date.today()).days,
                    due_meter_ago=task.due_meter_reading - current_meter,
                )
            return TaskDetailedState(
                state=TaskDueState.UPCOMING,
                due_reason=DueReason.NOT_DUE,
                due_days_ago=(task.due_date - datetime.date.today()).days,
                due_meter_ago=task.due_meter_reading - current_meter,
            )

    async def get_all_tasks_by_state(self) -> TasksByStateSchema:
        ret = TasksByStateSchema()
        tasks = await self.get_all_tasks()
        for task in tasks:
            taskSchema = TaskSchema.model_validate(task)
            taskSchema.detailed_state = await self.determine_task_state(
                task.machine_id, task.id
            )
            if taskSchema.detailed_state.state is TaskDueState.COMPLETED:
                ret.completed.append(taskSchema)
            elif taskSchema.detailed_state.state is TaskDueState.DUE:
                ret.due.append(taskSchema)
            elif taskSchema.detailed_state.state is TaskDueState.OVERDUE:
                ret.due.append(taskSchema)
                ret.overdue.append(taskSchema)
            elif taskSchema.detailed_state.state is TaskDueState.UPCOMING:
                ret.upcoming.append(taskSchema)
        return ret

    async def get_supply(self, supply_id) -> Supply:
        async with self.async_session() as session:
            supply = (
                (await session.execute(select(Supply).where(Supply.id == supply_id)))
                .unique()
                .scalars()
                .first()
            )
        if not supply:
            raise SupplyNotFound(supply_id)
        return supply

    async def get_supplies(self) -> List[Supply]:
        async with self.async_session() as session:
            supplies = (await session.execute(select(Supply))).unique().scalars().all()
        return supplies

    async def create_supply(self, supply: Supply) -> Supply:
        async with self.async_session() as session:
            session.add(supply)
            await session.commit()
            await session.refresh(supply)
        return supply

    async def update_supply(self, supply_id, new_supply) -> Supply:
        supply = await self.get_supply(supply_id)
        if not supply:
            raise SupplyNotFound(supply_id)
        async with self.async_session() as session:
            await session.execute(
                update(Supply).where(Supply.id == supply_id).values(**new_supply)
            )
            session.add(supply)
            await session.commit()
            await session.refresh(supply)
            return supply

    async def delete_supply(self, supply_id) -> Supply:
        async with self.async_session() as session:
            supply = (
                (await session.execute(select(Supply).where(Supply.id == supply_id)))
                .unique()
                .scalars()
                .first()
            )
            if not supply:
                raise SupplyNotFound(supply_id)
            await session.delete(supply)
            await session.commit()
        return supply

    async def create_td_task(self, task: Task) -> TDTask:
        try:
            new_task = {
                "project_id": self.project,
                "content": task.description,
                "due_lang": "en",
                "due_string": task.due_date.strftime("%Y-%m-%d"),
            }
            new_td_task = await self.todoist.add_task(**new_task)
            logger.info(f"Created new task {new_td_task.id}")
            return new_td_task
        except requests.exceptions.HTTPError as e:
            logger.error("Failed to create task", exc_info=e)
            return None

    async def reconcile_all_tasks(self):
        for machine in await self.get_machines():
            await self.reconcile_tasks(machine)

    async def reconcile_tasks(
        self, machine: Machine
    ) -> List[Tuple[TDTask | None, bool]]:
        return [await self.reconcile_task(machine.id, task) for task in machine.tasks]

    async def reconcile_task(
        self, machine_id: str, task: Task, deleted=False
    ) -> Tuple[Task, TDTask]:
        if enable_todoist:
            if deleted and task.todoist_task_id:
                logger.info(
                    f"Convoy task[{task.id}] has been deleted. Deleting Todoist task[{task.todoist_task_id}]"
                )
                td_task = await self.todoist.delete_task(task.todoist_task_id)
                return (task, td_task)
            if not deleted and task.todoist_task_id:
                try:
                    td_task: TDTask = await self.todoist.get_task(task.todoist_task_id)
                    assert task.description == td_task.content
                    assert task.due_date.strftime("%Y-%m-%d") == td_task.due.date
                    assert task.completed == td_task.is_completed
                    logger.info(
                        f"Convoy task[{task.id}] matches Todoist task[{task.todoist_task_id}]. Doing nothing."
                    )
                    return (task, td_task)
                except AssertionError:
                    logger.info(
                        f"Convoy task[{task.id}] does not match Todoist task[{task.todoist_task_id}]. Updating TD task."
                    )
                    await self.todoist.update_task(
                        task.todoist_task_id,
                        content=task.description,
                        due_string=task.due_date.strftime("%Y-%m-%d"),
                        is_completed=task.completed,
                    )
                    if not task.completed and td_task.is_completed:
                        logger.info(
                            f"Todoist task[{task.todoist_task_id}] has been marked completed, but Convoy task is still open. Reopening TD task."
                        )
                        await self.todoist.reopen_task(task.todoist_task_id)
                    elif task.completed and not td_task.is_completed:
                        logger.info(
                            f"Convoy task[{task.id}] has been marked completed, but Todoist task[{task.todoist_task_id}] is still open. Closing TD task."
                        )
                        await self.todoist.close_task(task.todoist_task_id)
                    td_task = await self.todoist.get_task(task.todoist_task_id)
                    return (task, td_task)
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        logger.info(
                            f"Todoist task[{task.todoist_task_id}] for Convoy task[{task.id}] has been deleted. Recreating."
                        )
                        td_task = await self.create_td_task(task)
                        task = await self.set_todoist_task_id(
                            machine_id, task.id, td_task.id
                        )
                        return (task, td_task)
                    else:
                        logger.info(
                            f"Failed to reconcile Convoy task[{task.id}]", exc_info=e
                        )
                        return (None, None)

            if not task.todoist_task_id:
                logger.info(
                    f"Todoist task for Convoy task[{task.id}] does not exist. Creating."
                )
                td_task = await self.create_td_task(task)
                if td_task:
                    task = await self.set_todoist_task_id(
                        machine_id, task.id, td_task.id
                    )
                return (task, td_task)


convoy_service = ConvoyService()
