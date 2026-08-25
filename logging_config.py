import logging
from pathlib import Path


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


LOG_FORMAT = (
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)


info_logger = logging.getLogger("info_logger")
info_logger.setLevel(logging.INFO)

info_handler = logging.FileHandler(
    LOG_DIR / "info.log"
)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(
    logging.Formatter(LOG_FORMAT)
)

info_logger.addHandler(info_handler)


warning_logger = logging.getLogger("warning_logger")
warning_logger.setLevel(logging.WARNING)

warning_handler = logging.FileHandler(
    LOG_DIR / "warning.log"
)
warning_handler.setLevel(logging.WARNING)
warning_handler.setFormatter(
    logging.Formatter(LOG_FORMAT)
)

warning_logger.addHandler(warning_handler)


error_logger = logging.getLogger("error_logger")
error_logger.setLevel(logging.ERROR)

error_handler = logging.FileHandler(
    LOG_DIR / "error.log"
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(
    logging.Formatter(LOG_FORMAT)
)

error_logger.addHandler(error_handler)