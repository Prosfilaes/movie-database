#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys

con = None

try:
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    table_list = ["alternate_movie_names", "dvd", "dvd_contents", "dvd_tags", "has_been_retagged", "movie", "person", "tags"]
    # Leaving out the reproducable imdb_movie_list and the virtual table movies_by_decade
    for table in table_list:
        print ("# {}".format (table));
        cur.execute ("SELECT * FROM {};".format (table))
        rows = cur.fetchall ();
        for row in rows:
            print (row);
        print ()
    
except mdb.Error as e:
  
    print (e)
    sys.exit(1)
    
finally:    
        
    if con:
        con.rollback ()
        con.close()
