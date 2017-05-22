import sys, argparse
from support import calendardb, version, icalparser

__title__ = version.get_title()
__author__ = version.get_author()
__version__ = version.get_version()

default_calendar = 'calendar.db'

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
        ics_test = icalparser.test_ical(args.new)
        if db_present == 1 and ics_test == 1:
            print('running add wizard')
        if db_present == -1:
            print('ERROR: Database not present or invalid.')
        if ics_test == -1:
            print('ERROR: Invalid .ics link provided.')
        sys.exit(2)
if __name__ == "__main__":
    main()