import requests
from icalendar import Calendar, Event
from support import version

__author__ = version.get_author()
__version__ = version.get_version()
__title__ = version.get_title()

def get_ical(link):
    head = {'user-agent' : '{}/{}'.format(__title__, __version__)}
    r = requests.get(link, headers=head)
    return r.content.decode('iso-8859-1')

class Connect():
    def __init__(self, link):
        self.__link = link
        self.__raw_ical = repr(get_ical(self.__link))
#        self.__raw_ical = repr(open('test.ics', 'rb').read().decode('utf-8'))
    def __get_raw__events(self):
            for event in str(self.__raw_ical).split('\\'):
                if event != '' and event != 'n':
                    yield event[1:]
    def __get_end_eventidx(self, startidx):
        event_list = list()
        for entry in self.__get_raw__events():
            event_list.append(entry)
        endidx = None
        for idx, entry in enumerate(event_list[startidx:]):
            if entry == 'END:VEVENT':
                endidx = idx+startidx
                break
        return endidx
    def test_cal(self):
        try:
            if self.get_raw_events_list()[0] == 'BEGIN:VCALENDAR':
                return 1
            else:
                return -1
        except:
            return -1
    def __event_clean(self, event_list):
        clean_event_list = list()
        candidate = list()
        for idx, event in enumerate(event_list):
            if event[:1] == ' ':
                candidate.append(idx-1)
        for idx, event in enumerate(event_list):
            if idx in candidate:
                clean_event_list.append(event+event_list[idx+1][1:])
            elif idx-1 in candidate:
                continue
            else:
                clean_event_list.append(event)
        return clean_event_list
    def get_raw_events_list(self):
        event_list = list()
        for entry in self.__get_raw__events():
            event_list.append(entry)
        return event_list
    def get_events(self):
        event_list = list()
        raw_list = self.get_raw_events_list()
        for idx, entry in enumerate(self.__get_raw__events()):
            if entry == 'BEGIN:VEVENT':
                event_start = idx + 1
                event_end = self.__get_end_eventidx(event_start)
                event_list.append(self.__event_clean(raw_list[event_start:event_end]))
        return event_list
def test_ical(link):
    test_con = Connect(link)
    return test_con.test_cal()
if __name__ == "__main__":
    CalendarE = Connect('http://admin.vrbo.com/icalendar/bd6b684b3f054055a440a5e51df8bac1.ics')
    events = CalendarE.get_events()
    for event in events:
        print('-------------------------------')
        for entry in event:
            print(entry)