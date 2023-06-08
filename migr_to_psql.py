import os, time

from cmbot_songs import SongList
import psycopg2

F_PATH = 'songlist.json'

slist = SongList(F_PATH)

# print(slist.json_ready())

# Connect to an existing database
conn = psycopg2.connect(
    dbname='chormeister_0',
    user='developer',
    password='89568956',
    host='localhost'

)

# Open a cursor to perform database operations
cur = conn.cursor()


# cur.execute("")
# Execute a command: this creates a new table

def create_song():
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS song
        (id serial PRIMARY KEY,
        status varchar,
        name varchar,
        lyricist varchar,
        composer varchar,
        translator varchar,
        theme varchar,
        performers varchar,
        melodicality varchar);
        """
    )


def migrate_songs():
    i = 0
    for key, value in slist.json_ready().items():
        out_keys = list()
        out_value = list()
        for entry in value.values():
            if entry == '':
                out_value.append('NULL')
            else:
                out_value.append("'" + str(entry) + "'")
        for entry in value.keys():
            if entry == '':
                out_keys.append('NULL')
            else:
                out_keys.append(str(entry))
        print(i, end='\r')
        cur.execute('INSERT INTO song (' + ','.join(out_keys) + ') VALUES (' + ','.join(out_value) + ');')
        i += 1
        time.sleep(0.01)
    conn.commit()


# create_song()
# migrate_songs()

cur.execute('SELECT * FROM song;')
out = cur.fetchall()

cur.close()
conn.close()

for i in out:
    print(i)
