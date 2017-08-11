#!/usr/bin/python3
import sys, argparse, os, sqlite3, logging, csv, time
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


def touch(file):
    with open(file, 'a'):
        os.utime(file, None)
def remove(file):
    os.remove(file)
def exists(file):
    return os.path.isfile(file)

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
        remove(lock_file)
        sys.exit(2)
    events = teamwork_api.get_calendar_events()
    selected_event = prompts.event_selection(events)
    if selected_event + 1 > events.__len__():
        print('new event wizard, new selected_event setting')
        remove(lock_file)
        sys.exit(2)
    import_status = cal_db.append_ical(ical, projects[selected_project][0],events[selected_event][0], events[selected_event][1])
    if import_status == 1:
        print('Import Success!')
        cal_db.save()
    elif import_status == -1:
        print('Import Failure!')
    remove(lock_file)
    sys.exit(2)

def get_sync_key(listing):
    return listing.get_last_sync()

def sync_ical(db, maxjob=3, wait_time=300):
    listings = db.get_listings_objects()

    sorted_listings = sorted(listings,key=get_sync_key)
    synced_items = 0
    for idx, listing in enumerate(sorted_listings):
        last_sync = time.time() - listing.get_last_sync()

        if last_sync >= wait_time and synced_items < maxjob:
            result = db.sync_listing_ical(listing)
            if result:
                synced_items += 1
                print(listing.get_event_name())
    return db

def main():
    parser = argparse.ArgumentParser(prog=__title__)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__))
    parser.add_argument('-s', '--setup', help='Initializes db for daemon.', action='store_true', required=False )
    parser.add_argument('-n', '--new', help='Add new .ical to sync with teamwork.', metavar='\'.ics url\'')
    parser.add_argument('-r', '--run', help='Syncs calendar from airbnb and vrbo with teamwork.', action='store_true', required=False)
    parser.add_argument('-R', '--remove', help='Remove company calendar from teamwork', metavar='\'Company ID\'')
    parser.add_argument('-c', '--clear', help='Removes all entries from teamwork and database.', action='store_true', required=False)
    parser.add_argument('-b', '--backup', help='Backup listings to .csv file.', action='store_true', required=False)
    parser.add_argument('-e', '--event', nargs='+', help='Add new event to teamviewer.', metavar='name color')



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
        if args.new != backup_file:
            touch(lock_file)
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
            remove(lock_file)
            sys.exit(2)
        elif args.new == backup_file:
            print('Installing backup files')
            db = calendardb.MainFile(default_calendar)
            with open(backup_file, 'r') as csvfile:
                backupreader = csv.reader(csvfile, delimiter = ' ',
                                          quotechar='|')
                for listing in backupreader:
                    db.append_ical(listing[1],listing[0],listing[2],listing[3])
            db.save()

            sys.exit(2)
    elif args.remove:
        connection = teamworkapi.Connect(teamwork_api)
        connection.get_company_calendar(args.remove, startdate=1495584000, enddate=int(time.time()))
        return -1
    elif args.run:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename="run.log", level=logging.DEBUG)
        urllib3_logger = logging.getLogger('urllib3')
        urllib3_logger.setLevel(logging.WARNING)
        logging.info('Logging Started')
        if not exists(lock_file):
            db = calendardb.MainFile(default_calendar)
            db = sync_ical(db)
            pending_additions, pending_removal = db.get_pending_teamwork_actions()
            if pending_additions > 0 or pending_removal > 0:
                logging.info("{} pending additions to teamwork.".format(pending_additions))
                logging.info("{} pending removals to teamwork.".format(pending_removal))
                print("There are '{}' pending additions to teamwork and '{}' pending removals to teamwork. Syncing now.".format(pending_additions, pending_removal))
                teamwork = teamworkapi.Connect(teamwork_api)
                teamwork.set_company(db.get_company_id())
                db.sync_teamwork(teamwork)
            else:
                logging.info("Nothing to append to teamwork.")
            db.close()
        elif exists(lock_file):
            logging.warning('Lock file \'{}\' exists. Will not sync with teamwork until removed.'.format(lock_file))

    elif args.clear:
        db = calendardb.MainFile(default_calendar)
        teamwork = teamworkapi.Connect(teamwork_api)
        db.remove_all_posted(teamwork)
        db.save()
        db.close()
    elif args.event:
        teamwork = teamworkapi.Connect(teamwork_api)
        print(args.event)
        if args.event.__len__() == 2:
            response = teamwork.post_calendar_event_type(args.event[0],args.event[1])
            if response:
                print('event created')
            else:
                print('fail')
    elif args.backup:
        db = calendardb.MainFile(default_calendar)
        listings = db.get_listings()
        with open(backup_file, 'w') as csvfile:
            backupwriter = csv.writer(csvfile, delimiter = ' ',
                                      quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for listing in listings:
                backupwriter.writerow([listing[1],listing[2],listing[3],listing[4]])
if __name__ == "__main__":
    lock_file = 'lock'
    backup_file = 'backup.csv'
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    main()