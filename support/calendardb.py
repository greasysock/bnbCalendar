from support import version

__author__ = version.get_author()
__version__ = version.get_version()

from random import randint
import sqlite3

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
            self.__c.execute("INSERT INTO config VALUES ('{}, {}')".format(company_id, cutoff))
            return 1
        else:
            return -1
    def iter_listings(self):
        for listing in self.__c.execute("SELECT * FROM listings"):
            yield listing
    def get_listings(self):
        out_list = list()
        for listing in self.iter_listings():
            out_list.append(listing)
        return out_list
    def get_ical_present(self, ical_link, idx=1):
        present = False
        for ical_check in self.iter_listings():
            if ical_check[idx] == ical_link: present = True
        return present
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
    ('ical id' id, 'arrival date' date, 'leave date' date, 'amount' money, 'guest' name, 'service' int, 'email' name, 'phone' text, 'posted' BIT)''')
    conn.commit()
    conn.close()
    new_file = MainFile(file_name)
    new_file.set_company_id_cutoff(company_id, cutoff_date)
    new_file.save()
    return new_file
def testdb(file_name):
    test_file = MainFile(file_name)
    return test_file.testdb()