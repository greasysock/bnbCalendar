import requests, time, datetime
from support import version

__author__ = version.get_author()
__version__ = version.get_version()
__title__ = version.get_title()

ignore_guests = ['Not available', 'Blocked']

def get_ical(link):
    head = {'user-agent' : '{}/{}'.format(__title__, __version__)}
    r = requests.get(link, headers=head, timeout=10)
    return r.content.decode('iso-8859-1')

class Connect():
    def __init__(self, link, test=False):
        self.__link = link
        if not test:
            self.__raw_ical = repr(get_ical(self.__link))
        elif test:
            self.__raw_ical = repr(open('abbtest.ics', 'rb').read().decode('utf-8'))
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
    def get_to_date(self, epoch_time):
        try:
            out_list = list()
            for event in self.__events:
                if event['start'] >= epoch_time:
                    out_list.append(event)
            return out_list
        except AttributeError:
            self.__events = self.get_events()
            return self.get_to_date(epoch_time)
    def get_to_largest_date(self):
        try:
            date_list = list()
            for event in self.__events:
                date_list.append(event['end'])

            return max(date_list)
        except AttributeError:
            self.__events = self.get_events()
            return self.get_to_largest_date()
    def get_events_abb(self):
        out_list = list()
        recover = ('DTSTART;VALUE=DATE', 'DTEND;VALUE=DATE', 'SUMMARY', 'PHONE', 'EMAIL')
        for raw_event in self.__iter_events_raw():
            raw_values = self.__recover_value(raw_event, recover)
            print(raw_values)
            event_dict = dict()
            event_dict['start'] = self.__abb_date_clean(raw_values[0])
            event_dict['end'] = self.__abb_date_clean(raw_values[1])
            event_dict['guest'] = self.__abb_name_clean(raw_values[2])
            if raw_values.__len__() == recover.__len__():
                event_dict['phone'] = raw_values[3]
                event_dict['email'] = raw_values[4]
            if event_dict['guest'] not in ignore_guests:
                out_list.append(event_dict)
        return out_list
    def __recover_value(self, extract_line ,recover_tup, seperator=':', back_seperator=';'):
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
        print(date)
        year = int(date[0:4])
        month = int(date[4:6])
        day = int(date[6:8])
        seconds = date[9:]
        print("{}/{}/{} {}".format(month, day, year, seconds))
        hour = int(int(seconds[:-1]) / 10000)
        dt = datetime.datetime(year, month, day, hour)
        return time.mktime(dt.timetuple())
    def __abb_date_clean(self, date):
        year = int(date[0:4])
        month = int(date[4:6])
        day = int(date[6:8])
        dt = datetime.datetime(year, month, day)
        return time.mktime(dt.timetuple())
    def __vrbo_name_clean(self, name):
        filter_name = name [11:]
        if filter_name != '':
            return filter_name
        else:
            return name
    def __abb_name_clean(self, name):
        if name != 'Not available':
            return name[:-13]
        elif name == 'Not available':
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
            if event_dict['guest'] not in ignore_guests:
                out_list.append(event_dict)
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
    CalendarE = Connect('https://www.airbnb.com/calendar/ical/11651866.ics?s=51fe1a87d1b0a8294164d35086888b5c', test=True)
    events = CalendarE.get_events()
    CalendarE.get_to_date(1495584000)
    print(CalendarE.get_to_largest_date())