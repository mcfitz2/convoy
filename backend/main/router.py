from typing import List

from .utils import setup_logger
from .dependencies import get_service
from .service import ConvoyService

from .models import Machine, MachineSchema, MachineUpdateSchema, MeterReading, MeterReadingSchema, SupplySchema, Task, TaskCompleteSchema, TaskCreateSchema, TaskSchema
from fastapi import Depends

from fastapi import APIRouter

logger = setup_logger("Router")

router = APIRouter()


@router.patch("/api/v1/machines/{machine_id}", response_model=MachineSchema)
async def update_machine(machine_id: str, new_machine: MachineUpdateSchema, service: ConvoyService = Depends(get_service)) -> MachineSchema:
    updated = await service.update_machine(machine_id, new_machine.model_dump(exclude_none=True, exclude_unset=True))
    return updated


@router.delete("/api/v1/machines/{machine_id}", response_model=MachineSchema)
async def delete_machine(machine_id: str, service: ConvoyService = Depends(get_service)) -> MachineSchema:
    return MachineSchema.model_validate(await service.delete_machine(machine_id))


@router.post("/api/v1/machines", response_model=MachineSchema)
async def create_machine(new_machine: MachineSchema, service: ConvoyService = Depends(get_service)) -> MachineSchema:
    return MachineSchema.model_validate(await service.create_machine(Machine.from_schema(new_machine)))


@router.get("/api/v1/machines/{machine_id}", response_model=MachineSchema)
async def get_machine(machine_id: str, service: ConvoyService = Depends(get_service)) -> MachineSchema:
    return MachineSchema.model_validate(await service.get_machine(machine_id))


@router.post("/api/v1/machines/{machine_id}/readings", response_model=MeterReadingSchema)
async def create_reading(machine_id: str, reading: MeterReadingSchema, service: ConvoyService = Depends(get_service)) -> MeterReadingSchema:
    if not reading.machine_id:
        reading.machine_id = machine_id
    reading = await service.record_reading(machine_id, MeterReading.from_schema(reading))
    return MeterReadingSchema.model_validate(reading)


@router.get("/api/v1/machines", response_model=List[MachineSchema])
async def get_machines(service: ConvoyService = Depends(get_service)) -> List[MachineSchema]:
    return [MachineSchema.model_validate(m) for m in await service.get_machines()]


@router.delete("/api/v1/machines/{machine_id}/tasks/{task_id}", response_model=TaskSchema)
async def delete_task(task_id: str, machine_id: str, service: ConvoyService = Depends(get_service)) -> TaskSchema:
    return TaskSchema.model_validate(await service.delete_task(machine_id, task_id))


@router.get("/api/v1/machines/{machine_id}/tasks/{task_id}", response_model=TaskSchema)
async def get_task(task_id: str, machine_id: str, service: ConvoyService = Depends(get_service)) -> TaskSchema:
    return TaskSchema.model_validate(await service.get_task(machine_id, task_id))


@router.get("/api/v1/machines/{machine_id}/tasks", response_model=List[TaskSchema])
async def get_tasks(machine_id: str, service: ConvoyService = Depends(get_service)) -> List[TaskSchema]:
    return [TaskSchema.model_validate(t) for t in await service.get_tasks(machine_id)]


@router.post("/api/v1/machines/{machine_id}/tasks", response_model=TaskSchema)
async def create_task(
    machine_id: str,
    task: TaskCreateSchema,
    service: ConvoyService = Depends(get_service),
) -> TaskSchema:
    created: Task = await service.create_task(machine_id, Task.from_schema(task))
    return TaskSchema.model_validate(created)


@router.post("/api/v1/machines/{machine_id}/tasks/{task_id}/complete", response_model=TaskSchema)
async def complete_task(task: TaskCompleteSchema, machine_id: str, task_id: str, service: ConvoyService = Depends(get_service)) -> TaskSchema:
    updated = await service.complete_task(machine_id, task_id, completed_date=task.completed_date, completed_meter_reading=task.completed_meter_reading, notes=task.notes)
    return updated


@router.patch("/api/v1/supplies/{supply_id}", response_model=SupplySchema)
async def update_supply(
    supply_id: str,
    supply: SupplySchema,
    service: ConvoyService = Depends(get_service),
) -> SupplySchema:
    updated = await service.update_supply(supply_id, supply)
    return updated


@router.get("/api/v1/supplies", response_model=List[SupplySchema])
async def get_supplies(service: ConvoyService = Depends(get_service)) -> List[SupplySchema]:
    return await service.get_supplies()


@router.post("/api/v1/supplies", response_model=SupplySchema)
async def create_supply(supply: SupplySchema, service: ConvoyService = Depends(get_service)) -> SupplySchema:
    created = await service.create_supply(supply)
    return created


@router.delete("/api/v1/supplies/{supply_id}", response_model=SupplySchema)
async def delete_supply(supply_id, service: ConvoyService = Depends(get_service)) -> SupplySchema:
    deleted = await service.delete_supply(supply_id)
    return deleted
