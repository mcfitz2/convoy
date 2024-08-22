from contextlib import asynccontextmanager

from fastapi import FastAPI

from .router import router
from .service import convoy_service
from .utils import (
    custom_generate_unique_id,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await convoy_service.init_models(drop=False)
    yield


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
