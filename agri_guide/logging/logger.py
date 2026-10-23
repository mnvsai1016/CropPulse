import logging
import sys
from logging import Logger


def _create_logger() -> Logger:
    logger_ = logging.getLogger("agri_guide")
    if logger_.handlers:
        return logger_

    logger_.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger_.addHandler(handler)

    return logger_


logger: Logger = _create_logger()








