import requests, json, time, logging
from support import version

__author__ = version.get_author()
__version__ = version.get_version()
__title__ = version.get_title()

site = 'https://bnbwithme.teamwork.com'

class Connect():
    def __init__(self, api_key, site=site):
        self.__api_key = api_key
        self.__default_company = None
        self.__site = site
        self.__auth = (self.__api_key, 'pass')
        self.__header = {'user-agent':'{}/{}'.format(__title__,__version__)}
        self.__connection = self.test()
        self.__last_action = 0
    def __url_build(self, url):
        return '{}/{}'.format(self.__site,url)
    def test(self):
        site = self.__url_build('projects.json')
        r = requests.get(site, headers=self.__header, auth=self.__auth)
        try:
            rjson = r.json()
        except json.decoder.JSONDecodeError:
            rjson = {'STATUS':'FAIL'}
            logging.warning("Failed to connect to teamwork servers.")
        try:
            working = rjson['STATUS'] == 'OK'
        except KeyError:
            logging.warning("Failed to connect to teamwork servers, authentication error.")
            working = False
        return working
    def set_company(self, company):
        self.__default_company = company
    def __epochtodate(self, date, type=0):
        '''
        YYYY-MM-DDThhmmss --> Format
        '''
        if type == 0:
            return time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(date))
        elif type == 1:
            return time.strftime('%Y%m%d', time.localtime(date))
    def __remove_calendarevent(self, event_id):
        site = self.__url_build('calendarevents/{}.json'.format(event_id))
        print(site)
        r = requests.delete(site, auth=(self.__api_key, 'pass'), headers=self.__header)

        try:
            rejson = r.json()
            if rejson['STATUS'] == 'OK':
                return 1
            else:
                return -1
        except KeyError:
            return -1
        except json.decoder.JSONDecodeError:
            print(r.status_code)
            return -1
    def remove_calendarevent(self, event_id):
        if self.__connection:
            return self.__remove_calendarevent(event_id)
        else:
            return -1
    def __get_calendarentries(self, startdate, enddate):
        site = self.__url_build('calendarevents.json')
        fix_startdate = self.__epochtodate(startdate)
        fix_enddate = self.__epochtodate(enddate)
        payload = {'startdate':fix_startdate, 'endDate':fix_enddate}
        r = requests.get(site, params=payload, auth=(self.__api_key, 'pass'), headers=self.__header)
        return r.json()
    def get_calendarentries(self, startdate, enddate):
        if self.__connection:
            return self.__get_calendarentries(startdate, enddate)
        else:
            return -1
    def __post_calendarevent(self, entry_object):
        site = self.__url_build('calendarevents.json')

        fix_startdate = self.__epochtodate(entry_object.get_start())
        fix_enddate = self.__epochtodate(entry_object.get_end())
        all_day = "true"
        title = '{} - {}'.format(entry_object.get_guest(), entry_object.get_event_name())
        service = {0:"Airbnb", 1:"VRBO"}
        description = "Email: {}\nPhone: {}\n".format(entry_object.get_email(), entry_object.get_phone())
        where = service[entry_object.get_service()]
        privacy = {"type":"project", "project-id":entry_object.get_project_id()}
        type = {"id":entry_object.get_event_id()}
        attending_user_ids = ""
        show_as_busy = "false"
        notify_user_ids = "199418, 274641"
