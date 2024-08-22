
import pytest
from fastapi.testclient import TestClient

from ..main.main import app
from ..main.service import convoy_service as service
from .utils import (
    create_machine_via_service,
    create_machine_via_service_no_readings,
    init,
)

client = TestClient(app)



@pytest.mark.asyncio
async def test_get_tasks_by_state():
    await init()
    machine = await create_machine_via_service()

    current_meter = await service.get_current_meter_reading(machine.id)
    assert current_meter == 1000
    results = await service.get_all_tasks_by_state()
   
    assert len(results.completed) == 1
    assert len(results.due) == 2
    assert len(results.overdue) == 1
    assert len(results.upcoming) == 1

@pytest.mark.asyncio
async def test_create_machine_without_readings():
    await init()
    machine = await create_machine_via_service_no_readings()
    assert len(machine.meter_readings) == 1
    current_meter = await service.get_current_meter_reading(machine.id)
    assert current_meter == 0