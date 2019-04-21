from enum import Enum
from support import teamworkapi

class LOG_LEVEL(Enum):
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class logger:
    _teamwork = None
    _log_level = None
    def set_teamwork(self, tw:teamworkapi.Connect):
        self._teamwork = tw
    
    def set_log_level(self, level:LOG_LEVEL):
        self._log_level = level

log = logger()

def warning(message):
    pass

def error(message):
    pass

def critical(message):
    pass
