from plexapi.server import PlexServer
import mysql.connector

#Python file containing authorisation details for accessing the server, and the SQL database. Find these in the script, and replace for your purposes
import plex_auth

#Create a plex server object to pull data
baseurl = plex_auth.baseurl
token = plex_auth.token
plex = PlexServer(baseurl,token)

#List of all libraires, as they appear in the server
library_list = ['Anime Films','Films','TV','Streaming','Anime','Carry On','Animation','Pratchett',
                'Batman','Disney','Docu-films','Dreamworks','Buster Keaton','Docu-series','James Bond',
                'Kaiju','Ghibli','Looney Tunes (Golden Collection)','Marvel','Pixar','Star Wars',
                'Top Gear Specials','Alfabusa','Anime OVAs','Clone Wars (2003)','Clone Wars (2008+)',
                'MiniSeries','Music Videos','Video Downloads']

#Define functions to allow connections and execute queries
def create_db_connection():
    connection = None
    connection = mysql.connector.connect(
            host=plex_auth.host,
            user=plex_auth.user,
            passwd=plex_auth.passwd,
            database=plex_auth.database
        )

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()


#Collect all data, edit library titles for use in SQL, then upload to tables
counter = 0
for i in library_list:
    try:
        list = []
        year = []
        num = 0
        id = []
        movies = plex.library.section(f'{i}')
        for video in movies.search():
            num += 1
            id.append(num)
            list.append(video.title)
            year.append(video.year)

        i = i.replace('-','_')
        i = i.replace(' ', '_')
        i = i.replace('(', '')
        i = i.replace(')', '')
        i = i.replace('+', '')


        conn = create_db_connection()
        cur = conn.cursor()
        drop_table = f"""DROP TABLE IF EXISTS {i};"""
        create_table = f"""CREATE TABLE {i} (id INT PRIMARY KEY, {i} VARCHAR(255), year INT);"""
        push_data = f"""INSERT INTO {i} (id,{i},year) VALUES (%s,%s,%s)"""
        record = (id,list,year)
        execute_query(conn, drop_table)
        execute_query(conn, create_table)
        for j in range(0,len(list)):
            cur.execute(f"""INSERT INTO {i} (id,{i},year) VALUES (%s,%s,%s)""",(id[j],list[j],year[j]))
        conn.commit()
        cur.close()
        conn.close()
        counter += 1
    except Exception:
        print(f'{i} has had a problem!')

#Small feature to alert me if any problems occur
if counter == 29:
    print('All tables successfully updated!')
else:
    print(f'{29-counter} table(s) not updated')






