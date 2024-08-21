from .service import ConvoyService, convoy_service


def get_service() -> ConvoyService:
    return convoy_service


# async def valid_machine_id(machine_id: str) -> Machine:
#     machine = await machine_service.get_machine(machine_id)
#     if not machine:
#         raise MachineNotFound()

#     return machine


# async def machine_readings(machine_id: str) -> List[MeterReadingPublic]:
#     return await machine_service.get_meter_readings(machine_id)
