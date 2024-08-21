from contextlib import asynccontextmanager
from .utils import (
    custom_generate_unique_id,
)
from fastapi import FastAPI

from .service import convoy_service
from .router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    await convoy_service.init_models()
    yield
    # Clean up the ML models and release the resources


app = FastAPI(generate_unique_id_function=custom_generate_unique_id, separate_input_output_schemas=False, lifespan=lifespan)
app.include_router(router)

# @app.middleware("http")
# async def add_custom_header(request, call_next):
#     response = await call_next(request)
#     if response.status_code == 404:
#         return FileResponse("static/index.html")
#     return response


# @app.exception_handler(404)
# def not_found(request, exc):
#     return FileResponse("static/index.html")


# app.mount("/ui", StaticFiles(directory="static"), name="static")
