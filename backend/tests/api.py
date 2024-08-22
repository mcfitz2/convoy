import datetime
import logging

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from ..main.main import app
from .utils import (
    complete_task_via_api,
    create_machine_via_api,
    create_machine_via_service,
    create_supply_via_api,
    create_task_via_api,
    delete_machine_via_api,
    delete_supply_via_api,
    delete_task_via_api,
    get_machine_via_api,
    get_machines_via_api,
    get_supplies_via_api,
    get_supply_via_api,
    get_task_via_api,
    get_tasks_via_api,
    init,
    update_supply_via_api,
)

client = TestClient(app)



@pytest.mark.asyncio
async def test_get_machines():
    await init()
    await create_machine_via_service()
    response = await get_machines_via_api()

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["year"] == 2025
    assert len(response.json()[0]["tasks"]) == 4
    assert len(response.json()[0]["meter_readings"]) == 1
    assert response.json()[0]["purchase_date"] == "08/19/2024"


@pytest.mark.asyncio
async def test_get_machine():
    await init()
    machine = await create_machine_via_service()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/machines/{machine.id}")
        assert response.status_code == 200
        assert response.json()["year"] == 2025
        assert len(response.json()["tasks"]) == 4
        assert len(response.json()["meter_readings"]) == 1
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
    assert len(response.json()["meter_readings"]) == 1
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
        assert len(response.json()["meter_readings"]) == 1
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
async def test_get_task_missing():
    await init()
    machine = (await create_machine_via_api()).json()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/machines/{machine['id']}/tasks/dummy")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_task_missing():
    await init()
    machine = (await create_machine_via_api()).json()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete(f"/api/v1/machines/{machine['id']}/tasks/dummy")
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
        assert len(response.json()["meter_readings"]) == 2
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


@pytest.mark.asyncio
async def test_complete_recurring_task():
    await init()
    response = await create_machine_via_api()
    machine_id = response.json()["id"]

    response = await create_task_via_api(machine_id, recurring=True)
    assert response.status_code == 200
    task = response.json()
    assert task["due_date"] == "08/30/2024"
    assert task["recurring"] is True

    response = await get_task_via_api(machine_id, task["id"])
    assert response.status_code == 200
    task = response.json()
    assert task["due_date"] == "08/30/2024"
    assert task["recurring"] is True

    response = await complete_task_via_api(machine_id, task["id"])

    assert response.status_code == 200
    assert response.json()["due_date"] == "08/30/2024"
    assert response.json()["completed_date"] == "08/19/2024"
    assert response.json()["completed"] is True

    response = await get_task_via_api(machine_id, task["id"])
    assert response.status_code == 200
    response = await get_tasks_via_api(machine_id)
    assert response.status_code == 200
    assert len(response.json()) == 2

    assert len([t for t in response.json() if t["completed"] is True]) == 1
    assert len([t for t in response.json() if t["completed"] is False]) == 1
    desc = [t["description"] for t in response.json()]
    time_int = [t["meter_interval"] for t in response.json()]
    meter_int = [t["time_interval"] for t in response.json()]
    assert len(set(desc)) == 1
    assert len(set(meter_int)) == 1
    assert len(set(time_int)) == 1


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
    assert len(response.json()["meter_readings"]) == 1
    assert response.json()["purchase_date"] == "08/19/2024"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/machines")
        assert response.status_code == 200
        assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_create_supply():
    await init()
    response = await create_supply_via_api()
    assert response.status_code == 200
    assert response.json()["machine_id"] is None
    assert response.json()["quantity_on_hand"] == 2
    assert response.json()["unit"] == "each"
    assert response.json()["name"] == "Oil Filter"


@pytest.mark.asyncio
async def test_create_supply_machine_specific():
    await init()
    response = await create_machine_via_api()
    machine = response.json()
    response = await create_supply_via_api(machine["id"])
    assert response.status_code == 200
    assert response.json()["machine_id"] == machine["id"]
    assert response.json()["quantity_on_hand"] == 2
    assert response.json()["unit"] == "each"
    assert response.json()["name"] == "Oil Filter"


@pytest.mark.asyncio
async def test_update_supply():
    await init()
    response = await create_supply_via_api()
    assert response.status_code == 200
    assert response.json()["machine_id"] is None
    assert response.json()["quantity_on_hand"] == 2
    assert response.json()["unit"] == "each"
    assert response.json()["name"] == "Oil Filter"

    response = await update_supply_via_api(response.json()['id'])
    assert response.status_code == 200
    logging.warning(response.content)
    assert response.json()["machine_id"] is None
    assert response.json()["quantity_on_hand"] == 1000
    assert response.json()["unit"] == "each"
    assert response.json()["name"] == "Oil Filter"
    
@pytest.mark.asyncio
async def test_delete_supply():
    await init()
    response = await create_supply_via_api()
    assert response.status_code == 200
    assert response.json()["machine_id"] is None
    assert response.json()["quantity_on_hand"] == 2
    assert response.json()["unit"] == "each"
    assert response.json()["name"] == "Oil Filter"

    response = await delete_supply_via_api(response.json()["id"])
    assert response.status_code == 200
    assert response.json()["machine_id"] is None
    assert response.json()["quantity_on_hand"] == 2
    assert response.json()["unit"] == "each"
    assert response.json()["name"] == "Oil Filter"


@pytest.mark.asyncio
async def test_get_supply():
    await init()
    response = await create_supply_via_api()
    assert response.status_code == 200
    assert response.json()["machine_id"] is None
    assert response.json()["quantity_on_hand"] == 2
    assert response.json()["unit"] == "each"
    assert response.json()["name"] == "Oil Filter"

    response = await get_supply_via_api(response.json()["id"])
    assert response.status_code == 200
    assert response.json()["name"] == "Oil Filter"


@pytest.mark.asyncio
async def test_get_supply_missing():
    await init()
    response = await get_supply_via_api("dummy")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_supplies():
    await init()
    await create_supply_via_api(name="Rags")
    await create_supply_via_api(name="Wrench")
    await create_supply_via_api(name="Carb Cleaner")

    response = await get_supplies_via_api()
    assert response.status_code == 200
    assert len(response.json()) == 3

    ids = [s["id"] for s in response.json()]
    names = [s["name"] for s in response.json()]
    assert len(ids) == len(set(ids))
    assert len(names) == len(set(names))




