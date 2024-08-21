import datetime
import logging
from ..main.service import convoy_service as service
from ..main.models import Machine, MeterReading, Task
from ..main.main import app
from httpx import ASGITransport, AsyncClient
import os


async def init():
    await service.init_models()


async def delete_all_doist_tasks():
    for task in await service.todoist.get_tasks(project_id=os.environ.get("TODOIST_PROJECT_ID", "2338186081")):
        await service.todoist.delete_task(task.id)


async def create_machine_via_service() -> Machine:
    machine = await service.create_machine(
        Machine(
            meter_unit="mile",
            make="Test",
            model="Machine",
            year=2025,
            purchase_date=datetime.date(2024, 8, 19),
            meter_readings=[MeterReading(timestamp=datetime.datetime.now(), value=1000)],
            tasks=[
                Task(description="Task To Delete", time_interval=100, meter_interval=100, due_date=datetime.datetime.today(), due_meter_reading=2000),
                Task(
                    description="Task to Complete", time_interval=100, meter_interval=100, due_date=datetime.datetime.today(), due_meter_reading=2000
                ),
            ],
        )
    )
    return machine


async def get_machines_via_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/machines")
        return response


async def create_task_via_api(machine_id, recurring=False):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            f"/api/v1/machines/{machine_id}/tasks",
            json={
                "description": "Oil Change",
                "time_interval": 10,
                "meter_interval": 1000,
                "due_date": "08/30/2024",
                "due_meter_reading": 10000,
                "recurring": recurring,
            },
        )
        return response


async def delete_machine_via_api(machine_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete(f"/api/v1/machines/{machine_id}")
        return response


async def delete_task_via_api(machine_id, task_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete(f"/api/v1/machines/{machine_id}/tasks/{task_id}")
        return response


async def complete_task_via_api(machine_id, task_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            f"/api/v1/machines/{machine_id}/tasks/{task_id}/complete",
            json={"completed_date": "08/19/2024", "completed_meter_reading": 1000, "notes": "Did a thing"},
        )
        if response.status_code != 200:
            logging.warning(response.content)
        return response


async def get_task_via_api(machine_id, task_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:

        response = await ac.get(
            f"/api/v1/machines/{machine_id}/tasks/{task_id}",
        )
        return response


async def get_tasks_via_api(machine_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:

        response = await ac.get(
            f"/api/v1/machines/{machine_id}/tasks",
        )
        return response


async def create_machine_via_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/machines",
            headers={"Content-Type": "application/json"},
            json={
                "meter_unit": "mile",
                "make": "Test",
                "model": "Machine 2",
                "year": 2025,
                "purchase_date": "08/19/2024",
            },
        )
        return response


async def get_machine_via_api(machine_id: str):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            f"/api/v1/machines/{machine_id}",
        )
        return response


async def create_supply_via_api(machine_id=None, name=None):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/supplies",
            headers={"Content-Type": "application/json"},
            json={"name": name or "Oil Filter", "unit": "each", "quantity_on_hand": 2, "machine_id": machine_id},
        )
        if response.status_code == 422:
            logging.warning(response.content)
        return response


async def get_supply_via_api(supply_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/supplies/{supply_id}")
        return response


async def delete_supply_via_api(supply_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete(f"/api/v1/supplies/{supply_id}")
        return response


async def get_supplies_via_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/supplies")
        return response


async def update_supply_via_api(supply_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.patch(
            f"/api/v1/supplies/{supply_id}",
            json={
                "quantity_on_hand": 1000,
            },
        )
        return response
