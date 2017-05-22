import requests, json, time
from support import version

__author__ = version.get_author()
__version__ = version.get_version()
__title__ = version.get_title()

api_key = 'twp_E9bQI6vc3LNRIfyNHwhCXxtkZDly'
site = 'https://bnbwithme.teamwork.com'
class Connect():
    def __init__(self, api_key, site=site):
        self.__api_key = api_key
        self.__default_company = None
        self.__site = site
        self.__header = {'user-agent':'{}/{}'.format(__title__,__version__)}
        self.__connection = self.test()
        self.__last_action = 0
    def __url_build(self, url):
        return '{}/{}'.format(self.__site,url)
    def test(self):
        site = self.__url_build('projects.json')
        r = requests.get(site, auth=(self.__api_key, 'pass'), headers=self.__header)
        try:
            rjson = r.json()
        except json.decoder.JSONDecodeError:
            rjson = {'STATUS':'FAIL'}
        working = rjson['STATUS'] == 'OK'
        return working
    def set_company(self, company):
        self.__default_company = company
    def __epochtodate(self, date):
        '''
        YYYYMMDD --> Format
        '''
        return time.strftime('%Y%m%d', time.localtime(date))
    def __get_calendarevents(self, startdate, enddate):
        site = self.__url_build('calendarevents.json')
        fix_startdate = self.__epochtodate(startdate)
        fix_enddate = self.__epochtodate(enddate)
        payload = {'startdate':fix_startdate, 'endDate':fix_enddate}
        r = requests.get(site, params=payload, auth=(self.__api_key, 'pass'), headers=self.__header)
        return r.json()
    def get_calendarevents(self, startdate, enddate):
        if self.__connection:
            return self.__get_calendarevents(startdate, enddate)
        else:
            return -1
    def __post_calendarevent(self):
        return -1
    def post_clendarevent(self):
        if self.__connection:
            return self.__post_calendarevent()
        else:
            return -1
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

if __name__ == '__main__':
    connection = Connect(api_key)
    print(connection.get_calendarevents(1492622538,1495214547))