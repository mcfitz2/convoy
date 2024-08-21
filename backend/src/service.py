import datetime
import os
from typing import List, Tuple

from bson import ObjectId
import requests
from sqlalchemy import select, update
from exceptions import MachineNotFound, TaskNotFound
from utils import LogRetry, setup_logger
from models import Base, Machine, MeterReading, Supply, Task
from todoist_api_python.api_async import TodoistAPIAsync
from todoist_api_python.models import Task as TDTask

from todoist_api_python.endpoints import BASE_URL
from requests import Session as RequestsSession
from requests.adapters import HTTPAdapter
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

logger = setup_logger("ConvoyService")
enable_todoist = False


class ConvoyService:
    async def init_models(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    def __init__(self):
        self.engine = create_async_engine("sqlite+aiosqlite://")
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        self.token = os.environ.get("TODOIST_TOKEN", "6b679be327e54dd808c0bb79da8aa43962d008b8")
        self.project = os.environ.get("TODOIST_PROJECT_ID", "2338186081")
        s = RequestsSession()
        s.mount(BASE_URL, HTTPAdapter(max_retries=LogRetry(total=10, backoff_factor=1, status_forcelist=[500, 502, 503, 504])))
        self.todoist: TodoistAPIAsync = TodoistAPIAsync(self.token, session=s)

    async def create_machine(self, machine: Machine) -> Machine:
        async with self.async_session() as session:
            session.add(machine)
            for meter_reading in machine.meter_readings:
                session.add(meter_reading)
            for task in machine.tasks:
                session.add(task)
            await session.commit()
            await session.refresh(machine)
            return machine

    async def get_machine(self, machine_id) -> Machine:
        async with self.async_session() as session:
            machine = (await session.execute(select(Machine).where(Machine.id == machine_id))).unique().scalars().first()
            if not machine:
                raise MachineNotFound(machine_id)
            else:
                return machine

    async def update_machine(self, machine_id: str, new_machine: dict) -> Machine:
        machine = await self.get_machine(machine_id)
        if not machine:
            raise MachineNotFound(machine_id)
        async with self.async_session() as session:
            await session.execute(update(Machine).where(Machine.id == machine_id).values(**new_machine))
            session.add(machine)
            await session.commit()
            await session.refresh(machine)
            return machine

    async def delete_machine(self, machine_id: str) -> Machine:
        async with self.async_session() as session:
            machine = (await session.execute(select(Machine).where(Machine.id == machine_id))).unique().scalars().first()
            await session.delete(machine)
            await session.commit()
            await self.reconcile_tasks(machine)
            return machine

    async def get_machines(self) -> List[Machine]:
        async with self.async_session() as session:
            return (await session.execute(select(Machine))).unique().scalars().all()

    async def record_reading(self, machine_id: str, reading: MeterReading) -> MeterReading:
        machine = await self.get_machine(machine_id)
        async with self.async_session() as session:
            session.add(reading)
            await session.commit()
            await session.refresh(reading)
            await self.reconcile_tasks(machine)
            return reading

    async def create_task(self, machine_id: str, task: Task) -> Task:
        machine = await self.get_machine(machine_id)

        task.due_meter_reading = task.due_meter_reading if task.due_meter_reading else machine.current_meter_reading()
        task.due_date = task.due_date if task.due_date else datetime.date.today()
        task.machine_id = machine_id
        async with self.async_session() as session:
            session.add(task)
            await session.commit()
            await session.refresh(task)
            await self.reconcile_task(machine, task)
            return task

    async def complete_task(self, machine_id: str, task_id: str, completed_date: datetime.date, completed_meter_reading: float, notes: str) -> Task:
        machine = await self.get_machine(machine_id)
        task = await self.get_task(machine_id, task_id)
        task.completed = True
        task.completed_date = completed_date
        task.completed_meter_reading = completed_meter_reading
        if notes:
            task.notes = notes
        async with self.async_session() as session:
            session.add(task)
            if task.recurring:
                new_task = Task(
                    due_date=task.completed_date + datetime.timedelta(days=task.time_interval),
                    due_meter_reading=task.completed_meter_reading + task.meter_interval,
                    completed=False,
                    completed_meter_reading=None,
                    completed_date=None,
                    notes=task.notes,
                    todoist_task_id=None,
                    machine_id=machine_id,
                    task_supplies=task.task_supplies,
                )
                session.add(new_task)
                await self.reconcile_task(machine.id, new_task)

        await session.commit()
        await self.reconcile_task(machine.id, task)

        return task

    async def set_todoist_task_id(self, machine_id: str, task_id: str, todoist_task_id: str):
        logger.info(f"Setting todoist_task_id={todoist_task_id} on task {task_id}")
        async with self.async_session() as session:
            await session.execute(update(Task).where(Task.id == task_id).values({"todoist_task_id": todoist_task_id}))
            await session.commit()
    async def delete_task(self, machine_id: str, task_id: str) -> Task:
        async with self.async_session() as session:
            task = (await session.execute(select(Task).where(Task.id == task_id))).unique().scalars().first()
            await session.delete(task)
            await session.commit()
            await self.reconcile_task(machine_id, task)
            return task

    async def get_task(self, machine_id: str, task_id: str) -> Task:
        async with self.async_session() as session:
            task = (await session.execute(select(Task).where(Task.id == task_id))).unique().scalars().first()
            if not task:
                raise TaskNotFound(machine_id, task_id)
            return task

    async def get_tasks(self, machine_id: str) -> List[Task]:
        await self.get_machine(machine_id)
        async with self.async_session() as session:
            tasks = (await session.execute(select(Task).where(Task.machine_id == machine_id))).unique().scalars().all()
            return tasks

    async def get_supply(self, supply_id) -> Supply:
        result = await self.engine.find_one(Supply, {"_id": ObjectId(supply_id)})
        return result

    async def get_supplies(self) -> List[Supply]:
        result = await self.engine.find(Supply, {})
        return result

    async def create_supply(self, supply) -> Supply:
        created = await self.engine.save(supply)
        return created

    async def update_supply(self, supply_id, new_supply) -> Supply:
        supply = await self.get_supply(supply_id)
        supply.model_update(new_supply, exclude=["id", "_id"])
        updated = await self.engine.save(supply)
        return updated

    async def delete_supply(self, supply_id) -> Supply:
        supply = await self.get_supply(supply_id)
        await self.engine.delete(supply)
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

    async def reconcile_tasks(self, machine: Machine) -> List[Tuple[TDTask | None, bool]]:
        return [await self.reconcile_task(machine.id, task) for task in machine.tasks]

    async def reconcile_task(self, machine_id: str, task: Task, deleted=False) -> Tuple[TDTask | None, bool]:
        if enable_todoist:
            if deleted and task.todoist_task_id:
                logger.info(f"Convoy task[{task.id}] has been deleted. Deleting Todoist task[{task.todoist_task_id}]")
                await self.todoist.delete_task(task.todoist_task_id)
                return
            if not deleted and task.todoist_task_id:
                try:
                    td_task: TDTask = await self.todoist.get_task(task.todoist_task_id)
                    assert task.description == td_task.content
                    assert task.due_date.strftime("%Y-%m-%d") == td_task.due.date
                    assert task.completed == td_task.is_completed
                    logger.info(f"Convoy task[{task.id}] matches Todoist task[{task.todoist_task_id}]. Doing nothing.")
                    return
                except AssertionError:
                    logger.info(f"Convoy task[{task.id}] does not match Todoist task[{task.todoist_task_id}]. Updating TD task.")
                    await self.todoist.update_task(
                        task.todoist_task_id, content=task.description, due_string=task.due_date.strftime("%Y-%m-%d"), is_completed=task.completed
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
                    return
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        logger.info(f"Todoist task[{task.todoist_task_id}] for Convoy task[{task.id}] has been deleted. Recreating.")
                        td_task = await self.create_td_task(task)
                        await self.set_todoist_task_id(machine_id, task.id, td_task.id)
                        return
                    else:
                        logger.info(f"Failed to reconcile Convoy task[{task.id}]", exc_info=e)
                        return

            if not task.todoist_task_id:
                logger.info(f"Todoist task for Convoy task[{task.id}] does not exist. Creating.")
                td_task = await self.create_td_task(task)
                if td_task:
                    await self.set_todoist_task_id(machine_id, task.id, td_task.id)
                return


convoy_service = ConvoyService()
