import logging

logger = logging.Logger(__name__)


class FlightNotFoundException(Exception):
    def __init__(self, call_sign: str):
        super()

        logger.info(f"Could not found flight with call sign {call_sign}.")
