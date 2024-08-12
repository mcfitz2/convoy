import uuid
from fastapi.routing import APIRoute
from sqlalchemy.schema import CreateSchema  # type: ignore
from sqlmodel import Session, create_engine
import os

engine = None


def uuid_gen():
    return uuid.uuid4().hex


def get_session():
    engine = get_engine()
    with Session(engine) as session:
        yield session


def get_engine():
    if engine:
        return engine
    else:
        return setup_engine()


def custom_generate_unique_id(route: APIRoute):
    return f"{route.name}"


def setup_engine():
    if os.environ["ENV"] == "development":
        sqlite_file_name = "convoy.db"
        sqlite_url = f"sqlite:///{sqlite_file_name}"
        engine = create_engine(sqlite_url, echo=True, pool_size=50, max_overflow=100)
    elif os.environ["ENV"] == "production":
        engine = create_engine(
            f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}",
            connect_args={"options": f"-csearch_path={os.environ['DB_SCHEMA']}"},
            pool_size=50,
            max_overflow=100,
        )
        with engine.connect() as connection:
            connection.execute(
                CreateSchema(os.environ["DB_SCHEMA"], if_not_exists=True)
            )
            connection.commit()
    return engine
