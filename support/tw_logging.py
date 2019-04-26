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
    _project_id = 376160
    def set_teamwork(self, tw:teamworkapi.Connect):
        self._teamwork = tw
    
    def set_log_level(self, level:LOG_LEVEL):
        self._log_level = level

    # Project ID for logging messages
    def set_project_id(self, project_id:int):
        self._project_id = project_id

    # Method to get category by string name or create a new category. Returns the id to use in message.
    def get_category_id(self, level:LOG_LEVEL):
        return ""
    
    # Gets list of user ids to notify for messages
    def get_users_to_notify(self):
        return ""

    def post_message(self, level:LOG_LEVEL, title:str, message:str):
        if self._log_level is None:
            return
        elif level.value >= self._log_level.value:
            category_id = self.get_category_id(level)
            notify_users = self.get_users_to_notify()
            return self._teamwork.post_message(self._project_id, title, message,notify_user_ids=notify_users, category_id=category_id)

    def info(self, title:str, message:str):
        return self.post_message(LOG_LEVEL.INFO, title, message)

    def warning(self, title:str, message:str):
        return self.post_message(LOG_LEVEL.WARNING, title, message)

    def error(self, title:str, message:str):
        return self.post_message(LOG_LEVEL.ERROR, title, message)

    def critical(self, title:str, message:str):
        return self.post_message(LOG_LEVEL.CRITICAL, title, message)
    
log = logger()