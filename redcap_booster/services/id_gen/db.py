import sqlite3
from redcap_booster import config
import random
import sys

class DatabaseAccess:
    """Manage access to database for ID generation service"""
    
    def __init__(self, service):
        db = getattr(config.settings, f'{service}')['db']
        self.con = sqlite3.connect(db)
        self.cur = self.con.cursor()
    
    def create_table(self, pid):
        assert pid.isdecimal()
        self.cur.execute(f'CREATE TABLE IF NOT EXISTS pid_{pid} (\n'
                          '    idx INTEGER PRIMARY KEY,\n'
                          '    id TEXT UNIQUE NOT NULL,\n'
                          '    record TEXT UNIQUE\n'
                          ')')
    
    def import_map(self, pid, map):
        assert pid.isdecimal()
        self.create_table(pid)
        
        self.cur.execute(f'SELECT * from pid_{pid} LIMIT 1')
        if self.cur.fetchone():
            sys.exit(f'Table pid_{pid} is not empty')
        
        self.cur.executemany(f'INSERT INTO pid_{pid} VALUES (NULL,?,?)', map)
        self.con.commit()
    
    def load_ids(self, pid, ids, random_order=False):
        assert pid.isdecimal()
        self.create_table(pid)
        
        self.cur.execute(f'SELECT id from pid_{pid}')
        old_ids = self.cur.fetchall()
        new_ids = [(id,) for id in ids if (id,) not in old_ids]
        if len(new_ids) < len(ids):
            print(f'{len(ids)-len(new_ids)} of {len(ids)} IDs already loaded;',
                  end=' ')
        
        if random_order:
            random.shuffle(new_ids)
        
        self.cur.executemany(f'INSERT INTO pid_{pid} VALUES (NULL,?,NULL)',
                             new_ids)
        self.con.commit()
        print(f'{len(new_ids)} new IDs loaded for project {pid}')
    
    def get_id(self, pid, record):
        assert pid.isdecimal()
        
        self.cur.execute(f'SELECT id FROM pid_{pid} WHERE record=?', (record,))
        id = self.cur.fetchone()
        if id:
            return id[0]
        
        else:
            q = f'SELECT id FROM pid_{pid} WHERE record IS NULL ORDER BY idx LIMIT 1'
            self.cur.execute(q)
            id = self.cur.fetchone()
            if id:
                self.cur.execute(f'UPDATE pid_{pid} SET record=? WHERE id=?',
                                 (record, id[0]))
                self.con.commit()
                return id[0]
    
    def export_map(self, pid):
        assert pid.isdecimal()
        
        map = []
        self.cur.execute(f'SELECT id,record FROM pid_{pid} ORDER BY idx')
        for row in self.cur:
            map.append(row)
        
        return map
