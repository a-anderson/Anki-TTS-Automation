from logging import Handler, LogRecord
from tqdm import tqdm

class TqdmLoggingHandler(Handler):
    """A logging handler that integrates with tqdm progress bars."""

    def emit(self, record: LogRecord) -> None:
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)
