import pytest
from fastapi.testclient import TestClient

from ..main.main import app
from .utils import create_machine_via_api


@pytest.mark.asyncio
async def test_startup():
    with TestClient(app):
        await create_machine_via_api()
