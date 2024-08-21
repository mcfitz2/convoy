import pytest

from ..main.service import convoy_service as service
from .utils import (
    create_machine_via_api,
    create_task_via_api,
    delete_all_doist_tasks,
    delete_task_via_api,
    get_task_via_api,
    get_tasks_via_api,
    init,
)


@pytest.mark.asyncio
async def test_reconcile_tasks_create_from_convoy():
    await init()
    await delete_all_doist_tasks()
    machine = (await create_machine_via_api()).json()
    task_response = await create_task_via_api(machine["id"])
    task = task_response.json()
    assert task.get("todoist_task_id") is not None
    td_task1 = await service.todoist.get_task(task.get("todoist_task_id"))
    assert td_task1
    assert td_task1.content == task.get("description")
    await delete_all_doist_tasks()


@pytest.mark.asyncio
async def test_reconcile_tasks_delete_from_convoy():
    await init()
    await delete_all_doist_tasks()
    machine = (await create_machine_via_api()).json()
    task_response = await create_task_via_api(machine["id"])

    task = task_response.json()
    assert task.get("todoist_task_id") is not None
    td_task1 = await service.todoist.get_task(task.get("todoist_task_id"))
    assert td_task1
    assert td_task1.content == task.get("description")

    task_delete_response = await delete_task_via_api(machine_id=machine["id"], task_id=task["id"])
    assert task_delete_response.status_code == 200

    tasks = await get_tasks_via_api(machine_id=machine["id"])
    assert tasks.status_code == 200
    assert len(tasks.json()) == 0

    with pytest.raises(Exception):
        await service.todoist.get_task(task["todoist_task_id"])
    await delete_all_doist_tasks()


@pytest.mark.asyncio
async def test_reconcile_tasks_complete_from_todoist():

    await init()
    await delete_all_doist_tasks()
    machine = (await create_machine_via_api()).json()
    task_response = await create_task_via_api(machine["id"])

    task = task_response.json()
    assert task.get("todoist_task_id") is not None
    td_task1 = await service.todoist.get_task(task.get("todoist_task_id"))
    assert td_task1
    assert td_task1.content == task.get("description")

    await service.todoist.close_task(task["todoist_task_id"])
    await service.reconcile_all_tasks()
    should_be_reopened = await service.todoist.get_task(task["todoist_task_id"])
    assert should_be_reopened.is_completed is False

    await delete_all_doist_tasks()


@pytest.mark.asyncio
async def test_reconcile_tasks_delete_from_todoist():

    await init()
    await delete_all_doist_tasks()
    machine = (await create_machine_via_api()).json()
    task_response = await create_task_via_api(machine["id"])

    task = task_response.json()
    assert task.get("todoist_task_id") is not None
    td_task = await service.todoist.get_task(task.get("todoist_task_id"))
    assert td_task
    assert td_task.content == task.get("description")
    old_td_task_id = td_task.id
    old_todoist_task_id = task["todoist_task_id"]

    await service.todoist.delete_task(task["todoist_task_id"])
    await service.reconcile_all_tasks()

    reconciled_task = (await get_task_via_api(machine["id"], task["id"])).json()

    assert reconciled_task["todoist_task_id"] != old_td_task_id
    assert reconciled_task["todoist_task_id"] != old_todoist_task_id

    should_exist = await service.todoist.get_task(reconciled_task["todoist_task_id"])
    assert should_exist
    assert should_exist.content == reconciled_task.get("description")

    await delete_all_doist_tasks()


@pytest.mark.asyncio
async def test_reconcile_tasks_no_changes():

    await init()
    await delete_all_doist_tasks()
    machine = (await create_machine_via_api()).json()
    task_response = await create_task_via_api(machine["id"])

    task = task_response.json()
    assert task.get("todoist_task_id") is not None
    td_task = await service.todoist.get_task(task.get("todoist_task_id"))
    assert td_task
    assert td_task.content == task.get("description")

    await service.reconcile_all_tasks()

    await delete_all_doist_tasks()
