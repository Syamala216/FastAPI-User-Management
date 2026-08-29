import logging
from pathlib import Path
from datetime import datetime


LOG_DIR = Path("logs")


LOG_FORMAT = (
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)


class DailyFileHandler(logging.Handler):
    def __init__(self, logger_type):
        super().__init__()

        self.logger_type = logger_type
        self.current_date = None
        self.file_handler = None

        self._update_handler()

    def _get_log_file(self):
        now = datetime.now()

        year = now.strftime("%Y")
        week = now.strftime("%V")
        date = now.strftime("%Y-%m-%d")

        day_folder = (
            LOG_DIR
            / year
            / f"Week_{week}"
            / date
        )

        day_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        return day_folder / f"{self.logger_type}.log"

    def _update_handler(self):
        today = datetime.now().date()

        if self.current_date == today:
            return

        if self.file_handler:
            self.file_handler.close()

        log_file = self._get_log_file()

        self.file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8"
        )

        self.file_handler.setFormatter(
            logging.Formatter(LOG_FORMAT)
        )

        self.current_date = today

    def emit(self, record):
        try:
            self._update_handler()
            self.file_handler.emit(record)

        except Exception:
            self.handleError(record)

    def close(self):
        if self.file_handler:
            self.file_handler.close()

        super().close()




info_logger = logging.getLogger("info_logger")
info_logger.setLevel(logging.INFO)
info_logger.propagate = False

if not info_logger.handlers:
    info_handler = DailyFileHandler("info")
    info_handler.setLevel(logging.INFO)

    info_logger.addHandler(info_handler)


warning_logger = logging.getLogger("warning_logger")
warning_logger.setLevel(logging.WARNING)
warning_logger.propagate = False

if not warning_logger.handlers:
    warning_handler = DailyFileHandler("warning")
    warning_handler.setLevel(logging.WARNING)

    warning_logger.addHandler(warning_handler)



# --------------------------------------------------

error_logger = logging.getLogger("error_logger")
error_logger.setLevel(logging.ERROR)
error_logger.propagate = False

if not error_logger.handlers:
    error_handler = DailyFileHandler("error")
    error_handler.setLevel(logging.ERROR)

    error_logger.addHandler(error_handler)