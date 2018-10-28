from support import version, icalparser

__author__ = version.get_author()
__version__ = version.get_version()

from random import randint
import sqlite3, logging, time
import requests.exceptions, logging


'''
Class: icalObject
Description: wraps parsed ical data for easier implementation
'''


class parentObject():
    def __init__(self, parent):
        self.__parent = parent
    def get_id(self):
        try:
            return self.__parent[0]
        except TypeError:
            return self.__parent
    def get_project_id(self):
        try:
            return self.__parent[1]
        except TypeError:
            return self.__parent
    def get_ical_link(self):
        try:
            return self.__parent[2]
        except TypeError:
            return self.__parent
    def get_event_id(self):
        try:
            return self.__parent[3]
        except TypeError:
            return self.__parent
    def get_event_name(self):
        try:
            return self.__parent[4]
        except TypeError:
            return self.__parent
    def get_last_sync(self):
        try:
            return self.__parent[5]
        except TypeError:
            return self.__parent

class icalObject(parentObject):
    def __init__(self, listing, cutoff):
        parentObject.__init__(self,listing)
        self.__listing = listing
        self.__cutoff = cutoff
    def generate(self):
        self.__parser = icalparser.Connect(self.get_ical_link())
        return -1
    def get_type(self):
        return self.__parser.get_type()
    def get_events(self):
        try:
            events = self.__parser.get_to_date(self.__cutoff)
            out_list = list()
            for event in events:
                out_list.append(entry_icalObject(event))
            return out_list
        except AttributeError:
            self.generate()
            events = self.__parser.get_to_date(self.__cutoff)
            out_list = list()
            for event in events:
                out_list.append(entry_icalObject(event))
            return out_list

'''
Class: entryObject
Description: wraps entry object from database for easier access.
'''

class entryObject():
    def __init__(self, entry):
        self.__entry = entry

    def get_ical_id(self):
        return self.__entry[0]
    @property
    def ical_id(self):
        return self.get_ical_id()

    def get_start(self):
        return self.__entry[1]
    @property
    def start(self):
        return self.get_start()

    def get_end(self):
        return self.__entry[2]
    @property
    def end(self):
        return self.get_end()

    def get_amount(self):
        return self.__entry[3]
    @property
    def amount(self):
        return self.get_amount()

    def get_guest(self):
        return self.__entry[4]
    @property
    def guest(self):
        return self.get_guest()

    def get_service(self):
        return self.__entry[5]
    @property
    def service(self):
        return self.get_service()

    def get_email(self):
        return self.__entry[6]
    @property
    def email(self):
        return self.get_email()

    def get_phone(self):
        return self.__entry[7]
    @property
    def phone(self):
        return self.get_phone()

    def get_posted(self):
        return self.__entry[8]
    @property
    def posted(self):
        return self.get_posted()

    def get_delete(self):
        return self.__entry[9]
    @property
    def delete(self):
        return self.get_delete()

    def get_post_id(self):
        return self.__entry[10]
    @property
    def post_id(self):
        return self.get_post_id()

    def get_entry_id(self):
        return self.__entry[11]
    @property
    def entry_id(self):
        return self.get_entry_id()

    def get_cleaning_entry(self):
        return self.__entry[12]
    @property
    def cleaning_entry(self):
        return self.get_cleaning_entry()

    def set_remove_log(self, operation):
        try:
            self.__remove += operation
        except AttributeError:
            self.__remove = 0
            self.__remove += 1
    def get_remove_log(self):
        try:
            return self.__remove
        except AttributeError:
            return -1

'''
Class: entryparentObject
Description: Adds parent data to entryObject class
'''


class entryparentObject(entryObject):
    def __init__(self, entry, parent):
        entryObject.__init__(self, entry)
        self.__parent = parent
    def get_project_id(self):
        try:
            return self.__parent[1]
        except TypeError:
            return self.__parent
    def get_event_id(self):
        try:
            return self.__parent[3]
        except TypeError:
            return self.__parent
    def get_event_name(self):
        try:
            return self.__parent[4]
        except TypeError:
            return self.__parent
    def get_last_sync(self):
        try:
            return self.__parent[5]
        except TypeError:
            return self.__parent



