import datetime
import logging
from pydantic import ValidationError
import pytest
from ..main.service import convoy_service as service
from ..main.models import Machine, MeterReading, MeterReadingSchema, Task, MachineSchema, TaskSchema
from ..main.main import app
from httpx import ASGITransport, AsyncClient
from fastapi.testclient import TestClient
import os

client = TestClient(app)


async def init():
    await service.init_models()


async def delete_all_doist_tasks():
    for task in await service.todoist.get_tasks(project_id=os.environ["TODOIST_PROJECT_ID"]):
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


async def create_task_via_api(machine_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            f"/api/v1/machines/{machine_id}/tasks",
            json={
                "description": "Oil Change",
                "time_interval": 10,
                "meter_interval": 1000,
                "due_date": "08/30/2024",
                "due_meter_reading": 10000,
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
            f"/api/v1/machines/{machine_id}/tasks/{task_id}/complete", json={"completed_date": "08/19/2024", "completed_meter_reading": 1000}
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


def test_parse_date():
    m1 = MachineSchema(year=2020, make="Chevy", model="Silverado", meter_unit="mile", purchase_date="08/19/24")
    m2 = MachineSchema(year=2020, make="Chevy", model="Silverado", meter_unit="mile", purchase_date=datetime.date(year=2024, day=19, month=8))
    m3 = MachineSchema(year=2020, make="Chevy", model="Silverado", meter_unit="mile", purchase_date=datetime.datetime(year=2024, day=19, month=8))
    m4 = MachineSchema(year=2020, make="Chevy", model="Silverado", meter_unit="mile", purchase_date=None)
    assert isinstance(m1.purchase_date, datetime.date)
    assert isinstance(m2.purchase_date, datetime.date)
    assert isinstance(m3.purchase_date, datetime.date)
    assert m4.purchase_date is None
    assert m4.model_dump()["purchase_date"] is None
    assert m4.model_dump_json()


def test_parse_timestamp():
    m1 = MeterReadingSchema(value=1000, timestamp="08/19/24")
    m2 = MeterReadingSchema(value=1000, timestamp=datetime.date(year=2024, day=19, month=8))
    m3 = MeterReadingSchema(value=1000, timestamp=datetime.datetime(year=2024, day=19, month=8))
    assert isinstance(m1.timestamp, datetime.datetime)
    assert isinstance(m2.timestamp, datetime.datetime)
    assert isinstance(m3.timestamp, datetime.datetime)
    with pytest.raises(ValidationError):
        MeterReadingSchema(value=1000, timestamp=None)


def test_task_schema():
    t1 = TaskSchema(
        description="Descriptuion",
        meter_interval=100,
        due_meter_reading=1000,
        due_date=datetime.date(year=2024, day=19, month=8),
        time_interval=1,
        notes=None,
        machine_id="dummpy",
        completed_date=None,
    )
    t1.model_dump_json()
    t2 = TaskSchema(
        description="Descriptuion",
        meter_interval=100,
        due_meter_reading=1000,
        due_date=datetime.date(year=2024, day=19, month=8),
        time_interval=1,
        notes=None,
        machine_id="dummpy",
        completed_date=datetime.date(year=2024, day=19, month=8),
    )
    assert t2.model_dump()["completed_date"] == "08/19/2024"
    assert t1.model_dump()["completed_date"] is None


@pytest.mark.asyncio
async def test_get_machines():
    await init()
    await create_machine_via_service()
    response = await get_machines_via_api()

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["year"] == 2025
    assert len(response.json()[0]["tasks"]) == 2
    assert len(response.json()[0]["meter_readings"]) == 1
    assert response.json()[0]["name"] == "2025 Test Machine"
    assert response.json()[0]["purchase_date"] == "08/19/2024"


@pytest.mark.asyncio
async def test_get_machine():
    await init()
    machine = await create_machine_via_service()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/machines/{machine.id}")
        assert response.status_code == 200
        assert response.json()["year"] == 2025
        assert len(response.json()["tasks"]) == 2
        assert len(response.json()["meter_readings"]) == 1
        assert response.json()["name"] == "2025 Test Machine"
        assert response.json()["purchase_date"] == "08/19/2024"


@pytest.mark.asyncio
async def test_get_machine_missing():
    await init()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/machines/dummy")
        assert response.status_code == 404


@pytest.mark.asyncio()
async def test_create_machine():
    await init()
    response = await create_machine_via_api()
    assert response.status_code == 200
    assert response.json()["year"] == 2025
    assert len(response.json()["tasks"]) == 0
    assert len(response.json()["meter_readings"]) == 0
    assert response.json()["name"] == "2025 Test Machine 2"
    assert response.json()["purchase_date"] == "08/19/2024"


@pytest.mark.asyncio
async def test_update_machine():
    await init()
    response = await create_machine_via_api()

    machine_id = response.json()["id"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.patch(
            f"/api/v1/machines/{machine_id}",
            json={
                "year": 2026,
                "purchase_date": "08/19/2024",
            },
        )
        assert response.status_code == 200
        assert response.json()["year"] == 2026
        assert len(response.json()["tasks"]) == 0
        assert len(response.json()["meter_readings"]) == 0
        assert response.json()["name"] == "2026 Test Machine 2"
        assert response.json()["purchase_date"] == "08/19/2024"


@pytest.mark.asyncio
async def test_update_machine_missing():
    await init()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.patch(
            "/api/v1/machines/dummy",
            json={
                "year": 2026,
                "purchase_date": "08/19/2024",
            },
        )
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_record_reading():
    await init()
    response = await create_machine_via_api()
    machine_id = response.json()["id"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            f"/api/v1/machines/{machine_id}/readings",
            json={"timestamp": datetime.datetime.now().isoformat(), "value": 2000},
        )
        assert response.status_code == 200
        assert response.json()["value"] == 2000

        response = await get_machine_via_api(machine_id)

        assert response.status_code == 200
        assert response.json()["year"] == 2025
        assert len(response.json()["tasks"]) == 0
        assert len(response.json()["meter_readings"]) == 1
        assert response.json()["name"] == "2025 Test Machine 2"
        assert response.json()["purchase_date"] == "08/19/2024"


@pytest.mark.asyncio
async def test_create_and_delete_task_no_supplies():
    await init()
    response = await create_machine_via_api()
    machine_id = response.json()["id"]

    response = await create_task_via_api(machine_id)
    assert response.status_code == 200
    task = response.json()
    assert task["due_date"] == "08/30/2024"
    response = await delete_task_via_api(machine_id, task["id"])

    assert response.status_code == 200
    assert response.json()["due_date"] == "08/30/2024"

    response = await get_task_via_api(machine_id, task["id"])
    assert response.status_code == 404
    response = await get_tasks_via_api(machine_id)
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_complete_task():
    await init()
    response = await create_machine_via_api()
    machine_id = response.json()["id"]

    response = await create_task_via_api(machine_id)
    assert response.status_code == 200
    task = response.json()
    assert task["due_date"] == "08/30/2024"
    response = await complete_task_via_api(machine_id, task["id"])

    assert response.status_code == 200
    assert response.json()["due_date"] == "08/30/2024"
    assert response.json()["completed_date"] == "08/19/2024"
    assert response.json()["completed"] is True

    response = await get_task_via_api(machine_id, task["id"])
    assert response.status_code == 200
    response = await get_tasks_via_api(machine_id)
    assert response.status_code == 200
    assert len(response.json()) == 1


# @pytest.mark.asyncio(scope="session", autouse=True)
# async def test_update_task(machine):
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
#         response = await ac.post(
#             f"/api/v1/machines/{machine.id}/readings",
#             json={"timestamp": datetime.datetime.now().isoformat(), "value": 2000},
#         )
#         logging.warning(response.content)
#         assert response.status_code == 200
#         assert response.json()["value"] == 2000
#         response = await ac.get(
#             f"/api/v1/machines/{machine.id}",
#         )
#         assert response.status_code == 200
#         assert response.json()["year"] == 2025
#         assert len(response.json()["tasks"]) == 2
#         assert len(response.json()["meter_readings"]) == 2
#         assert response.json()["name"] == "2025 Test Machine"
#         assert response.json()["purchase_date"] == "08/19/2024"


@pytest.mark.asyncio
async def test_delete_task():
    await init()
    response = await create_machine_via_api()
    machine = response.json()
    response = await create_task_via_api(machine["id"])
    task = response.json()

    response = await delete_task_via_api(machine["id"], task["id"])

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_machine():
    await init()
    response = await create_machine_via_api()
    machine = response.json()
    response = await delete_machine_via_api(machine["id"])
    assert response.status_code == 200
    assert response.json()["year"] == 2025
    assert len(response.json()["tasks"]) == 0
    assert len(response.json()["meter_readings"]) == 0
    assert response.json()["name"] == "2025 Test Machine 2"
    assert response.json()["purchase_date"] == "08/19/2024"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/machines")
        assert response.status_code == 200
        assert len(response.json()) == 0


# @pytest.mark.asyncio(scope="session")
# async def test_reconcile_tasks_create_from_convoy(machine):
#     await service.reconcile_tasks(machine)
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
#         response = await ac.get("/api/v1/machines")
#         assert response.status_code == 200
#         assert len(response.json()[0]["tasks"]) == 2
#         task1 = response.json()[0]["tasks"][0]
#         task2 = response.json()[0]["tasks"][1]

#         assert task1.get("todoist_task_id") is not None
#         assert task2.get("todoist_task_id") is not None

#         td_task1 = await service.todoist.get_task(task1.get("todoist_task_id"))
#         td_task2 = await service.todoist.get_task(task2.get("todoist_task_id"))

#         assert td_task1
#         assert td_task1.content == task1.get("description")

#         assert td_task2
#         assert td_task2.content == task2.get("description")


# @pytest.mark.asyncio(scope="session")
# async def test_reconcile_tasks_delete_from_convoy(machine):
#     await service.reconcile_tasks(machine)
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
#         response = await ac.get("/api/v1/machines")
#         assert response.status_code == 200
#         assert len(response.json()[0]["tasks"]) == 2
#         task1 = response.json()[0]["tasks"][0]
#         task2 = response.json()[0]["tasks"][1]

#         assert task1.get("todoist_task_id") is not None
#         assert task2.get("todoist_task_id") is not None

#         td_task1 = await service.todoist.get_task(task1.get("todoist_task_id"))
#         td_task2 = await service.todoist.get_task(task2.get("todoist_task_id"))

#         assert td_task1
#         assert td_task1.content == task1.get("description")

#         assert td_task2
#         assert td_task2.content == task2.get("description")

#         await service.delete_task(machine.id, task1["id"])

#         response = await ac.get("/api/v1/machines")
#         assert response.status_code == 200
#         assert len(response.json()[0]["tasks"]) == 1

#         with pytest.raises(Exception):
#             await service.todoist.get_task(task1["todoist_task_id"])
#         await service.todoist.get_task(task2["todoist_task_id"])


# @pytest.mark.asyncio(scope="session")
# async def test_reconcile_tasks_complete_from_todoist(machine):
#     logging.info("Reconciling at the start")
#     await service.reconcile_tasks(machine)
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
#         response = await ac.get("/api/v1/machines")
#         assert response.status_code == 200
#         assert len(response.json()[0]["tasks"]) == 2
#         task1 = response.json()[0]["tasks"][0]
#         task2 = response.json()[0]["tasks"][1]

#         assert task1.get("todoist_task_id") is not None
#         assert task2.get("todoist_task_id") is not None

#         td_task1 = await service.todoist.get_task(task1.get("todoist_task_id"))
#         td_task2 = await service.todoist.get_task(task2.get("todoist_task_id"))

#         assert td_task1
#         assert td_task1.content == task1.get("description")

#         assert td_task2
#         assert td_task2.content == task2.get("description")

#         await service.todoist.close_task(task2["todoist_task_id"])
#         logging.info(f"Reconciling after closing task {task2}")
#         await service.reconcile_tasks(machine)
#         should_be_reopened = await service.todoist.get_task(task2["todoist_task_id"])
#         assert should_be_reopened.is_completed is False
