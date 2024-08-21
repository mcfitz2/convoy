import datetime
import logging
import sys
import uuid

from dateutil.parser import parse
from fastapi.routing import APIRoute
from urllib3 import Retry

engine = None


class LogRetry(Retry):
    def __init__(self, *args, **kwargs):
        logger = setup_logger("HTTP Retry")
        logger.info(
            f"Encountered HTTP Status {kwargs.get('status', '-')} for URL {kwargs.get('method')} {kwargs.get('url')}, retrying. {kwargs.get('total')} tries left"
        )
        super().__init__(*args, **kwargs)


def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stdout)
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)
    return logger


def uuid_gen():
    return uuid.uuid4().hex


def custom_generate_unique_id(route: APIRoute):
    return f"{route.name}"


def parse_date(cls, value) -> datetime.date:
    if not value:
        return value
    if isinstance(value, datetime.datetime):
        return value.date()
    elif isinstance(value, datetime.date):
        return value
    else:
        return parse(value).date()


def parse_timestamp(cls, value) -> datetime.datetime:
    if not value:
        return value
    if isinstance(value, datetime.datetime):
        return value
    elif isinstance(value, datetime.date):
        return datetime.datetime(value.year, value.month, value.day)
    else:
        return parse(value)