'''
Class: entry_icalObject
Description: Wraps individual ical entry for easier manipulation.
'''

class entry_icalObject():
    def __init__(self, entry_candidate):
        self.__entry = entry_candidate
    def get_start(self):
        return self.__entry['start']
    def get_end(self):
        return self.__entry['end']
    def get_guest(self):
        return self.__entry['guest']
    def get_phone(self):
        try:
            return self.__entry['phone']
        except KeyError:
            return ''
    def get_email(self):
        try:
            return self.__entry['email']
        except KeyError:
            return ''
    def get_amount(self):
        return 0

class MainFile():
    def __init__(self, db_file):
        self.__db_file = db_file
        self.__conn = sqlite3.connect(db_file)
        self.__c = self.__conn.cursor()

    def save(self):
        self.__conn.commit()

    def close(self):
        self.__conn.close()

    def testdb(self):
        valid_db = ['config', 'listings', 'entries']
        test_db = list()
        for table_name in self.__c.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            for table in table_name:
                test_db.append(table)

        if valid_db == test_db:
            return 1
        else:
            return -1

    def get_from_config(self, idx):
        try:
            config = str()
            for client_data in self.__c.execute('SELECT * FROM config'):
                config = client_data[idx]
            if config == str():
                return -1
            else:
                return config
        except sqlite3.OperationalError:
            return -1

    def get_company_id(self):
        return self.get_from_config(0)

    def get_cutoff(self):
        return self.get_from_config(1)

    def get_cleaning_event(self):
        return self.get_from_config(2)

    def set_company_id_cutoff_cleaning(self, company_id, cutoff, cleaning_event):
        cur_id = self.get_company_id()
        if cur_id == -1:
            self.__c.execute("INSERT INTO config VALUES ('{}', '{}', '{}')".format(company_id, cutoff, cleaning_event))
            return 1
        else:
            return -1

    def get_listings(self):
        out_list = list()
        for listing in self.__c.execute("SELECT * FROM listings"):
            out_list.append(listing)
        return out_list

    def get_listings_objects(self):
        listings = self.get_listings()
        out_list = list()
        for listing in listings:
            out_list.append(parentObject(listing))
        return out_list

    def iter_listings(self):
        for listing in self.__c.execute("SELECT * FROM listings"):
            yield listing

    def iter_entries(self):
        for entry in self.__c.execute("SELECT * FROM entries"):
            yield entry

    def get_listing(self, id, idx=0):
        out_listing = None
        for listing in self.iter_listings():
            if listing[idx] == id:
                out_listing = listing
        if out_listing != None:
            return out_listing
        else:
            return -1

    def get_entries(self):
        out_list = list()
        for entry in self.iter_entries():
            out_list.append(entry)
        return out_list
    def get_entries_listing(self, id):
        entries = self.get_entries()
        out_list = list()
        for entry in entries:
            if id == entry[0]:
                entry_parent = self.get_listing(entry[0])
                out_list.append(entryparentObject(entry, entry_parent))
        return out_list
    def iter_entries_objects(self):
        for entry in self.iter_entries():
            yield entryObject(entry)
    def stay_duration_calc(self, start, end):
        return -1
    def get_entries_parent_objects(self):
        out_list = list()
        entries = self.get_entries()
        for entry in entries:
            entry_parent = self.get_listing(entry[0])
            out_list.append(entryparentObject(entry, entry_parent))
        return out_list

    def get_pending_entries(self):
        out_list_add = list()
        out_list_rem = list()
        entries = self.get_entries_parent_objects()
        for entry in entries:
            if entry.get_delete() == 1:
                out_list_rem.append(entry)
            elif entry.get_posted() == 0:
                out_list_add.append(entry)
        return out_list_add,out_list_rem

    def get_pending_cleaning_entries(self):
        out_list_add = list()
        out_list_rem = list()
        entries = self.get_entries_parent_objects()
        for entry in entries:
            if entry.get_delete() == 1 and entry.get_cleaning_entry() != '':
                out_list_rem.append(entry)
            elif entry.get_delete() == 1 and entry.get_post_id() == -1:
                out_list_rem.append(entry)
            elif entry.get_posted() == 1 and entry.get_cleaning_entry() == '':
                out_list_add.append(entry)
        return out_list_add, out_list_rem

    def get_posted_entries(self):
        out_list = list()
        entries = self.get_entries_parent_objects()
        for entry in entries:
            if entry.get_posted() == 1:
               out_list.append(entry)
        return out_list

    def get_ical_present(self, ical_link, idx=1):
        present = False
        for ical_check in self.iter_listings():
            if ical_check[idx] == ical_link: present = True
        return present

    def get_entry_present(self, entry_test, parent_ical):
        parentId = parent_ical.get_id()
        present = 0
        for entry in self.iter_entries():
            entry_obj = entryObject(entry)
            if entry_obj.get_ical_id() == parentId:
                if entry_test.get_start() == entry_obj.get_start() and entry_test.get_end() == entry_obj.get_end() and entry_test.get_guest() == entry_obj.get_guest():
                    present += 1
        if present == 1:
            return True
        elif present == 0:
            return False

    def append_entry(self, entry, parent_ical, id = None):
        ical_id = parent_ical.get_id()
        start_date = entry.get_start()
        leave_date = entry.get_end()
        amount = entry.get_amount()
        guest = entry.get_guest()
        service = parent_ical.get_type()
        email = entry.get_email()
        phone = entry.get_phone()
        if id == None:
            entry_id = self.get_unique_random_entry()
        else:
            entry_id = id
        print('ICAL_ID = {} S = {} E = {}'.format(ical_id, start_date, leave_date))
        try:
            self.__c.execute("INSERT INTO entries VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(ical_id, start_date, leave_date, amount, guest, service, email, phone, 0, 0, '', entry_id, ''))
        except sqlite3.OperationalError:
            logging.info("Skipping:\n  Name: {}".format(guest))
            print('skipping')
    def set_mark_remove(self, entry, remove_step = 1):
        params = (remove_step, entry.get_entry_id())
        sql = ''' UPDATE entries
                  SET "delete" = ?
                  WHERE "entry id" = ?'''
        self.__c.execute(sql, params)
        return -1

    def remove_entry(self, entry):
        params = entry.get_entry_id()
        self.__c.execute("DELETE FROM entries WHERE \"entry id\" = '{}'".format(params))
        logging.info("Entry '{}' removed from calendar database".format(entry.get_entry_id()))
        self.save()
        return -1

    def remove_listing(self, ical_id):
        self.__c.execute("DELETE FROM listings WHERE \"ical id\" = '{}'".format(ical_id))
        logging.info("Listing id '{}' removed from calendar database".format(ical_id))
        self.save()
        return -1

    def get_pending_teamwork_actions(self):
        pending_additions = 0
        pending_removals = 0
        for entry in self.iter_entries_objects():
            if entry.get_delete() == 1:
                pending_removals += 1
            if entry.get_posted() == 0:
                pending_additions += 1
        return pending_additions, pending_removals

    def update_entry_id(self, entry, id):
        params = (id, entry.get_entry_id())
        sql = ''' UPDATE entries
                  SET posted = 1 ,
                      "post id" = ?
                  WHERE "entry id" = ?'''
        self.__c.execute(sql, params)
        return -1

    def update_entry_cleaning_id(self, entry, id):
        params = (id, entry.get_entry_id())
        sql = ''' UPDATE entries
                          SET "cleaning id" = ?
                          WHERE "entry id" = ?'''
        self.__c.execute(sql, params)
        return -1

    def set_listing_last_sync(self, listingobj):
        params = (time.time(), listingobj.get_id())
        sql = ''' UPDATE listings
                                  SET "last sync" = ?
                                  WHERE "ical id" = ?'''
        self.__c.execute(sql, params)
        self.save()
        return -1

    def sync_icals(self):
        listings = self.get_listings()
        entries = self.get_entries_parent_objects()
        for listing in listings:
            ical_listing = icalObject(listing, self.get_cutoff())
            ical_events = ical_listing.get_events()
            print(ical_events)
            logging.debug('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            logging.debug(listing[2])
            logging.debug(ical_events)
            logging.debug('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            if ical_events != list():
                for ical_event in ical_events:
                    for entry in entries:
                        if entry.get_guest() == ical_event.get_guest() and entry.get_start() == ical_event.get_start() and entry.get_end() == ical_event.get_end() and ical_listing.get_id() == entry.get_ical_id():
                            entry.set_remove_log(1)
                    if not self.get_entry_present(ical_event, ical_listing):
                        self.append_entry(ical_event, ical_listing)
        for entry in entries:
            if entry.get_remove_log() == -1:
                logging.info("No match found in ical for '{}'. Set to remove from teamwork.".format(entry.get_entry_id()))
                self.set_mark_remove(entry)
        self.save()
    def sync_listing_ical(self, listingobj):
        listing = self.get_listing(listingobj.get_id())
        ical_object = icalObject(listing, self.get_cutoff())
        try:
            ical_events = ical_object.get_events()
        except requests.ConnectionError:
            exit()
        entries = self.get_entries_listing(listingobj.get_id())
        logging.info("Listing '{}' Listing ID '{}'".format(ical_object.get_event_name(), ical_object.get_id()))
        out_value = 0
        if ical_events != []:
            for ical_event in ical_events:
                for entry in entries:
                    if entry.get_guest() == ical_event.get_guest()\
                            and entry.get_start() == ical_event.get_start() \
                            and entry.get_end() == ical_event.get_end() \
                            and ical_object.get_id() == entry.get_ical_id():
                        entry.set_remove_log(1)
                if not self.get_entry_present(ical_event, ical_object):
                    self.append_entry(ical_event, ical_object)
                    self.save()
            out_value = 1
            for entry in entries:
                if entry.get_remove_log() == -1:
                    logging.info("No match found in ical for '{}'. Set to remove from teamwork.".format(entry.get_entry_id()))
                    self.set_mark_remove(entry)
                    self.set_mark_remove(entry)
        self.set_listing_last_sync(listingobj)
        return out_value == 1
    def sync_teamwork(self, teamwork):
        pending_entries_add, pending_entries_remove = self.get_pending_entries()
        for entry in pending_entries_add:
            post_id = teamwork.post_calendarevent(entry)
            print(post_id)
            if not post_id:
                logging.warning("'{}' - Failed to upload to teamwork.".format(entry.get_entry_id()))
                continue
            else:
                logging.info("'{}' - Upload to teamwork with the posting id '{}'".format(entry.get_entry_id(), post_id))
                self.update_entry_id(entry, post_id)
        pending_entries_cleaning_add, pending_entries_cleaning_remove = self.get_pending_cleaning_entries()
        for entry in pending_entries_cleaning_add:
            start = entry.get_end()
            end = entry.get_end()
            title = '{} - Cleaning'.format(entry.get_event_name())
            description = ''
            where = entry.get_event_name()
            project_id = entry.get_project_id()
            event_id = self.get_cleaning_event()
            post_id = teamwork.post_calendarevent_cleaning(start=start,end=end,title=title,description=description,
                                                           where=where,project_id=project_id, event_id=event_id)
            if not post_id:
                logging.warning("'{}' - Cleaning event failed to upload to teamwork.".format(entry.get_entry_id()))
            else:
                self.update_entry_cleaning_id(entry, post_id)
                self.save()
        for entry in pending_entries_cleaning_remove:
            if entry.get_cleaning_entry() != -1:
                remove_status = teamwork.remove_calendarevent(entry.get_cleaning_entry())
                if remove_status == 1:
                    self.update_entry_cleaning_id(entry, -1)
                elif remove_status == -1:
                    logging.warning("'{}' - Cleaning event failed to remove from teamwork".format(self.get_cleaning_event()))
        for entry in pending_entries_remove:
            if entry.get_post_id() != -1:
                remove_status = teamwork.remove_calendarevent(entry.get_post_id())
                if remove_status == 1:
                    self.update_entry_id(entry,-1)
            elif entry.get_post_id() == -1:
                remove_status = 1
            if remove_status == 1 and entry.get_cleaning_entry() == -1:
                self.remove_entry(entry)
        self.save()
        return -1

    def remove_all_posted(self, teamwork):
        posted_entries = self.get_posted_entries()
        for entry in posted_entries:
            if entry.get_cleaning_entry() != '' and entry.get_cleaning_entry() != -1:
                cleaning_remove_status = teamwork.remove_calendarevent(entry.get_cleaning_entry())
            else:
                cleaning_remove_status = 1
            if cleaning_remove_status == 1:
                self.update_entry_cleaning_id(entry, -1)
                remove_status = teamwork.remove_calendarevent(entry.get_post_id())
            else:
                remove_status = -1
            if remove_status == 1:
                self.remove_entry(entry)
        return -1

    def get_unique_random(self):
        numgen = randgen()
        match = True
        listings = self.get_listings()
        id = numgen.generate()
        while match:
            id = numgen.generate()
            count_match = 0
            for listing in listings:
                if id == listing[0]:
                    count_match += 1
            if count_match == 0:
                match = False
        return id

    def get_unique_random_entry(self):
        numgen = randgen()
        match = True
        entries = self.get_entries()
        id = numgen.threegen()
        while match:
            id = numgen.threegen()
            count_match = 0
            for entry in entries:
                if id == entry[11]:
                    count_match += 1
            if count_match == 0:
                match = False
        return id

    def append_ical(self, ical_link, project_id, event_id, event_name):
        if not self.get_ical_present(ical_link):
            unique_id = self.get_unique_random()
            self.__c.execute("INSERT INTO listings VALUES ('{}','{}','{}','{}','{}', '{}')".format(unique_id,project_id,ical_link,event_id,event_name,0))
            return 1
        else:
            return -1

class randgen():
    def __init__(self):
        self.__alph = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',1,2,3,4,5,6,7,8,9]
        self.__alphlen = self.__alph.__len__() - 1
    def generate(self):
        int1 = randint(0, self.__alphlen)
        int2 = randint(0, self.__alphlen)
        return '{}{}'.format(self.__alph[int1], self.__alph[int2])
    def threegen(self):
        int1 = randint(0, self.__alphlen)
        int2 = randint(0, self.__alphlen)
        int3 = randint(0, self.__alphlen)
        return '{}{}{}'.format(self.__alph[int1], self.__alph[int2], self.__alph[int3])

def createdb(file_name, company_id=98287, start_week=2, cleaning_event=106880):
    time_offset = start_week * 24 * 60 * 60 * 7
    cutoff_date = int(time.time()) - time_offset
    conn = sqlite3.connect(file_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE config
        ('company_id' id, 'cutoff_date' date, 'cleaning event type' id )''')
    c.execute('''CREATE TABLE listings
    ('ical id' id, 'project id' id, 'ical link' text, 'event id' id, 'event name' text, 'last sync' date)''')
    c.execute('''CREATE TABLE entries
    ('ical id' id, 'arrival date' date, 'leave date' date, 'amount' money, 'guest' name, 'service' int, 'email' name, 'phone' text, 'posted' BIT, 'delete' BYTE, 'post id' id, 'entry id' id, 'cleaning id' id)''')
    conn.commit()
    conn.close()
    new_file = MainFile(file_name)
    new_file.set_company_id_cutoff_cleaning(company_id, cutoff_date, cleaning_event)
    new_file.save()
    return new_file

def testdb(file_name):
    test_file = MainFile(file_name)
    return test_file.testdb()

if __name__ == "__main__":
    test_db = "calendar.db"
    db = MainFile(test_db)