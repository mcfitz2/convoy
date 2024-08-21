from fastapi.testclient import TestClient
import pytest

from .utils import create_machine_via_api
from ..main.main import app

@pytest.mark.asyncio
async def test_startup():
    with TestClient(app):
        await create_machine_via_api()
