from support import version, icalparser, teamworkapi

__author__ = version.get_author()
__version__ = version.get_version()

from random import randint
import sqlite3


'''
Class: icalObject
Description: wraps parsed ical data for easier implementation
'''

class icalObject():
    def __init__(self, listing, cutoff):
        self.__listing = listing
        self.__cutoff = cutoff
    def generate(self):
        self.__parser = icalparser.Connect(self.get_link())
        return -1
    def get_link(self):
        return self.__listing[2]
    def get_id(self):
        return self.__listing[0]
    def get_projectid(self):
        return self.__listing[1]
    def get_eventid(self):
        return self.__listing[3]
    def get_name(self):
        return self.__listing[4]
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
    def get_start(self):
        return self.__entry[1]
    def get_end(self):
        return self.__entry[2]
    def get_amount(self):
        return self.__entry[3]
    def get_guest(self):
        return self.__entry[4]
    def get_service(self):
        return self.__entry[5]
    def get_email(self):
        return self.__entry[6]
    def get_phone(self):
        return self.__entry[7]
    def get_posted(self):
        return self.__entry[8]
    def get_delete(self):
        return self.__entry[9]
    def get_post_id(self):
        return self.__entry[10]
    def get_entry_id(self):
        return self.__entry[11]
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
        return self.__parent[1]
    def get_event_id(self):
        return self.__parent[3]
    def get_event_name(self):
        return self.__parent[4]

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
    def set_company_id_cutoff(self, company_id, cutoff):
        cur_id = self.get_company_id()
        if cur_id == -1:
            self.__c.execute("INSERT INTO config VALUES ('{}', '{}')".format(company_id, cutoff))
            return 1
        else:
            return -1
    def get_listings(self):
        out_list = list()
        for listing in self.__c.execute("SELECT * FROM listings"):
            out_list.append(listing)
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
    def iter_entries_objects(self):
        for entry in self.iter_entries():
            yield entryObject(entry)
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
        self.__c.execute("INSERT INTO entries VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(ical_id, start_date, leave_date, amount, guest, service, email, phone, 0, 0, '', entry_id))
    def append_entry_self(self, entry, posted, listing_id):
        ical_id = entry.get_ical_id()
        start_date = entry.get_start()
        leave_date = entry.get_end()
        amount = entry.get_amount()
        guest = entry.get_guest()
        service = entry.get_service()
        email = entry.get_email()
        phone = entry.get_phone()
        entry_id = entry.get_entry_id()
        self.__c.execute("INSERT INTO entries VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(ical_id, start_date, leave_date, amount, guest, service, email, phone, posted, 0, listing_id, entry_id))

    def set_mark_remove(self, entry, remove_step = 1):
        params = (remove_step, entry.get_entry_id())
        sql = ''' UPDATE entries
                  SET "delete" = ?
                  WHERE "entry id" = ?'''
        self.__c.execute(sql, params)
        return -1

    def remove_entry(self, entry):
        params = entry.get_entry_id()
        print(params)
        self.__c.execute("DELETE FROM entries WHERE \"entry id\" = '{}'".format(params))
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
    def sync_ical(self):
        listings = self.get_listings()
        entries = self.get_entries_parent_objects()
        for listing in listings:
            ical_listing = icalObject(listing, self.get_cutoff())
            ical_events = ical_listing.get_events()
            for ical_event in ical_events:
                for entry in entries:
                    if entry.get_guest() == ical_event.get_guest() and entry.get_start() == ical_event.get_start() and entry.get_end() == ical_event.get_end() and ical_listing.get_id() == entry.get_ical_id():
                        entry.set_remove_log(1)
                if not self.get_entry_present(ical_event, ical_listing):
                    self.append_entry(ical_event, ical_listing)
        for entry in entries:
            if entry.get_remove_log() == -1:
                print('{} NO MATCH FOUND REMOVE.'.format(entry.get_entry_id()))
                self.set_mark_remove(entry)
        self.save()
    def sync_teamwork(self, teamwork):
        pending_entries_add, pending_entries_remove = self.get_pending_entries()
        for entry in pending_entries_add:
            post_id = teamwork.post_calendarevent(entry)
            print(post_id)
            if not post_id:
                continue
            else:
                self.update_entry_id(entry, post_id)
        for entry in pending_entries_remove:
            remove_status = teamwork.remove_calendarevent(entry.get_post_id())
            if remove_status == 1:
                self.remove_entry(entry)
        self.save()
        return -1
    def remove_all_posted(self, teamwork):
        posted_entries = self.get_posted_entries()
        for entry in posted_entries:
            remove_status = teamwork.remove_calendarevent(entry.get_post_id())
            if remove_status == 1:
                print('removed')
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
            self.__c.execute("INSERT INTO listings VALUES ('{}','{}','{}','{}','{}')".format(unique_id,project_id,ical_link,event_id,event_name))
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
def createdb(file_name, company_id=131775, cutoff_date=1495584000):
    conn = sqlite3.connect(file_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE config
        ('company_id' id, 'cutoff_date' date)''')
    c.execute('''CREATE TABLE listings
    ('ical id' id, 'project id' id, 'ical link' text, 'event id' id, 'event name' text)''')
    c.execute('''CREATE TABLE entries
    ('ical id' id, 'arrival date' date, 'leave date' date, 'amount' money, 'guest' name, 'service' int, 'email' name, 'phone' text, 'posted' BIT, 'delete' BYTE, 'post id' id, 'entry id' name)''')
    conn.commit()
    conn.close()
    new_file = MainFile(file_name)
    new_file.set_company_id_cutoff(company_id, cutoff_date)
    new_file.save()
    return new_file
def testdb(file_name):
    test_file = MainFile(file_name)
    return test_file.testdb()
if __name__ == "__main__":
    test_db = "calendar.db"
    db = MainFile(test_db)