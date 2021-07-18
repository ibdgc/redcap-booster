"""Database for ID generation service"""

import sqlite3
from redcap_booster import config
import random

con = sqlite3.connect(config.settings.id_gen['db'])
cur = con.cursor()

def create_table(pid):
    assert pid.isdecimal()
    cur.execute(f'CREATE TABLE IF NOT EXISTS pid_{pid} (\n'
                 '    idx INTEGER PRIMARY KEY,\n'
                 '    id TEXT UNIQUE NOT NULL,\n'
                 '    record TEXT UNIQUE\n'
                 ')')

def load_ids(pid, ids, random_order=False):
    assert pid.isdecimal()
    create_table(pid)
    
    cur.execute(f'SELECT id from pid_{pid}')
    old_ids = cur.fetchall()
    new_ids = [(id,) for id in ids if (id,) not in old_ids]
    if len(new_ids) < len(ids):
        print(f'{len(ids)-len(new_ids)} of {len(ids)} IDs already loaded;', end=' ')
    
    if random_order:
        random.shuffle(new_ids)
    
    cur.executemany(f'INSERT INTO pid_{pid} VALUES (NULL, ?, NULL)', new_ids)
    con.commit()
    print(f'{len(new_ids)} new IDs loaded for project {pid}')

def get_id(pid, record):
    assert pid.isdecimal()
    
    cur.execute(f'SELECT id FROM pid_{pid} WHERE record=?', (record,))
    id = cur.fetchone()
    if id:
        return id[0]
    
    else:
        cur.execute(f'SELECT id FROM pid_{pid} WHERE record IS NULL ORDER BY idx LIMIT 1')
        id = cur.fetchone()
        if id:
            cur.execute(f'UPDATE pid_{pid} SET record=? WHERE id=?',
                        (record, id[0]))
            con.commit()
            return id[0]

def get_map(pid):
    assert pid.isdecimal()
    
    map = []
    cur.execute(f'SELECT id,record FROM pid_{pid} ORDER BY idx')
    for row in cur:
        map.append(row)
    
    return map
