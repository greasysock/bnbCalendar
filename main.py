#!/usr/bin/python3
import sys, argparse, os, sqlite3
from support import calendardb, version, icalparser, teamworkapi, prompts

__title__ = version.get_title()
__author__ = version.get_author()
__version__ = version.get_version()

default_calendar = 'calendar.db'
try:
    teamwork_api = os.environ['teamwork_api']
except KeyError:
    print('ERROR: \'teamwork_api\' env variable is missing.')
    sys.exit(2)
def import_wizard(ical, teamwork_api):
    print('WARNING: New project feature not added.')
    print('WARNING: New event feature not added.')
    ical_parse = icalparser.Connect(ical)
    cal_db = calendardb.MainFile(default_calendar)
    teamwork_api.set_company(cal_db.get_company_id())
    projects = teamwork_api.get_projects()
    selected_project = prompts.project_selection(teamwork_api.get_projects())
    if selected_project + 1 > projects.__len__():
        print('new project wizard, new selected_project setting')
        sys.exit(2)
    events = teamwork_api.get_calendar_events()
    selected_event = prompts.event_selection(events)
    if selected_event + 1 > events.__len__():
        print('new event wizard, new selected_event setting')
        sys.exit(2)
    import_status = cal_db.append_ical(ical, projects[selected_project][0],events[selected_event][0], events[selected_event][1])
    if import_status == 1:
        print('Import Success!')
        cal_db.save()
    elif import_status == -1:
        print('Import Failure!')
    sys.exit(2)
def main():
    parser = argparse.ArgumentParser(prog=__title__)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__))
    parser.add_argument('-s', '--setup', help='Initializes db for daemon.', action='store_true', required=False )
    parser.add_argument('-n', '--new', help='Add new .ical to sync with teamwork.', metavar='\'.ics url\'')
    parser.add_argument('-r', '--run', help='Syncs calendar from airbnb and vrbo with teamwork.', action='store_true', required=False)
    args = parser.parse_args()
    if args.setup:
        db_present = calendardb.testdb(default_calendar)
        if db_present == 1:
            print('CalendarDB is already present. Delete current DB to create a new one.')
        elif db_present == -1:
            calendardb.createdb(default_calendar)
            print('CalendarDB Created. Type \'{} -n url\' to add a new calendar to sync.'.format(__title__))
        sys.exit(2)
    elif args.new:
        db_present = calendardb.testdb(default_calendar)
        calendar = calendardb.MainFile(default_calendar)
        try:
            if not calendar.get_ical_present(args.new):
                ics_test = icalparser.test_ical(args.new)
            elif calendar.get_ical_present(args.new):
                ics_test = -2
        except sqlite3.OperationalError:
            ics_test = -1
        test_tw_api = teamworkapi.Connect(teamwork_api)
        if db_present == 1 and ics_test == 1 and test_tw_api.test():
            import_wizard(args.new, test_tw_api)
        if db_present == -1:
            print('ERROR: Database not present or invalid.')
        if ics_test == -1:
            print('ERROR: Invalid .ics link provided.')
        elif ics_test == -2:
            print('ERROR: .ics provided already exists in database.')
        if not test_tw_api.test():
            print('ERROR: Invalid api key or connection error.')
        sys.exit(2)
if __name__ == "__main__":
    main()