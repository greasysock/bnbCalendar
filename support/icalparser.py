import requests, time, datetime
from support import version

__author__ = version.get_author()
__version__ = version.get_version()
__title__ = version.get_title()

def get_ical(link):
    head = {'user-agent' : '{}/{}'.format(__title__, __version__)}
    r = requests.get(link, headers=head, timeout=10)
    return r.content.decode('iso-8859-1')

class Connect():
    def __init__(self, link):
        self.__link = link
#        self.__raw_ical = repr(get_ical(self.__link))
        self.__raw_ical = repr(open('test.ics', 'rb').read().decode('utf-8'))
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
    def get_type(self):
        if 'admin.vrbo.com' in self.__link:
            return 1
        elif 'airbnb.com' in self.__link:
            return 0
        else:
            return -1
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
    def get_events_abb(self):
        return -1
    def __recover_value(self, extract_line ,recover_tup, seperator=':'):
        out_dict = dict()
        out_tup = list()
        for entry in extract_line:
            entry_split = entry.split(seperator)
            for idx, match in enumerate(recover_tup):
                if entry_split[0] == match:
                    out_tup.insert(idx,entry_split[1])
                    out_dict[match] = entry_split[1]

        return tuple(out_tup)
    def __date_clean(self, date):
        year = int(date[0:4])
        month = int(date[4:6])
        day = int(date[6:8])
        seconds = date[9:]
        hour = int(int(seconds[:-1]) / 10000)
        dt = datetime.datetime(year, month, day, hour)
        return time.mktime(dt.timetuple())
    def __vrbo_name_clean(self, name):
        filter_name = name [11:]
        if filter_name != '':
            return filter_name
        else:
            return name
    def get_events_vrbo(self):
        out_list = list()
        recover = ('DTSTART', 'DTEND', 'SUMMARY')
        for raw_event in self.__iter_events_raw():
            event_dict = dict()
            raw_values = self.__recover_value(raw_event, recover)
            event_dict['start'] = self.__date_clean(raw_values[0])
            event_dict['end'] = self.__date_clean(raw_values[1])
            event_dict['guest'] = self.__vrbo_name_clean(raw_values[2])
            out_list.append(event_dict)
            print(event_dict)
        return out_list
    def __iter_events_raw(self):
        raw_list = self.get_raw_events_list()
        for idx, entry in enumerate(self.__get_raw__events()):
            if entry == 'BEGIN:VEVENT':
                event_start = idx + 1
                event_end = self.__get_end_eventidx(event_start)
                yield self.__event_clean(raw_list[event_start:event_end])
    def get_events(self):
        if self.get_type() == 0:
            return self.get_events_abb()
        elif self.get_type() == 1:
            return self.get_events_vrbo()
def test_ical(link):
    try:
        test_con = Connect(link)
        return test_con.test_cal()
    except:
        return -1
if __name__ == "__main__":
    CalendarE = Connect('http://admin.vrbo.com/icalendar/bd6b684b3f054055a440a5e51df8bac1.ics')
    events = CalendarE.get_events()