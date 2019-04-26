from enum import Enum
from support import teamworkapi

class LOG_LEVEL(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3

level_names = {
    LOG_LEVEL.INFO : "Info",
    LOG_LEVEL.WARNING : "Warning",
    LOG_LEVEL.ERROR : "Error",
    LOG_LEVEL.CRITICAL : "Critical"
}

class logger:
    _teamwork = None
    _log_level = None
    _project_id = 376160
    _category_ids = {}
    _notify_users = None
    def set_teamwork(self, tw:teamworkapi.Connect):
        self._teamwork = tw
    
    def set_log_level(self, level:LOG_LEVEL):
        self._log_level = level

    # Project ID for logging messages
    def set_project_id(self, project_id:int):
        self._project_id = project_id

    # Method to get category by string name or create a new category. Returns the id to use in message.
    def get_category_id(self, level:LOG_LEVEL):
        if level in self._category_ids:
            return self._category_ids[level]
        
        # Retrieve list of categories from teamwork
        categories = self._teamwork.get_project_categories(self._project_id)
        category_name = level_names[level]
        category_id = None

        # Find category by iteration
        for category in categories["categories"]:
            if category["name"] == category_name:
                category_id = category["id"]
        
        # If category exists, store in dictionary and return id. Otherwise create category and return ID
        if category_id:
            self._category_ids[level] = category_id
            return category_id
        
        category_id = self._teamwork.post_project_category(self._project_id, category_name)
        if category_id:
            self._category_ids[level] = category_id
            return category_id
    
    # Gets list of user ids to notify for messages
    def get_users_to_notify(self):
        # Checks if value is not None and returns
        if self._notify_users:
            return self._notify_users
        
        project_users = self._teamwork.get_users_on_project(self._project_id)
        if project_users:
            self._notify_users = list()
            for user in project_users['people']:
                self._notify_users.append(user['id'])
            return self._notify_users

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