#        notify_user_ids = "274641"

        project_users_can_edit = "false"
        reminders = []

        event = {"start" : fix_startdate,
                 "end" : fix_enddate,
                 "all-day":all_day,
                 "title":title,
                 "description": description,
                 "where":where,
                 "privacy":privacy,
                 "show-as-busy":show_as_busy,
                 "type":type,
                 "attending-user-ids":attending_user_ids,
                 "notify":'true',
                 "notify-user-ids":notify_user_ids,
                 "attendees-can-edit":project_users_can_edit,
                 "project-users-can-edit":project_users_can_edit,
                 "reminders":reminders}

        payload = {"event":event}

        r = requests.post(site, json=payload,  auth=(self.__api_key, 'pass'), headers=self.__header)

        rejson = r.json()
        try:
            if rejson['STATUS'] == 'OK':
                return r.json()['id']
            else:
                return False
        except KeyError:
            print(rejson)
            return False
    def post_calendarevent(self, entry_object):
        if self.__connection:
            return self.__post_calendarevent(entry_object)
        else:
            return False
    def __post_calendarevent_cleaning(self, **kwargs):
        site = self.__url_build('calendarevents.json')

        start_fix = self.__epochtodate(kwargs['start'])
        end_fix = self.__epochtodate(kwargs['end'])

        all_day = "true"
        privacy = {"type":"project", "project-id":kwargs['project_id']}
        type = {"id":kwargs['event_id']}
        attending_user_ids = ""
        show_as_busy = "false"
        notify_user_ids = "201024"
