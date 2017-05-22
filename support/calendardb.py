from support import version

__author__ = version.get_author()
__version__ = version.get_version()

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
        valid_db = ['config', 'userinfo', 'projects', 'listings', 'entries']
        test_db = list()
        for table_name in self.__c.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            for table in table_name:
                test_db.append(table)

        if valid_db == test_db:
            return 1
        else:
            return -1
    def get_company_id(self):
        try:
            company_id = str()
            for client_data in self.__c.execute('SELECT * FROM config'):
                company_id = client_data[0]
            if company_id == str():
                return -1
            else:
                return company_id
        except sqlite3.OperationalError:
            return -1

    def set_company_id(self, company_id):
        cur_id = self.get_company_id()
        if cur_id == -1:
            self.__c.execute("INSERT INTO config VALUES ('{}')".format(company_id))
            return 1
        else:
            return -1
def createdb(file_name, company_id=131775):
    conn = sqlite3.connect(file_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE config
        ('company_id' id)''')
    c.execute('''CREATE TABLE userinfo
    ('username' name, 'userid' id, 'project id' id)''')
    c.execute('''CREATE TABLE projects
    ('project id' id, 'project' TEXT)''')
    c.execute('''CREATE TABLE listings
    ('project id' id, 'ical link' text, 'event type' id)''')
    c.execute('''CREATE TABLE entries
    ('listing id' id, 'arrival date' date, 'leave date' date, 'amount' money, 'guest' name, 'service' int, 'email' name, 'phone' text, 'posted' BIT)''')
    conn.commit()
    conn.close()
    new_file = MainFile(file_name)
    new_file.set_company_id(company_id)
    new_file.save()
    return new_file
def testdb(file_name):
    test_file = MainFile(file_name)
    return test_file.testdb()