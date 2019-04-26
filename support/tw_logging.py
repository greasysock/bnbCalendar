from enum import Enum
from support import teamworkapi

class LOG_LEVEL(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3

level_names = {
    0 : "Info",
    1 : "Warning",
    2 : "Error",
    3 : "Critical"
}

class logger:
    _teamwork = None
    _log_level = None
    def set_teamwork(self, tw:teamworkapi.Connect):
        self._teamwork = tw
    
    def set_log_level(self, level:LOG_LEVEL):
        self._log_level = level

    def post_message(self, level:LOG_LEVEL, title:str, message:str):
        if self._log_level is None:
            return
        elif level.value >= self._log_level.value:
            return

    def info(self, title:str, message:str):
        return self.post_message(LOG_LEVEL.INFO, title, message)

    def warning(self, title:str, message:str):
        return self.post_message(LOG_LEVEL.WARNING, title, message)

    def error(self, title:str, message:str):
        return self.post_message(LOG_LEVEL.ERROR, title, message)

    def critical(self, title:str, message:str):
        return self.post_message(LOG_LEVEL.CRITICAL, title, message)
    
log = logger()