#        notify_user_ids = ""

        project_users_can_edit = "false"
        reminders = []

        event = {"start" : start_fix,
                 "end" : end_fix,
                 "all-day":all_day,
                 "title": kwargs['title'],
                 "description": kwargs['description'],
                 "where": kwargs['where'],
                 "privacy": privacy,
                 "show-as-busy": show_as_busy,
                 "type": type,
                 "attending-user-ids": attending_user_ids,
                 "notify-user-ids": notify_user_ids,
                 "notify": 'true',
                 "attendees-can-edit": project_users_can_edit,
                 "project-users-can-edit": project_users_can_edit,
                 "reminders":reminders}

        payload = {"event":event}

        r = requests.post(site, json=payload,  auth=(self.__api_key, 'pass'), headers=self.__header)

        rejson = r.json()
        try:
            if rejson['STATUS'] == 'OK':
                return r.json()['id']
            else:
                return False
        except KeyError:
            print(rejson)
            return False
    def post_calendarevent_cleaning(self, **kwargs):
        if self.__connection:
            return self.__post_calendarevent_cleaning(**kwargs)
        else:
            return False
    def __get_projects(self):
        site = self.__url_build('companies/{}/projects.json'.format(self.__default_company))
        r = requests.get(site, auth=(self.__api_key, 'pass'), headers=self.__header)
        projects_pack = r.json()
        out_list = list()
        for project in projects_pack['projects']:
            out_tup = (project['id'], project['name'])
            out_list.append(out_tup)
        return out_list
    def get_projects(self):
        if self.__connection:
            return self.__get_projects()
        else:
            return -1
    def __get_users_on_project(self, project_id):
        site = self.__url_build('projects/{}/people.json'.format(project_id))
        r = requests.get(site, auth=(self.__api_key, 'pass'), headers=self.__header)
        users_pack = r.json()
        out_list = list()
        for user in users_pack['people']:
            out_tup = (user['id'], )
        return users_pack
    def get_users_on_project(self, project_id):
        if self.__connection:
            return self.__get_users_on_project(project_id)
        else:
            return -1
    def __get_calendar_events(self):
        site = self.__url_build('eventtypes.json')
        r = requests.get(site, auth=(self.__api_key, 'pass'), headers=self.__header)
        events_pack = r.json()
        out_list = list()
        for event in events_pack['eventtypes']:
            out_tup = (event['id'], event['name'], event['color'])
            out_list.append(out_tup)
        return out_list
    def get_calendar_events(self):
        if self.__connection:
            return self.__get_calendar_events()
        else:
            return -1
    def __post_calendar_event_type(self, title, hexcolor):
        eventtype = {'name':title,'color':hexcolor}
        payload = {'eventtype':eventtype}
        site = self.__url_build('eventtypes.json')
        r = requests.post(site, json=payload, auth=self.__auth, headers=self.__header)
        try:
            response = r.json()
        except json.decoder.JSONDecodeError:
            response = False
        try:
            reponse = response['STATUS'] == 'OK'
        except KeyError:
            response = False
        return response
    def __get_project_calendar_events(self, project, **kwargs):
        site = self.__url_build('calendarevents.json')
        payload = {'startdate':kwargs['startdate'], 'endDate':kwargs['enddate'], 'updatedAfterDate':kwargs['updatedafter']}
        r = requests.get(site, params=payload,auth=self.__auth, headers=self.__header)
        rjson = r.json()
        out_list = list()
        for event in rjson['events']:
            if event['privacy']['project-id'] == project:
                out_list.append(event)
        return out_list
    def get_project_calendar_events(self, project, **kwargs):
        if self.__connection:
            return self.__get_project_calendar_events(project, **kwargs)
        else:
            return -1
    def __get_company_clanedar(self, company, **kwargs):
        site = self.__url_build('calendarevents.json')
        payload = {'startdate':self.__epochtodate(kwargs['startdate'], type=1), 'endDate':self.__epochtodate(kwargs['enddate'], type=1)}
        r = requests.get(site, params=payload,auth=self.__auth, headers=self.__header)
        out_list = list()
        rjson = r.json()
        company_dict = dict()
        print(rjson)
        for event in rjson['events']:
            print(event['privacy'])
            if event['privacy']['project-id'] == company:
                out_list.append(event)
        return out_list
    def get_company_calendar(self, company, **kwargs):
        if self.__connection:
            return self.__get_company_clanedar(company, **kwargs)
        else:
            return -1
    def __get_company_id(self, project):
        site = self.__url_build('projects.json')
        r = requests.get(site, auth=self.__auth, headers=self.__header)
        rjson = r.json()
        out_company = ''
        for project in rjson['projects']:
            print(project)
        return -1
    def get_company_id(self, project):
        if self.__connection:
            return self.__get_company_id(project)
        else:
            return -1
    def post_calendar_event_type(self, title, hexcolor):
        if self.__connection:
            return self.__post_calendar_event_type(title, hexcolor)
        else:
            return False
    def __update_calendar_event_type(self, **kwargs):
        site = self.__url_build('eventtypes/{}.json'.format(kwargs['event_id']))
        payload = {
            "eventtype":{
                "name" : kwargs['name'],
                "color": kwargs['color']
        }
        }
        r = requests.put(site, auth=self.__auth, json=payload)
        print(r.json())
        return -1
    def update_calendar_event_type(self, **kwargs):
        if self.__connection:
            return self.__update_calendar_event_type(**kwargs)
        else:
            return -1
    def __add_user(self, **kwargs):
        site = self.__url_build('people.json')
        payload = {
            "person": {
                "first-name": kwargs['first_name'],
                "last-name": kwargs['last_name'],
                "email-address": kwargs['email'],
                "user-type": "account",
                "user-name": kwargs['username'],
                "password": kwargs['password'],
                "company-id": kwargs['company_id'],
                "title": kwargs['title'],
                "phone-number-mobile": "",
                "phone-number-office": "",
                "phone-number-office-ext": "",
                "phone-number-fax": "",
                "phone-number-home": "",
                "im-handle": "",
                "im-service": "",
                "dateFormat": "dd/mm/yyyy",
                "sendWelcomeEmail": "no",
                "welcomeEmailMessage": "",
                "receiveDailyReports": "no",
                "autoGiveProjectAccess": "yes",
                "openID": "",
                "privateNotes": "",
                "userLanguage": "EN",
                "administrator": "yes",
                "canAddProjects": "yes",
                "timezoneId": "15",
                "notifyOnTaskComplete": "no",
                "userReceiveNotifyWarnings": "no",
                "notify-on-added-as-follower": "yes",
                "notify-on-status-update": "yes"
            }
        }
        r = requests.post(site, json=payload, auth=self.__auth)
        print(r.json())
        return -1
    def add_user(self, **kwargs):
        if self.__connection:
            return self.__add_user(**kwargs)
        else:
            return -1
if __name__ == '__main__':
    import os
    api_key = os.environ['teamwork_api']
    connection = Connect(api_key)
    print(connection.get_calendar_events())