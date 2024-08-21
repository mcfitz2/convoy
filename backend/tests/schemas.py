import datetime
from pydantic import ValidationError
import pytest

from ..main.models import MeterReadingSchema, PartSchema, MachineSchema, TaskCompleteSchema, TaskSchema

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

    t3 = TaskCompleteSchema(completed_date=datetime.date(year=2024, day=19, month=8), completed_meter_reading=10000)
    assert t3.model_dump()["completed_date"] == "08/19/2024"


def test_part_schema():
    PartSchema(name="MXL 4050", link="http://valid-url.com", supply_id="dummy")
