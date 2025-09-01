import logging
import sys
from typing import Optional

_HAS_CONFIGURED = False

def setup_logging(level: str | int = "INFO", *, json: bool = False) -> None:
    """Configure root logging once.

    Args:
        level: Logging level ("DEBUG", "INFO", etc.) or numeric.
        json: If True, log as JSON lines (very basic); else human-readable.
    """
    global _HAS_CONFIGURED
    if _HAS_CONFIGURED:
        return

    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)

    if json:
        class JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                payload = {
                    "level": record.levelname,
                    "name": record.name,
                    "msg": record.getMessage(),
                }
                if record.exc_info:
                    payload["exc_info"] = self.formatException(record.exc_info)
                # Manual JSON to avoid dependency
                import json as _json
                return _json.dumps(payload, ensure_ascii=False)
        fmt = JsonFormatter()
    else:
        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )

    handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(level)
    # Avoid duplicate handlers if re-run in REPL
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        root.addHandler(handler)
    else:
        root.handlers.clear()
        root.addHandler(handler)

    _HAS_CONFIGURED = True

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a module-level logger; ensures logging is configured."""
    if not _HAS_CONFIGURED:
        setup_logging()
    return logging.getLogger(name or __name__)
